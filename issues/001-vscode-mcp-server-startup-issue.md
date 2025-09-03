# VS Code MCP Server 启动失败问题报告

## 问题描述

在 VS Code 中启动 arxiv-mcp-server 时遇到模块找不到的错误：

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

### 1. 模块路径问题
VS Code 尝试使用 `/opt/anaconda3/bin/python -m arxiv_mcp_server` 启动服务器，但 Python 无法找到 `arxiv_mcp_server` 模块，因为：
- 模块位于项目的 `src/arxiv_mcp_server` 目录下
- Python 的模块搜索路径中没有包含 `src` 目录

### 2. 依赖问题
即使设置了 `PYTHONPATH=src`，仍然出现 `ModuleNotFoundError: No module named 'mcp.shared.message'` 错误，说明依赖可能没有正确安装或者版本不兼容。

### 3. 安装问题
虽然 `pip show arxiv-mcp-server` 显示包已安装，但显示的位置是 `/opt/anaconda3/lib/python3.12/site-packages`，而可编辑项目位置指向了当前目录，这表明使用了 `pip install -e .` 进行了可编辑安装。

## 重现步骤

1. 在 VS Code 中配置 arxiv-mcp-server
2. 尝试启动服务器
3. 观察错误日志

## 预期行为

服务器应该正常启动并可以被 VS Code MCP 客户端连接。

## 实际行为

服务器启动失败，报错 "No module named arxiv_mcp_server"

## 解决方案

详细的解决方案请参见：[001-vscode-mcp-server-startup-issue-resolution.md](001-vscode-mcp-server-startup-issue-resolution.md)

## 环境信息

- 操作系统: macOS 15.4
- Python 版本: 3.12 (通过 Anaconda)
- arxiv-mcp-server 版本: 0.3.1
- VS Code 版本: Qoder IDE 0.1.17

## 其他信息

这个问题可能影响所有使用 VS Code 集成 arxiv-mcp-server 的用户，需要尽快修复以确保良好的用户体验。