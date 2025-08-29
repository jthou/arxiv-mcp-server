"""
Arxiv MCP Server initialization
"""

from . import server
from . import config
import asyncio


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())


__all__ = ["main", "server", "config"]