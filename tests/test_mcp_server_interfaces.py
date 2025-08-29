"""MCP服务器接口测试 - 实现TODO.md中任务5的要求"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from pathlib import Path
import arxiv
import mcp.types as types

# 测试搜索论文接口
@pytest.mark.asyncio
async def test_search_papers_interface():
    """测试搜索论文接口"""
    # 导入相关模块
    from arxiv_mcp_server.tools.search import handle_search
    from arxiv_mcp_server.tools.search import _validate_categories, _build_date_filter
    
    # 验证能返回有效论文列表
    mock_client = MagicMock(spec=arxiv.Client)
    mock_paper = MagicMock(spec=arxiv.Result)
    mock_paper.get_short_id.return_value = "2103.12345"
    mock_paper.title = "Test Paper"
    mock_author = MagicMock()
    mock_author.name = "John Doe"
    mock_paper.authors = [mock_author]
    mock_paper.summary = "Test abstract"
    mock_paper.categories = ["cs.AI", "cs.LG"]
    mock_paper.published = datetime(2023, 1, 1, tzinfo=timezone.utc)
    mock_paper.pdf_url = "https://arxiv.org/pdf/2103.12345"
    
    mock_client.results.return_value = [mock_paper]
    
    with patch("arxiv.Client", return_value=mock_client):
        # 验证能返回有效论文列表
        result = await handle_search({"query": "machine learning", "max_results": 3})
        assert len(result) == 1
        # 检查返回的是TextContent对象
        assert isinstance(result[0], types.TextContent)
        content = json.loads(result[0].text)
        assert "total_results" in content
        assert "papers" in content
        assert len(content["papers"]) > 0
        
        # 验证返回结果包含标题、作者和摘要
        paper = content["papers"][0]
        assert "title" in paper
        assert "authors" in paper
        assert "abstract" in paper  # 注意：在处理函数中，summary被映射为abstract
        assert "id" in paper
        assert "categories" in paper
        assert "published" in paper
        assert "url" in paper
        
        # 验证不同查询条件的过滤效果
        result = await handle_search({
            "query": "test query", 
            "categories": ["cs.AI", "cs.LG"], 
            "max_results": 1
        })
        content = json.loads(result[0].text)
        assert len(content["papers"]) > 0
        
        # 验证错误查询的处理
        result = await handle_search({
            "query": "test query", 
            "categories": ["invalid.category"], 
            "max_results": 1
        })
        assert "Error: Invalid category" in result[0].text

# 测试下载论文接口
@pytest.mark.asyncio
async def test_download_paper_interface():
    """测试下载论文接口"""
    from arxiv_mcp_server.tools.download import handle_download, get_paper_path
    import arxiv
    
    paper_id = "2103.12345"
    
    # 验证能下载已知存在的论文
    mock_client = MagicMock(spec=arxiv.Client)
    mock_paper = MagicMock(spec=arxiv.Result)
    mock_paper.download_pdf = MagicMock()
    
    mock_client.results.return_value = iter([mock_paper])
    
    with patch("arxiv.Client", return_value=mock_client):
        with patch("asyncio.to_thread", return_value=None):
            result = await handle_download({"paper_id": paper_id})
            assert len(result) == 1
            # 检查返回的是TextContent对象
            assert isinstance(result[0], types.TextContent)
            content = json.loads(result[0].text)
            assert "status" in content
            
            # 验证无效paper_id的处理
            mock_client.results.side_effect = StopIteration()
            result = await handle_download({"paper_id": "invalid.12345"})
            content = json.loads(result[0].text)
            assert content["status"] == "error"
            assert "not found on arXiv" in content["message"]

# 测试论文列表接口
@pytest.mark.asyncio
async def test_list_papers_interface():
    """测试论文列表接口"""
    from arxiv_mcp_server.tools.list_papers import handle_list_papers
    import arxiv
    
    # 创建模拟的论文数据
    mock_client = MagicMock(spec=arxiv.Client)
    mock_paper = MagicMock(spec=arxiv.Result)
    mock_paper.title = "Test Paper"
    mock_paper.summary = "Test abstract"
    mock_author = MagicMock()
    mock_author.name = "John Doe"
    mock_paper.authors = [mock_author]
    mock_link = MagicMock()
    mock_link.href = "https://arxiv.org/abs/2103.12345"
    mock_paper.links = [mock_link]
    mock_paper.pdf_url = "https://arxiv.org/pdf/2103.12345"
    
    mock_client.results.return_value = iter([mock_paper])
    
    with patch("arxiv.Client", return_value=mock_client):
        with patch("arxiv_mcp_server.tools.list_papers.list_papers", return_value=["2103.12345"]):
            result = await handle_list_papers({})
            assert len(result) == 1
            # 检查返回的是TextContent对象
            assert isinstance(result[0], types.TextContent)
            content = json.loads(result[0].text)
            assert "total_papers" in content
            assert "papers" in content
            assert len(content["papers"]) > 0
            
            # 验证返回的论文列表格式
            paper = content["papers"][0]
            assert "title" in paper
            assert "summary" in paper
            assert "authors" in paper
            assert "links" in paper
            assert "pdf_url" in paper

# 测试阅读论文接口
@pytest.mark.asyncio
async def test_read_paper_interface():
    """测试阅读论文接口"""
    from arxiv_mcp_server.tools.read_paper import handle_read_paper
    
    paper_id = "2103.12345"
    test_content = "# Test Paper\nThis is test content with $formula$"
    
    # 验证能正确解析论文内容
    with patch("arxiv_mcp_server.tools.read_paper.list_papers", return_value=[paper_id]):
        with patch("pathlib.Path.read_text", return_value=test_content):
            result = await handle_read_paper({"paper_id": paper_id})
            assert len(result) == 1
            # 检查返回的是TextContent对象
            assert isinstance(result[0], types.TextContent)
            content = json.loads(result[0].text)
            assert content["status"] == "success"
            assert content["paper_id"] == paper_id
            assert "content" in content
            assert "$formula$" in content["content"]
            
            # 验证无效论文ID的处理
            with patch("arxiv_mcp_server.tools.read_paper.list_papers", return_value=[]):
                result = await handle_read_paper({"paper_id": "invalid.12345"})
                content = json.loads(result[0].text)
                assert content["status"] == "error"
                assert "not found" in content["message"]

# 测试提示管理接口
@pytest.mark.asyncio
async def test_prompt_management_interface():
    """测试提示管理接口"""
    from arxiv_mcp_server.prompts.handlers import list_prompts, get_prompt
    
    # 验证提示词列表获取
    prompts = await list_prompts()
    assert isinstance(prompts, list)
    # 应该至少有一个提示词
    assert len(prompts) >= 1
    
    # 验证获取特定提示词
    result = await get_prompt("deep-paper-analysis", {"paper_id": "2103.12345"})
    assert hasattr(result, 'messages')
    assert len(result.messages) == 1
    assert result.messages[0].role == "user"
    
    # 验证无效提示词处理
    with pytest.raises(ValueError, match="Prompt not found"):
        await get_prompt("invalid-prompt", {})

# 测试工具调用接口
@pytest.mark.asyncio
async def test_tool_calling_interface():
    """测试工具调用接口"""
    from arxiv_mcp_server.server import list_tools, call_tool
    import mcp.types as types
    
    # 验证工具列表获取
    tools = await list_tools()
    assert isinstance(tools, list)
    tool_names = [tool.name for tool in tools]
    expected_tools = ["search_papers", "download_paper", "list_papers", "read_paper"]
    for expected_tool in expected_tools:
        assert expected_tool in tool_names
    
    # 验证单个工具调用 - 搜索工具
    with patch("arxiv_mcp_server.server.handle_search") as mock_search:
        mock_search.return_value = [types.TextContent(type="text", text=json.dumps({"test": "result"}))]
        result = await call_tool("search_papers", {"query": "test"})
        assert len(result) == 1
        # 验证调用参数
        mock_search.assert_called_once_with({"query": "test"})
    
    # 验证工具调用参数验证
    result = await call_tool("unknown_tool", {})
    assert len(result) == 1
    assert "Error: Unknown tool" in result[0].text
    
    # 验证工具调用结果处理
    with patch("arxiv_mcp_server.server.handle_search") as mock_search:
        mock_search.side_effect = Exception("Test error")
        result = await call_tool("search_papers", {"query": "test"})
        assert len(result) == 1
        assert "Error:" in result[0].text

if __name__ == "__main__":
    pytest.main([__file__, "-v"])