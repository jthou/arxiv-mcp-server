"""Arxiv MCP Server (stdio only)
============================

This module implements an MCP stdio server for interacting with arXiv.
"""

import logging
import sys
import mcp.types as types
from typing import Dict, Any, List
from mcp.server.stdio import stdio_server
from mcp import ServerSession
from mcp.types import JSONRPCRequest, JSONRPCNotification, JSONRPCResponse, JSONRPCError, JSONRPCMessage
from .config import Settings
from .tools import handle_search, handle_download, handle_list_papers, handle_read_paper, handle_list_tools
from .tools import search_tool, download_tool, list_tool, read_tool, list_tools_tool
from .prompts.handlers import list_prompts as handler_list_prompts
from .prompts.handlers import get_prompt as handler_get_prompt

# 配置日志，将日志输出到文件而不是stdout/stderr
settings = Settings()
logger = logging.getLogger("arxiv-mcp-server")

# 创建文件处理器，避免日志干扰stdio通信
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('arxiv_mcp_server.log')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)  # 设置为DEBUG级别以捕获更多日志

# 确保日志不会输出到stdout/stderr
logger.propagate = False

async def list_prompts() -> List[types.Prompt]:
    """List available prompts."""
    return await handler_list_prompts()

async def get_prompt(
    name: str, arguments: Dict[str, str] | None = None
) -> types.GetPromptResult:
    """Get a specific prompt with arguments."""
    return await handler_get_prompt(name, arguments)

async def list_tools() -> List[types.Tool]:
    """List available arXiv research tools."""
    return [search_tool, download_tool, list_tool, read_tool, list_tools_tool]

async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls for arXiv research functionality."""
    logger.debug(f"Calling tool {name} with arguments {arguments}")
    try:
        if name == "search_papers":
            return await handle_search(arguments)
        elif name == "download_paper":
            return await handle_download(arguments)
        elif name == "list_papers":
            return await handle_list_papers(arguments)
        elif name == "read_paper":
            return await handle_read_paper(arguments)
        elif name == "list_tools":
            return await handle_list_tools(arguments)
        elif name == "list_prompts":
            prompts = await list_prompts()
            return [types.TextContent(
                type="text",
                text=f"Available prompts: {', '.join([p.name for p in prompts])}"
            )]
        elif name == "get_prompt":
            if "name" not in arguments:
                return [types.TextContent(type="text", text="Error: Missing 'name' argument for get_prompt")]
            prompt_result = await get_prompt(arguments["name"], arguments.get("arguments"))
            # 将PromptResult转换为TextContent
            return [types.TextContent(
                type="text",
                text=prompt_result.messages[0].content.text if prompt_result.messages and prompt_result.messages[0].content else "No content"
            )]
        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]
    except Exception as e:
        logger.error(f"Tool error: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

def print_help():
    """Print help information for the server."""
    help_text = """
Arxiv MCP Server - Model Context Protocol server for arXiv papers

Usage:
  python -m arxiv_mcp_server [options]

Options:
  --storage-path PATH    Specify the path to store downloaded papers
  --help, -h            Show this help message and exit

Environment Variables:
  ARXIV_STORAGE_PATH    Alternative way to specify storage path

Note:
  This server communicates via stdio and is designed to be used with MCP-compatible clients.
  It does not provide a web interface or CLI interface for direct user interaction.
"""
    print(help_text)

async def main():
    """Run the stdio server with proper shutdown handling."""
    # Check for help argument
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        return
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            try:
                async for message in read_stream:
                    try:
                        if isinstance(message, Exception):
                            error_msg = f"Invalid message format: {str(message)}"
                            logger.error(error_msg)
                            # 发送错误响应给客户端
                            await write_stream.send(
                                JSONRPCError(
                                    jsonrpc="2.0",
                                    id=None,
                                    error={
                                        "code": -32700,
                                        "message": error_msg
                                    }
                                )
                            )
                            continue
                        
                        # 检查消息类型，应该检查JSONRPCMessage
                        if not isinstance(message, JSONRPCMessage):
                            error_msg = f"Invalid message type received: {type(message)}"
                            logger.error(error_msg)
                            # 发送错误响应给客户端
                            await write_stream.send(
                                JSONRPCError(
                                    jsonrpc="2.0",
                                    id=None,
                                    error={
                                        "code": -32600,
                                        "message": error_msg
                                    }
                                )
                            )
                            continue
                        
                        # 从JSONRPCMessage中提取实际的请求对象
                        # JSONRPCMessage是一个RootModel，我们需要获取其root值
                        actual_message = message.root if hasattr(message, 'root') else message
                        
                        # 检查实际消息是否为请求类型
                        if not isinstance(actual_message, JSONRPCRequest):
                            error_msg = f"Invalid message type, expected JSONRPCRequest but got: {type(actual_message)}"
                            logger.error(error_msg)
                            # 发送错误响应给客户端
                            await write_stream.send(
                                JSONRPCError(
                                    jsonrpc="2.0",
                                    id=None,
                                    error={
                                        "code": -32600,
                                        "message": error_msg
                                    }
                                )
                            )
                            continue
                        
                        # Process message
                        msg_dict = actual_message.model_dump()
                        logger.debug(f"Received message: {msg_dict}")
                        
                        if 'method' not in msg_dict:
                            error_msg = "Invalid JSON-RPC message format: missing method"
                            logger.error(error_msg)
                            # 发送错误响应给客户端
                            if 'id' in msg_dict:
                                await write_stream.send(
                                    JSONRPCError(
                                        jsonrpc="2.0",
                                        id=msg_dict.get('id'),
                                        error={
                                            "code": -32600,
                                            "message": error_msg
                                        }
                                    )
                                )
                            continue
                            
                        response = await call_tool(
                            msg_dict['method'],
                            msg_dict.get('params', {}) or {}
                        )
                        
                        # 记录响应
                        logger.debug(f"Sending response: {response}")
                        
                        await write_stream.send(
                            JSONRPCResponse(
                                jsonrpc="2.0",
                                id=msg_dict.get('id'),
                                result={"content": response}
                            )
                        )
                            
                    except KeyboardInterrupt:
                        logger.info("Received shutdown signal")
                        break
                    except Exception as e:
                        error_msg = f"Error processing message: {str(e)}"
                        logger.exception(error_msg)  # 使用exception记录完整堆栈
                        # 尝试发送错误响应
                        try:
                            if 'actual_message' in locals() and hasattr(actual_message, 'model_dump'):
                                msg_dict = actual_message.model_dump()
                                if 'id' in msg_dict:
                                    await write_stream.send(
                                        JSONRPCError(
                                            jsonrpc="2.0",
                                            id=msg_dict['id'],
                                            error={
                                                "code": -32603,
                                                "message": error_msg
                                            }
                                        )
                                    )
                                else:
                                    # 如果没有ID，发送通知错误
                                    await write_stream.send(
                                        JSONRPCError(
                                            jsonrpc="2.0",
                                            id=None,
                                            error={
                                                "code": -32603,
                                                "message": error_msg
                                            }
                                        )
                                    )
                        except Exception as send_error:
                            logger.error(f"Error sending error response: {str(send_error)}")
            except KeyboardInterrupt:
                logger.info("Server shutdown requested")
            except Exception as e:
                logger.exception(f"Server error: {str(e)}")
                raise
    finally:
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
