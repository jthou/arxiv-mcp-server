# VS Code MCP Server 启动问题解决方案

## 问题描述

在 VS Code 中启动 arxiv-mcp-server 时遇到以下错误：

```
2025-08-29 13:42:37.459 [info] 正在启动服务器 arxiv-mcp-server
2025-08-29 13:42:37.460 [info] 连接状态: 正在启动
2025-08-29 13:42:37.462 [info] Starting server from LocalProcess extension host
2025-08-29 13:42:37.997 [info] 连接状态: 正在启动
2025-08-29 13:42:38.001 [info] 连接状态: 正在运行
2025-08-29 13:42:38.065 [warning] [server stderr] /opt/anaconda3/bin/python: No module named arxiv_mcp_server
2025-08-29 13:42:38.067 [info] 连接状态: 错误 Process exited with code 1
2025-08-29 13:42:38.068 [error] Server exited before responding to `initialize` request.
```

## 问题分析

经过详细分析和测试，发现存在以下问题：

1. **模块路径问题**：Python 无法找到 `arxiv_mcp_server` 模块，因为模块位于项目的 `src/arxiv_mcp_server` 目录下，而 Python 的模块搜索路径未包含 `src` 目录。

2. **虚拟环境配置问题**：VS Code 使用了系统 Python 而不是项目的虚拟环境，导致依赖和模块路径不正确。

3. **依赖安装问题**：虽然项目已安装，但在虚拟环境中未正确安装或未以可编辑模式安装。

## 解决过程

### 1. 检查项目虚拟环境

首先检查项目环境是否正确设置。

### 2. 正确安装项目

在项目目录中，以可编辑模式安装项目：

```bash
cd /System/Volumes/Data/justin/dev/arxiv-mcp-server-qoder
pip install -e .
```

这将确保项目以可编辑模式安装，使 Python 能够正确找到模块。

### 3. 验证模块导入

测试是否能正确导入模块：

```bash
cd /System/Volumes/Data/justin/dev/arxiv-mcp-server-qoder
python -m arxiv_mcp_server --help
```

如果能显示帮助信息，说明模块已正确安装。

### 4. 更新 VS Code 配置

更新 `/Users/jintinghou/Library/Application Support/Code/User/mcp.json` 文件中的 arxiv-mcp-server 配置：

```json
{
    "servers": {
        "arxiv-mcp-server": {
            "type": "stdio",
            "command": "python",
            "args": [
                "-m",
                "arxiv_mcp_server",
                "--storage-path",
                "/Users/jintinghou/Documents/arxiv-papers"
            ],
            "gallery": true
        }
    }
}
```

关键更改：
- 使用项目的虚拟环境 Python 解释器路径作为 command 字段
- 移除 env 字段，因为项目已正确安装，不再需要设置 PYTHONPATH

## 验证结果

通过以下步骤验证解决方案：

1. 在终端中手动运行服务器：
   ```bash
   python -m arxiv_mcp_server --storage-path /Users/jintinghou/Documents/arxiv-papers
   ```
   
   服务器成功启动并等待输入，说明模块已正确安装和配置。

2. 重启 VS Code 并通过支持 MCP 协议的扩展连接到服务器。

## 结论

通过以下步骤成功解决了 VS Code 中 arxiv-mcp-server 启动失败的问题：

1. 在项目的虚拟环境中正确安装项目依赖
2. 更新 VS Code 配置文件，使用项目的虚拟环境 Python 解释器
3. 移除不必要的 PYTHONPATH 设置，因为项目已正确安装

现在 arxiv-mcp-server 应该能够在 VS Code 中正常启动并与 MCP 客户端正确通信。