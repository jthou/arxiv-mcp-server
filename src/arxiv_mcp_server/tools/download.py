"""Download functionality for the arXiv MCP server."""

import arxiv
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import mcp.types as types
from ..config import get_settings
import pymupdf4llm
import logging
import re

logger = logging.getLogger("arxiv-mcp-server")
settings = get_settings()

# Global dictionary to track conversion status
conversion_statuses: Dict[str, Any] = {}


@dataclass
class ConversionStatus:
    """Track the status of a PDF to Markdown conversion."""

    paper_id: str
    status: str  # 'downloading', 'converting', 'success', 'error'
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    paper_title: Optional[str] = None  # 添加论文标题字段


def sanitize_filename(title: str) -> str:
    """将论文标题转换为安全的文件名，空格用下划线替换"""
    # 移除或替换不安全的字符
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', title)
    # 将空格替换为下划线
    sanitized = sanitized.replace(' ', '_')
    # 限制文件名长度
    return sanitized[:100]  # 限制为100个字符


def get_paper_path(
    paper_id: str, 
    paper_title: Optional[str] = None, 
    suffix: str = ".md"
) -> Path:
    """Get the absolute file path for a paper with given suffix."""
    storage_path = Path(settings.STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # 如果提供了论文标题，则使用标题作为文件名，否则使用论文ID
    if paper_title:
        filename = sanitize_filename(paper_title)
        return storage_path / f"{filename}{suffix}"
    else:
        return storage_path / f"{paper_id}{suffix}"


def convert_pdf_to_markdown(
    paper_id: str, 
    paper_title: Optional[str], 
    pdf_path: Path
) -> None:
    """Convert PDF to Markdown in a separate thread."""
    try:
        logger.info(f"Starting conversion for {paper_id}")
        markdown = pymupdf4llm.to_markdown(pdf_path, show_progress=False)
        
        # 使用论文标题作为文件名（如果可用）
        md_path = get_paper_path(paper_id, paper_title, ".md")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        status = conversion_statuses.get(paper_id)
        if status:
            status.status = "success"
            status.completed_at = datetime.now()

        # Clean up PDF after successful conversion
        pdf_path.unlink()
        logger.info(f"Conversion completed for {paper_id}")

    except Exception as e:
        logger.error(f"Conversion failed for {paper_id}: {str(e)}")
        status = conversion_statuses.get(paper_id)
        if status:
            status.status = "error"
            status.completed_at = datetime.now()
            status.error = str(e)
        # 清理PDF文件
        if pdf_path.exists():
            pdf_path.unlink()


download_tool = types.Tool(
    name="download_paper",
    description="Download a paper and create a resource for it",
    inputSchema={
        "type": "object",
        "properties": {
            "paper_id": {
                "type": "string",
                "description": "The arXiv ID of the paper to download",
            },
            "check_status": {
                "type": "boolean",
                "description": (
                    "If true, only check conversion status "
                    "without downloading"
                ),
                "default": False,
            },
        },
        "required": ["paper_id"],
    },
)


async def handle_download(
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle paper download and conversion requests."""
    paper_id = arguments["paper_id"]
    check_status = arguments.get("check_status", False)
    
    try:
        # If only checking status
        if check_status:
            status = conversion_statuses.get(paper_id)
            if not status:
                # 尝试使用论文ID查找文件
                md_path = get_paper_path(paper_id, None, ".md")
                if md_path.exists():
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "success",
                                    "message": "Paper is ready",
                                    "resource_uri": f"file://{md_path}",
                                }
                            ),
                        )
                    ]
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "status": "unknown",
                                "message": (
                                    "No download or conversion "
                                    "in progress"
                                ),
                            }
                        ),
                    )
                ]

            # 使用存储的论文标题获取文件路径
            md_path = get_paper_path(paper_id, status.paper_title, ".md")
            resource_uri = (
                f"file://{md_path}" if status.status == "success" else None
            )
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": status.status,
                            "started_at": status.started_at.isoformat(),
                            "completed_at": (
                                status.completed_at.isoformat()
                                if status.completed_at
                                else None
                            ),
                            "error": status.error,
                            "message": f"Paper conversion {status.status}",
                            "resource_uri": resource_uri,
                        }
                    ),
                )
            ]

        # Check if paper is already converted (使用论文ID检查)
        md_path = get_paper_path(paper_id, None, ".md")
        if md_path.exists():
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "success",
                            "message": "Paper already available",
                            "resource_uri": f"file://{md_path}",
                        }
                    ),
                )
            ]

        # Check if already in progress
        if paper_id in conversion_statuses:
            status = conversion_statuses[paper_id]
            # 使用存储的论文标题获取文件路径
            md_path = get_paper_path(paper_id, status.paper_title, ".md")
            resource_uri = (
                f"file://{md_path}" if status.status == "success" else None
            )
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": status.status,
                            "message": f"Paper conversion {status.status}",
                            "started_at": status.started_at.isoformat(),
                            "resource_uri": resource_uri,
                        }
                    ),
                )
            ]

        # Start new download and conversion
        pdf_path = get_paper_path(paper_id, None, ".pdf")
        client = arxiv.Client()

        # Download PDF first (在初始化状态之前执行可能抛出异常的代码)
        paper = next(client.results(arxiv.Search(id_list=[paper_id])))
        
        # 获取论文标题并清理文件名
        paper_title = paper.title if paper.title else None
        
        # Initialize status only after successful paper retrieval
        conversion_statuses[paper_id] = ConversionStatus(
            paper_id=paper_id, 
            status="downloading", 
            started_at=datetime.now(),
            paper_title=paper_title  # 存储论文标题
        )

        # 使用论文标题生成PDF路径
        if paper_title:
            pdf_path = get_paper_path(paper_id, paper_title, ".pdf")
        paper.download_pdf(dirpath=pdf_path.parent, filename=pdf_path.name)

        # Update status and start conversion
        status = conversion_statuses[paper_id]
        status.status = "converting"

        # Start conversion in thread
        convert_task = asyncio.to_thread(
            convert_pdf_to_markdown, 
            paper_id, 
            paper_title, 
            pdf_path
        )
        asyncio.create_task(convert_task)

        # 使用论文标题生成MD路径
        md_path = get_paper_path(paper_id, paper_title, ".md")
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "converting",
                        "message": "Paper downloaded, conversion started",
                        "started_at": status.started_at.isoformat(),
                        "resource_uri": f"file://{md_path}",
                    }
                ),
            )
        ]

    except StopIteration:
        # 清理可能已创建的状态和文件
        if paper_id in conversion_statuses:
            del conversion_statuses[paper_id]
        # 清理可能已创建的PDF文件
        pdf_path = get_paper_path(paper_id, None, ".pdf")
        if pdf_path.exists():
            pdf_path.unlink()
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "error",
                        "message": f"Paper {paper_id} not found on arXiv",
                    }
                ),
            )
        ]
    except Exception as e:
        # 清理可能已创建的状态和文件
        if paper_id in conversion_statuses:
            del conversion_statuses[paper_id]
        # 清理可能已创建的PDF文件
        pdf_path = get_paper_path(paper_id, None, ".pdf")
        if pdf_path.exists():
            pdf_path.unlink()
        error_msg = {"status": "error", "message": f"Error: {str(e)}"}
        return [
            types.TextContent(
                type="text",
                text=json.dumps(error_msg),
            )
        ]