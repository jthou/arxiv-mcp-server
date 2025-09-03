# MCP客户端示例文档

## 概述

本文档介绍了如何创建和使用MCP客户端与arxiv-mcp-server进行通信。通过MCP协议，客户端可以调用服务器提供的各种工具，如搜索论文、下载论文等。

## 客户端实现原理

MCP客户端通过标准输入/输出(stdio)与服务器进行通信，使用JSON-RPC协议格式交换消息。客户端需要正确处理消息的发送和接收，包括处理`JSONRPCMessage`包装。

## 示例客户端实现

项目中的[temp/uw_sim_downloader.py](file:///System/Volumes/Data/justin/dev/arxiv-mcp-server-qoder/temp/uw_sim_downloader.py)文件是一个完整的MCP客户端示例，它演示了如何：

1. 建立与服务器的连接
2. 发送请求并接收响应
3. 处理JSON-RPC消息
4. 调用服务器工具

### 关键实现要点

#### 1. 使用标准MCP客户端库

```python
from mcp.client.stdio import stdio_client, StdioServerParameters

# 创建服务器参数
server_params = StdioServerParameters(
    command=sys.executable,
    args=["-m", "arxiv_mcp_server", "--storage-path", str(target_dir.absolute())]
)

# 建立连接
async with stdio_client(server_params) as (read_stream, write_stream):
    # 进行通信
```

#### 2. 正确处理JSON-RPC消息

响应对象可能是一个`JSONRPCMessage`包装，需要访问其`root`属性获取实际的响应对象：

```python
# 处理JSONRPCMessage包装
if response and hasattr(response, 'root'):
    actual_response = response.root
else:
    actual_response = response
```

#### 3. 发送请求并接收响应

```python
async def send_request(write_stream, read_stream, request):
    """发送请求到MCP服务器并接收响应"""
    # 发送请求
    await write_stream.send(request)
    
    # 读取响应
    try:
        response = await asyncio.wait_for(read_stream.receive(), timeout=60.0)
        return response
    except asyncio.TimeoutError:
        print("读取服务器响应超时")
        return None
    except Exception as e:
        print(f"读取服务器响应时出错: {e}")
        return None
```

## 客户端使用流程

1. **建立连接**：使用`stdio_client`建立与服务器的连接
2. **列出工具**：调用`list_tools`方法获取服务器支持的工具列表
3. **调用工具**：根据需要调用相应的工具，如`search_papers`、`download_paper`等
4. **处理响应**：正确解析服务器返回的响应数据
5. **关闭连接**：完成操作后关闭与服务器的连接

## 工具调用示例

### 搜索论文

```python
request = types.JSONRPCRequest(
    jsonrpc="2.0",
    id=2,
    method="search_papers",
    params={
        "query": '"underwater simulation"',
        "max_results": 10,
        "date_from": "2019-01-01",
        "categories": ["cs.GR", "cs.CV"],
        "sort_by": "relevance"
    }
)
```

### 下载论文

```python
request = types.JSONRPCRequest(
    jsonrpc="2.0",
    id=3,
    method="download_paper",
    params={
        "paper_id": "2103.12345"
    }
)
```

## 错误处理

客户端需要处理多种可能的错误情况：

1. **超时错误**：服务器响应超时
2. **解析错误**：响应数据格式不正确
3. **网络错误**：与服务器通信中断
4. **服务器错误**：服务器内部错误

## 最佳实践

1. **设置合适的超时时间**：根据操作类型设置合理的超时时间
2. **正确处理消息包装**：始终检查并处理`JSONRPCMessage`包装
3. **错误日志记录**：记录详细的错误信息以便调试
4. **资源清理**：确保在操作完成后正确清理资源