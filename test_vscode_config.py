#!/usr/bin/env python3
"""
测试VS Code配置的arxiv-mcp-server是否正常工作
"""

import asyncio
import json
import subprocess
import sys
import os

async def send_request(process, request):
    """发送请求并接收响应"""
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    
    try:
        response = process.stdout.readline()
        return json.loads(response)
    except Exception as e:
        return {"error": f"读取响应时出错: {e}"}

async def test_arxiv_mcp_server():
    """测试arxiv-mcp-server是否正常工作"""
    print("=== 测试VS Code配置的arxiv-mcp-server ===\n")
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = "/System/Volumes/Data/justin/dev/arxiv-mcp-server-qoder/src"
    
    # 使用VS Code配置中的命令和参数启动MCP服务器进程
    process = subprocess.Popen(
        ["python", "-m", "arxiv_mcp_server", "--storage-path", "/Users/jintinghou/Documents/arxiv-papers"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1
    )
    
    try:
        # 1. 列出所有工具
        print("1. 列出所有可用工具:")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "list_tools",
            "params": {}
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            tools_text = response["result"]["content"][0]["text"]
            print(tools_text)
        else:
            print("错误:", response)
        print("\n" + "="*50 + "\n")
        
        # 2. 搜索论文示例
        print("2. 搜索论文示例:")
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "search_papers",
            "params": {
                "query": "sonar detection",
                "max_results": 3,
                "categories": ["cs.RO", "cs.AI", "eess.SP"]
            }
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            search_result = response["result"]["content"][0]["text"]
            print(search_result)
        else:
            print("错误:", response)
        print("\n" + "="*50 + "\n")
        
        print("测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 终止进程
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    asyncio.run(test_arxiv_mcp_server())