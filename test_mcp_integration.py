import asyncio
from mcp.client import Client

async def test_mcp_server():
    client = Client()
    await client.connect("arxiv-mcp-server")
    
    try:
        # Test search functionality
        search_results = await client.call_tool(
            "search_papers",
            {"query": "machine learning", "max_results": 3}
        )
        print("Search Results:", search_results)
        
        # Test list papers functionality
        papers_list = await client.call_tool("list_papers", {})
        print("Papers List:", papers_list)
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())