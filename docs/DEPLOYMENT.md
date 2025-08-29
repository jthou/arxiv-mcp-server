# Arxiv MCP Server 部署指南

## 系统要求
- Python 3.11+
- Git
- curl
- 可选: uv (Astral) (用于更快的依赖安装)
- 可选: Docker (用于容器化部署)

## 部署选项

### 1. 本地系统级部署（推荐）
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

### 2. 使用虚拟环境部署
```bash
# 当前已在项目目录中
# 查看当前仓库信息
git remote -v
git status

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -e .

# 运行服务
python -m arxiv_mcp_server --storage-path /path/to/paper/storage
```

### 3. 使用deploy.sh脚本部署
```bash
# 当前已在项目目录中
# 查看当前仓库信息
git remote -v
git status

# 运行部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 4. 使用show-help.sh脚本查看帮助
```bash
# 当前已在项目目录中
# 查看帮助信息
chmod +x scripts/show-help.sh
./scripts/show-help.sh
```

### 5. 使用uv工具部署
```bash
# 安装uv (如果尚未安装)
# macOS: brew install uv
# 其他系统: pip install uv

# 直接运行（无需安装）
uv tool run arxiv-mcp-server --storage-path /path/to/paper/storage

# 或者安装后运行
uv tool install arxiv-mcp-server
arxiv-mcp-server --storage-path /path/to/paper/storage
```

### 6. Docker部署
```bash
# 构建并运行Docker容器
./scripts/docker-build.sh

# 或者手动构建和运行
docker build -t arxiv-mcp-server .
docker run -d \
  --name arxiv-mcp-server \
  -p 8000:8000 \
  -v ./data:/app/data \
  arxiv-mcp-server

# 查看容器日志
docker logs -f arxiv-mcp-server

# 停止容器
docker stop arxiv-mcp-server
```

## MCP服务器特性说明

arxiv-mcp-server是一个MCP（Model Context Protocol）服务器，它通过标准输入/输出与客户端通信，而不是作为一个独立的Web服务运行。启动服务后不会在终端显示运行信息，需要通过支持MCP协议的客户端（如Claude Desktop）进行通信。

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

### 配置文件
项目使用 `src/arxiv_mcp_server/config.py` 进行配置，可以通过环境变量或命令行参数覆盖默认值。

### 自定义配置示例
```bash
# 方法1: 使用命令行参数
python -m arxiv_mcp_server --storage-path /mnt/data/papers

# 方法2: 设置环境变量
export ARXIV_STORAGE_PATH=/mnt/data/papers
python -m arxiv_mcp_server

# 方法3: 使用uv工具
uv tool run arxiv-mcp-server --storage-path /mnt/data/papers

# 方法4: Docker环境变量
docker run -d \
  --name arxiv-mcp-server \
  -e ARXIV_STORAGE_PATH=/app/data/papers \
  arxiv-mcp-server
```

## 获取帮助信息

要查看服务器的帮助信息，可以使用以下任一方法：

1. 使用 `--help` 或 `-h` 参数：
   ```bash
   python -m arxiv_mcp_server --help
   ```

2. 使用提供的脚本：
   ```bash
   ./scripts/show-help.sh
   ```

这将显示服务器的使用说明和配置选项。

## 测试

在部署后，建议运行测试以确保服务正常工作：

### 运行所有测试
```bash
# 使用run_tests.py脚本（推荐）
python run_tests.py

# 或者手动设置PYTHONPATH
PYTHONPATH=src python -m pytest
```

### 运行特定测试
```bash
# 运行配置测试
python run_tests.py tests/test_config.py -v

# 运行工具测试
python run_tests.py tests/tools/ -v

# 运行集成测试
python run_tests.py tests/integration/ -v
```

### 测试警告处理
项目已处理以下警告：
- 移除了不支持的`asyncio_fixture_loop_scope` pytest配置项
- 通过过滤忽略系统级Swig相关弃用警告（不影响功能）

## MCP客户端集成

要将arxiv-mcp-server与MCP客户端集成，请在客户端配置文件中添加以下配置：

### Claude Desktop配置示例
```json
{
    "mcpServers": {
        "arxiv-mcp-server": {
            "command": "arxiv-mcp-server",
            "args": [
                "--storage-path",
                "/path/to/paper/storage"
            ]
        }
    }
}
```

### 开发环境配置示例
```json
{
    "mcpServers": {
        "arxiv-mcp-server": {
            "command": "python",
            "args": [
                "-m",
                "arxiv_mcp_server",
                "--storage-path",
                "/path/to/paper/storage"
            ]
        }
    }
}
```

## 常见问题

### Q1: 部署时遇到Python版本不匹配错误
**解决方案**:
1. 使用系统包管理器安装Python 3.11+:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11
   
   # CentOS/RHEL
   sudo yum install python3.11
   
   # macOS (使用Homebrew)
   brew install python@3.11
   ```

2. 使用pyenv管理多版本Python:
   ```bash
   # 安装pyenv
   curl https://pyenv.run | bash
   
   # 安装Python 3.11
   pyenv install 3.11.6
   pyenv local 3.11.6
   ```

3. 验证安装:
   ```bash
   python --version
   ```

### Q2: 服务启动后似乎"卡住"了
这是正常现象。arxiv-mcp-server是一个MCP服务器，通过标准输入/输出与客户端通信，不会在终端显示运行信息。要使用该服务，需要通过支持MCP协议的客户端（如Claude Desktop）进行连接。

### Q3: 如何验证服务是否正常运行
由于MCP服务器的特性，无法直接通过终端查看运行状态。可以通过以下方式验证：

1. 检查进程是否存在:
   ```bash
   ps aux | grep arxiv_mcp_server
   ```

2. 运行测试验证功能:
   ```bash
   python run_tests.py
   ```

3. 通过MCP客户端测试连接

### Q4: 权限问题导致无法写入存储目录
**解决方案**:
1. 确保存储目录存在且有写权限:
   ```bash
   mkdir -p /path/to/paper/storage
   chmod 755 /path/to/paper/storage
   ```

2. 使用当前用户权限运行服务:
   ```bash
   python -m arxiv_mcp_server --storage-path /path/to/paper/storage
   ```

3. 或者使用用户级安装避免权限问题:
   ```bash
   pip install --user -e .
   ```

### Q5: 如何更新服务
```bash
# 系统级部署
cd /path/to/arxiv-mcp-server
git pull origin main
pip install -e .

# 虚拟环境部署
cd /path/to/arxiv-mcp-server
git pull origin main
source .venv/bin/activate
pip install -e .

# uv工具部署
uv tool upgrade arxiv-mcp-server

# Docker部署
./scripts/docker-build.sh
```

### Q6: 如何卸载服务
```bash
# 系统级安装卸载
pip uninstall arxiv-mcp-server

# uv工具卸载
uv tool uninstall arxiv-mcp-server

# Docker容器删除
docker stop arxiv-mcp-server
docker rm arxiv-mcp-server

# 删除存储数据（可选）
rm -rf ~/.arxiv-mcp-server
```