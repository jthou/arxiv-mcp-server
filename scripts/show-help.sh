#!/bin/bash
# Arxiv MCP Server 帮助信息显示脚本

set -euo pipefail

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# 检查是否在项目目录中
if [ ! -f "src/arxiv_mcp_server/server.py" ]; then
    log "错误: 请在项目根目录中运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ -z "${VIRTUAL_ENV:-}" ]; then
    if [ -d ".venv" ]; then
        log "激活虚拟环境..."
        source .venv/bin/activate
    else
        log "警告: 未检测到虚拟环境，使用系统Python"
    fi
fi

# 显示帮助信息
log "显示 arxiv-mcp-server 帮助信息..."
PYTHONPATH=src python -m arxiv_mcp_server --help