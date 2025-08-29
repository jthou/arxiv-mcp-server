#!/usr/bin/env python3
"""
MCP客户端演示脚本，展示如何使用arxiv-mcp-server的各种功能
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
    
    response = process.stdout.readline()
    return json.loads(response)

async def demo_mcp_server():
    """演示MCP服务器功能"""
    print("=== arxiv-mcp-server 功能演示 ===\n")
    
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
                "query": "transformer architecture",
                "max_results": 3,
                "categories": ["cs.CL", "cs.LG"]
            }
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            search_result = response["result"]["content"][0]["text"]
            print(search_result)
        else:
            print("错误:", response)
        print("\n" + "="*50 + "\n")
        
        # 3. 列出提示模板
        print("3. 列出可用的提示模板:")
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "list_prompts",
            "params": {}
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            prompts_text = response["result"]["content"][0]["text"]
            print(prompts_text)
        else:
            print("错误:", response)
        print("\n" + "="*50 + "\n")
        
        # 4. 获取特定提示模板
        print("4. 获取深度论文分析提示模板:")
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "get_prompt",
            "params": {
                "name": "deep-paper-analysis",
                "arguments": {
                    "paper_id": "2302.14017v1"
                }
            }
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            prompt_content = response["result"]["content"][0]["text"]
            print(prompt_content)
        else:
            print("错误:", response)
        print("\n" + "="*50 + "\n")
        
        print("演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
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
    asyncio.run(demo_mcp_server())