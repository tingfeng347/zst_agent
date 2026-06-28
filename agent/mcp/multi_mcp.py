import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient(
    {
        "WebSearch": {
            "transport": "streamable_http",
            "url": "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp",
            "headers": {"Authorization": f"Bearer {os.getenv('DASHSCOPE_API_KEY')}"},
        }
    }
)

_mcp_tools_cache = None


def get_mcp_tools():
    """获取 MCP 工具列表"""
    global _mcp_tools_cache
    if _mcp_tools_cache is not None:
        return _mcp_tools_cache
    
    _mcp_tools_cache = asyncio.run(mcp_client.get_tools())
    return _mcp_tools_cache
