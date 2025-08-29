#!/usr/bin/env python3
"""
下载并阅读关于水下自主清洁机器人的论文
"""

import asyncio
import json
import subprocess
import sys
import os
import time

async def send_request(process, request):
    """发送请求并接收响应"""
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    
    response = process.stdout.readline()
    return json.loads(response)

async def read_pool_cleaning_paper():
    """下载并阅读水下自主清洁机器人的论文"""
    print("=== 下载并阅读水下自主清洁机器人的论文 ===\n")
    
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
        # 1. 下载论文
        print("1. 下载论文 (ID: 2304.08185v1)...")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "download_paper",
            "params": {
                "paper_id": "2304.08185v1"
            }
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            download_result = response["result"]["content"][0]["text"]
            print("下载结果:")
            print(download_result)
        else:
            print("下载错误:", response)
        
        # 等待转换完成
        print("\n等待转换完成...")
        time.sleep(10)
        
        # 2. 阅读论文
        print("\n2. 阅读论文...")
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "read_paper",
            "params": {
                "paper_id": "2304.08185v1"
            }
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            paper_content = response["result"]["content"][0]["text"]
            print("论文内容:")
            print(paper_content)
        else:
            print("阅读错误:", response)
            
        # 3. 列出所有已下载的论文
        print("\n3. 列出所有已下载的论文...")
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "list_papers",
            "params": {}
        }
        
        response = await send_request(process, request)
        if "result" in response and "content" in response["result"]:
            papers_list = response["result"]["content"][0]["text"]
            print("已下载的论文:")
            print(papers_list)
        else:
            print("列出论文错误:", response)
            
    except Exception as e:
        print(f"过程中出现错误: {e}")
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
    asyncio.run(read_pool_cleaning_paper())