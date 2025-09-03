# MCP stdio服务器设计原则

在开发和调试基于stdio协议的MCP服务器过程中，我们总结了以下关键设计原则，以确保服务器的稳定性和可靠性。

## 1. 通信协议原则

### 1.1 纯净的stdio通信
- 服务器必须仅通过标准输入/输出进行通信，不得向stdout/stderr输出任何非JSON-RPC协议的数据
- 所有日志和调试信息应重定向到文件，避免干扰通信协议
- 客户端和服务端之间的所有数据交换都必须遵循JSON-RPC 2.0规范

### 1.2 消息类型处理
- 正确处理`JSONRPCMessage`包装类型，它是一个RootModel，包装了`Union[JSONRPCRequest, JSONRPCNotification, JSONRPCResponse, JSONRPCError]`
- 在接收消息时，需要从`JSONRPCMessage`中提取实际的请求对象
- 发送响应时使用正确的响应类型，如`JSONRPCResponse`或`JSONRPCError`

### 1.3 错误处理机制
- 对于每个接收到的请求，必须发送相应的响应（成功或错误）
- 错误响应应包含适当的错误代码和描述信息
- 服务器内部错误应记录到日志文件中，同时向客户端发送结构化的错误信息

## 2. 日志系统原则

### 2.1 日志输出隔离
- 日志不得输出到stdout或stderr，以免干扰stdio通信
- 使用文件处理器将日志重定向到专用日志文件
- 设置适当的日志级别以平衡调试信息和性能

### 2.2 日志内容规范
- 记录关键的请求处理过程，便于问题追踪
- 记录错误和异常的完整堆栈信息
- 避免记录敏感信息，如请求参数中的私密数据

## 3. 消息处理原则

### 3.1 消息验证
- 验证接收到的消息是否为有效的JSON-RPC消息
- 检查必需字段（如method、jsonrpc）是否存在
- 对无效消息发送适当的错误响应

### 3.2 请求处理
- 异步处理每个请求，避免阻塞其他请求
- 正确解析请求参数并验证其有效性
- 在处理完成后及时发送响应

### 3.3 响应格式
- 响应必须包含与请求相同的id字段
- 成功响应使用`result`字段，错误响应使用`error`字段
- 响应数据应符合客户端期望的格式

## 4. 服务生命周期原则

### 4.1 启动和关闭
- 服务器启动后应立即进入监听状态，等待客户端请求
- 正确处理关闭信号，确保资源得到释放
- 提供帮助信息等基本命令行功能

### 4.2 资源管理
- 合理管理内存和文件句柄等资源
- 及时关闭不再需要的资源
- 避免内存泄漏和资源竞争

## 5. 调试和测试原则

### 5.1 调试友好性
- 提供详细的日志记录以便问题诊断
- 在关键处理节点添加调试信息
- 设计易于测试的接口和功能

### 5.2 测试覆盖
- 编写全面的单元测试和集成测试
- 测试正常流程和各种异常情况
- 验证通信协议的正确性

## 6. 最佳实践示例

### 6.1 消息处理示例
```python
async for message in read_stream:
    try:
        # 验证消息类型
        if not isinstance(message, JSONRPCMessage):
            logger.error(f"Invalid message type received: {type(message)}")
            continue
            
        # 提取实际请求对象
        actual_message = message.root if hasattr(message, 'root') else message
        
        # 处理请求
        msg_dict = actual_message.model_dump()
        response = await call_tool(
            msg_dict['method'],
            msg_dict.get('params', {}) or {}
        )
        
        # 发送响应
        await write_stream.send(
            JSONRPCResponse(
                jsonrpc="2.0",
                id=msg_dict.get('id'),
                result={"content": response}
            )
        )
    except Exception as e:
        logger.exception(f"Error processing message: {str(e)}")
```

### 6.2 日志配置示例
```python
# 配置日志，将日志输出到文件而不是stdout/stderr
logger = logging.getLogger("mcp-server")
file_handler = logging.FileHandler('mcp_server.log')
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False  # 避免日志传播到父级处理器
```

这些原则基于我们在调试arxiv-mcp-server过程中遇到的实际问题和解决方案，旨在帮助开发者构建稳定、可靠的MCP stdio服务器。