# VS Code 集成指南

本文档详细说明如何将 arxiv-mcp-server 集成到 Visual Studio Code 中，以便在支持 MCP 协议的环境中使用。

## 前提条件

1. 已安装 Visual Studio Code
2. 已安装支持 MCP 协议的扩展（如 Qwen Chat 或其他支持 MCP 的扩展）
3. 已按照 [DEPLOYMENT.md](DEPLOYMENT.md) 中的说明部署了 arxiv-mcp-server

## 配置方法

### 方法一：全局配置（推荐）

1. 找到 VS Code 的全局设置目录：
   - Windows: `%APPDATA%\Code\User\`
   - macOS: `~/Library/Application Support/Code/User/`
   - Linux: `~/.config/Code/User/`

2. 在该目录下创建或编辑 `mcp.json` 文件，添加以下配置：

```json
{
    "mcpServers": {
        "arxiv-mcp-server": {
            "command": "python",
            "args": [
                "-m",
                "arxiv_mcp_server",
                "--storage-path",
                "~/Documents/arxiv-papers"
            ]
        }
    }
}
```

3. 根据你的实际环境调整以下参数：
   - `command`: Python 解释器路径（如果不在 PATH 中，需要使用完整路径）
   - `args`: 命令行参数，特别是 `--storage-path` 的值应指向你希望存储论文的目录

### 方法二：项目级配置

1. 在你的项目根目录创建 `.vscode/mcp.json` 文件
2. 添加相同的配置内容：

```json
{
    "mcpServers": {
        "arxiv-mcp-server": {
            "command": "python",
            "args": [
                "-m",
                "arxiv_mcp_server",
                "--storage-path",
                "./arxiv-papers"
            ]
        }
    }
}
```

## 配置参数说明

### command
指定用于启动 arxiv-mcp-server 的命令。通常为 `python`，但如果 Python 不在系统 PATH 中，可能需要使用完整路径，如 `/usr/bin/python3` 或 `C:\Python311\python.exe`。

### args
传递给 arxiv-mcp-server 的命令行参数：
- `-m arxiv_mcp_server`: 指定要运行的 Python 模块
- `--storage-path`: 指定论文存储目录的路径

### storage-path 选项
存储路径可以是：
- 绝对路径：如 `/home/user/arxiv-papers` 或 `C:\Users\user\Documents\arxiv-papers`
- 相对路径：相对于 VS Code 工作目录的路径，如 `./arxiv-papers`
- 用户目录：使用 `~` 表示用户主目录，如 `~/Documents/arxiv-papers`

## 验证配置

1. 重启 VS Code 以确保配置生效
2. 打开支持 MCP 的扩展（如 Qwen Chat）
3. 在扩展中查找并连接到 "arxiv-mcp-server"
4. 尝试使用服务器功能，如搜索论文或下载论文

## 故障排除

### 问题1：VS Code 无法找到 arxiv-mcp-server

**可能原因**: Python 模块未正确安装或不在 PYTHONPATH 中

**解决方案**:
1. 确保已正确安装 arxiv-mcp-server：
   ```bash
   pip install -e .
   ```
2. 验证模块是否可导入：
   ```bash
   python -c "import arxiv_mcp_server; print('Module found')"
   ```

### 问题2：权限错误

**可能原因**: 存储目录没有写权限

**解决方案**:
1. 确保存储目录存在：
   ```bash
   mkdir -p ~/Documents/arxiv-papers
   ```
2. 确保存储目录有写权限：
   ```bash
   chmod 755 ~/Documents/arxiv-papers
   ```

### 问题3：Python 版本不兼容

**可能原因**: 使用了不兼容的 Python 版本

**解决方案**:
1. 检查 Python 版本：
   ```bash
   python --version
   ```
2. 如果版本低于 3.11，建议升级 Python 或使用虚拟环境：
   ```bash
   # 创建虚拟环境
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -e .
   ```

### 问题4：扩展无法连接到服务器

**可能原因**: 扩展配置不正确或服务器未正确启动

**解决方案**:
1. 检查扩展的 MCP 配置是否正确
2. 在终端手动测试服务器启动：
   ```bash
   python -m arxiv_mcp_server --storage-path ~/Documents/arxiv-papers
   ```
3. 查看是否有错误信息输出

## 高级配置

### 使用 uv 工具管理

如果你使用 uv 工具管理 Python 项目，可以使用以下配置：

```json
{
    "mcpServers": {
        "arxiv-mcp-server": {
            "command": "uv",
            "args": [
                "run",
                "arxiv-mcp-server",
                "--storage-path",
                "~/Documents/arxiv-papers"
            ]
        }
    }
}
```

### 使用虚拟环境

如果你在虚拟环境中安装了 arxiv-mcp-server，需要指定虚拟环境中的 Python 解释器：

```json
{
    "mcpServers": {
        "arxiv-mcp-server": {
            "command": "/path/to/your/venv/bin/python",
            "args": [
                "-m",
                "arxiv_mcp_server",
                "--storage-path",
                "~/Documents/arxiv-papers"
            ]
        }
    }
}
```

## 更新配置

当更新 arxiv-mcp-server 时，通常不需要修改配置，除非：
1. 项目结构发生重大变化
2. 命令行参数发生变化
3. Python 模块名称发生变化

在这种情况下，请参考更新后的文档调整配置。

## 相关文档

- [DEPLOYMENT.md](DEPLOYMENT.md) - 部署指南
- [README.md](../README.md) - 项目概述