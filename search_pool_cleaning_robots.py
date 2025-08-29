#!/usr/bin/env python3
"""
搜索关于泳池清洁机器人的论文
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

async def search_pool_cleaning_papers():
    """搜索关于泳池清洁机器人的论文（不限时间范围）"""
    print("=== 搜索关于泳池清洁机器人的论文（不限时间范围） ===\n")
    
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
        # 尝试更广泛的搜索关键词
        search_terms = [
            "pool cleaning robot",
            "swimming pool robot", 
            "aquatic cleaning robot",
            "underwater robot cleaning",
            "pool maintenance robot",
            "autonomous pool cleaner",
            "underwater cleaning robot",
            "aquatic robot cleaning",
            "pool robot vacuum"
        ]
        
        # 扩展搜索领域
        categories = ["cs.RO", "cs.AI", "cs.SY", "cs.MA", "cs.LG", "physics.flu-dyn", "physics.class-ph"]
        
        for i, term in enumerate(search_terms, 1):
            print(f"\n尝试搜索关键词: {term}")
            request = {
                "jsonrpc": "2.0",
                "id": i,
                "method": "search_papers",
                "params": {
                    "query": term,
                    "max_results": 3,
                    "categories": categories
                }
            }
            
            response = await send_request(process, request)
            if "result" in response and "content" in response["result"]:
                search_result = response["result"]["content"][0]["text"]
                print(f"搜索结果 ({term}):")
                print(search_result)
            else:
                print(f"错误 ({term}):", response)
        
        # 尝试组合搜索
        print(f"\n尝试组合搜索关键词: underwater robot AND cleaning")
        request = {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "search_papers",
            "params": {
                "query": "underwater robot AND cleaning",
                "max_results": 5,
                "categories": categories
            }
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            search_result = response["result"]["content"][0]["text"]
            print(f"搜索结果 (underwater robot AND cleaning):")
            print(search_result)
        else:
            print(f"错误 (underwater robot AND cleaning):", response)
            
    except Exception as e:
        print(f"搜索过程中出现错误: {e}")
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
    asyncio.run(search_pool_cleaning_papers())