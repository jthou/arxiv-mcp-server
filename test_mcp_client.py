#!/usr/bin/env python3
"""
简单的MCP客户端测试脚本，用于测试arxiv-mcp-server的基本功能
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_mcp_server():
    """测试MCP服务器"""
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    
    # 启动MCP服务器进程
    process = subprocess.Popen(
        [sys.executable, "-m", "arxiv_mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1
    )
    
    try:
        # 发送list_tools请求
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "list_tools",
            "params": {}
        }
        
        # 发送请求
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response = process.stdout.readline()
        print("服务器响应:")
        print(response)
        
        # 解析响应
        try:
            response_data = json.loads(response)
            if "result" in response_data:
                print("成功接收到服务器响应:")
                print(json.dumps(response_data["result"], indent=2))
            else:
                print("服务器返回错误:")
                print(json.dumps(response_data, indent=2))
        except json.JSONDecodeError:
            print("无法解析服务器响应:")
            print(response)
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        # 终止进程
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())