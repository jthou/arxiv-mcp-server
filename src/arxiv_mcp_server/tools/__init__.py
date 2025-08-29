"""Tool definitions for the arXiv MCP server."""

from .search import search_tool, handle_search
from .download import download_tool, handle_download
from .list_papers import list_tool, handle_list_papers
from .read_paper import read_tool, handle_read_paper
from .list_tools import list_tools_tool, handle_list_tools


__all__ = [
    "search_tool",
    "download_tool",
    "read_tool",
    "list_tool",
    "list_tools_tool",
    "handle_search",
    "handle_download",
    "handle_read_paper",
    "handle_list_papers",
    "handle_list_tools",
]
