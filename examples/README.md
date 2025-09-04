# MCP客户端示例

这个目录包含了与arxiv-mcp-server通信的各种客户端示例。

## 示例列表

### Bash客户端
- **文件**: `bash-mcp-client.sh`
- **描述**: 使用Bash脚本实现的MCP客户端
- **功能**: 
  - 启动MCP服务器作为后台进程
  - 通过命名管道与服务器通信
  - 发送JSON-RPC请求并接收响应
  - 测试服务器连接和工具列表
  - 正确停止服务器和清理资源

## 使用方法

### Bash客户端
```bash
# 确保在项目根目录
cd /path/to/arxiv-mcp-server-qoder

# 安装依赖
pip install -e .

# 运行Bash客户端示例
chmod +x examples/bash-mcp-client.sh
./examples/bash-mcp-client.sh
```

## 依赖要求

- Python 3.11+
- arxiv-mcp-server模块
- coreutils (for timeout command on macOS)

## 注意事项

- 确保在项目根目录运行示例
- 示例脚本会自动设置正确的Python路径
- 所有临时文件会在测试完成后自动清理
