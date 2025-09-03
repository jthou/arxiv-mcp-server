[![Twitter Follow](https://img.shields.io/twitter/follow/JoeBlazick?style=social)](https://twitter.com/JoeBlazick)
[![smithery badge](https://smithery.ai/badge/arxiv-mcp-server)](https://smithery.ai/server/arxiv-mcp-server)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/blazickjp/arxiv-mcp-server/actions/workflows/tests.yml/badge.svg)](https://github.com/blazickjp/arxiv-mcp-server/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://img.shields.io/pypi/dm/arxiv-mcp-server.svg)](https://pypi.org/project/arxiv-mcp-server/)
[![PyPI Version](https://img.shields.io/pypi/v/arxiv-mcp-server.svg)](https://pypi.org/project/arxiv-mcp-server/)

# ArXiv MCP Server

> 🔍 Enable AI assistants to search and access arXiv papers through a simple MCP interface.

The ArXiv MCP Server provides a bridge between AI assistants and arXiv's research repository through the Model Context Protocol (MCP). It allows AI models to search for papers and access their content in a programmatic way.

<div align="center">
  
🤝 **[Contribute](https://github.com/blazickjp/arxiv-mcp-server/blob/main/CONTRIBUTING.md)** • 
📝 **[Report Bug](https://github.com/blazickjp/arxiv-mcp-server/issues)**

<a href="https://www.pulsemcp.com/servers/blazickjp-arxiv-mcp-server"><img src="https://www.pulsemcp.com/badge/top-pick/blazickjp-arxiv-mcp-server" width="400" alt="Pulse MCP Badge"></a>
</div>

## 系统要求

arxiv-mcp-server 需要以下环境：

- Python 3.11+
- Git
- curl
- 可选: uv (Astral) (用于更快的依赖安装)

## 核心功能

arxiv-mcp-server 提供以下主要功能：

- 🔎 **论文搜索**：支持关键词、时间范围、分类等条件的论文检索
- 📄 **论文访问**：根据 arXiv ID 下载和阅读论文
- 📋 **论文列表**：查看本地已下载的论文列表
- 🗃️ **本地存储**：论文保存在本地以提高访问速度
- 📝 **研究提示**：提供完整的论文分析流程提示

## 部署选项

### 本地系统级部署（推荐）

```bash
# 当前已在项目目录中
# 查看当前仓库信息
git remote -v
git status

# 系统级安装依赖
pip install -e .

# 运行服务
python -m arxiv_mcp_server --storage-path /path/to/paper/storage
```

### 使用 uv 工具部署

```bash
# 安装 uv (如果尚未安装)
# macOS: brew install uv
# 其他系统: pip install uv

# 直接运行（无需安装）
uv tool run arxiv-mcp-server --storage-path /path/to/paper/storage

# 或者安装后运行
uv tool install arxiv-mcp-server
arxiv-mcp-server --storage-path /path/to/paper/storage
```

## MCP 服务器特性说明

arxiv-mcp-server 是一个 MCP（Model Context Protocol）服务器，它通过标准输入/输出与客户端通信，而不是作为一个独立的 Web 服务运行。启动服务后不会在终端显示运行信息，需要通过支持 MCP 协议的客户端（如 Claude Desktop）进行通信。

## 配置选项

### 命令行参数

| 参数 | 描述 |
|------|------|
| `--storage-path` | 指定论文存储目录 |
| `--help`, `-h` | 显示帮助信息 |

### 环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `ARXIV_STORAGE_PATH` | ~/.arxiv-mcp-server/papers | 论文存储目录 |

### 自定义配置示例

```bash
# 方法1: 使用命令行参数
python -m arxiv_mcp_server --storage-path /mnt/data/papers

# 方法2: 设置环境变量
export ARXIV_STORAGE_PATH=/mnt/data/papers
python -m arxiv_mcp_server

# 方法3: 使用 uv 工具
uv tool run arxiv-mcp-server --storage-path /mnt/data/papers
```

## 获取帮助信息

要查看服务器的帮助信息，可以使用以下方法：

使用 `--help` 或 `-h` 参数：
```bash
python -m arxiv_mcp_server --help
```

## 测试

在部署后，建议运行测试以确保服务正常工作：

```
# 手动设置 PYTHONPATH
PYTHONPATH=src python -m pytest
```

## 集成其他文档

有关更详细的配置和使用信息，请参阅以下文档：

- [VS Code Integration](docs/VS_CODE_INTEGRATION.md) - 如何与 Visual Studio Code 集成
- [MCP stdio Server Principles](docs/MCP_STDIO_SERVER_PRINCIPLES.md) - MCP stdio 服务器设计原则

## 常见问题

### 服务启动后似乎"卡住"了

这是正常现象。arxiv-mcp-server 是一个 MCP 服务器，通过标准输入/输出与客户端通信，不会在终端显示运行信息。要使用该服务，需要通过支持 MCP 协议的客户端（如 Claude Desktop）进行连接。

### 如何验证服务是否正常运行

由于 MCP 服务器的特性，无法直接通过终端查看运行状态。可以通过以下方式验证：

1. 检查进程是否存在:
   ```bash
   ps aux | grep arxiv_mcp_server
   ```

2. 运行测试验证功能:
   ```bash
   python run_tests.py
   ```

3. 通过 MCP 客户端测试连接