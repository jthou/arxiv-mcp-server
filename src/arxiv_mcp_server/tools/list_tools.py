"""List tools functionality for the arXiv MCP server."""

from typing import Dict, Any, List
import mcp.types as types
from ..config import Settings

settings = Settings()

list_tools_tool = types.Tool(
    name="list_tools",
    description="List all available tools in the arXiv MCP server",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

async def handle_list_tools(
    arguments: Dict[str, Any] = None
) -> List[types.TextContent]:
    """Handle requests to list all available tools."""
    from . import search_tool, download_tool, list_tool, read_tool, list_tools_tool
    
    tools = [search_tool, download_tool, list_tool, read_tool, list_tools_tool]
    
    tool_list = "\n".join([
        f"{tool.name}: {tool.description.split('.')[0]}"
        for tool in tools
    ])
    
    return [types.TextContent(type="text", text=tool_list)]
