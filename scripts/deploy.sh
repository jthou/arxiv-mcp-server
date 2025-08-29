#!/bin/bash
# Arxiv MCP Server 部署脚本

set -euo pipefail

# 配置变量
APP_NAME="arxiv-mcp-server"
VENV_DIR=".venv"
PYTHON_VERSION="3.12"

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# 检查依赖
check_dependencies() {
    log "检查系统依赖..."
    
    # 检查Python版本
    if ! command -v python${PYTHON_VERSION} &> /dev/null; then
        log "警告: Python ${PYTHON_VERSION} 未找到，尝试使用系统默认Python版本"
        if ! python -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)"; then
            log "错误: 需要Python 3.11或更高版本"
            exit 1
        fi
        PYTHON_VERSION=""  # 使用默认Python版本
    fi
    
    # 检查uv是否安装
    if ! command -v uv &> /dev/null; then
        log "警告: uv (Astral) 未安装，将使用pip作为备选"
    fi
    
    # 检查其他必要命令
    for cmd in git curl; do
        if ! command -v $cmd &> /dev/null; then
            log "错误: $cmd 未安装"
            exit 1
        fi
    done
    
    log "所有必要依赖已安装"
}

# 安装依赖
install_dependencies() {
    log "安装项目依赖..."
    
    # 创建虚拟环境
    if [ ! -d "$VENV_DIR" ]; then
        log "创建Python虚拟环境..."
        python${PYTHON_VERSION} -m venv "$VENV_DIR"
    fi
    
    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"
    
    # 使用uv或pip安装依赖
    if command -v uv &> /dev/null; then
        log "使用uv安装依赖..."
        uv pip install -e .
    else
        log "使用pip安装依赖..."
        pip install -e .
    fi
    
    log "项目依赖安装完成"
}

# 启动服务
start_service() {
    log "启动服务..."
    
    # 确保虚拟环境已激活
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        source "$VENV_DIR/bin/activate"
    fi
    
    # 检查服务是否已在运行
    if pgrep -f "arxiv_mcp_server" > /dev/null; then
        log "服务已在运行，先停止现有服务..."
        pkill -f "arxiv_mcp_server"
        sleep 2
    fi
    
    # 启动服务
    log "启动arxiv-mcp-server服务..."
    nohup python -m arxiv_mcp_server > server.log 2>&1 &
    
    # 检查服务是否启动成功
    sleep 2
    if ! pgrep -f "arxiv_mcp_server" > /dev/null; then
        log "错误: 服务启动失败，请检查server.log"
        exit 1
    fi
    
    log "服务已成功启动 (PID: $(pgrep -f "arxiv_mcp_server"))"
}

# Docker部署选项
docker_deploy() {
    log "使用Docker部署..."
    if ! command -v docker &> /dev/null; then
        log "错误: Docker未安装"
        exit 1
    fi
    
    ./scripts/docker-build.sh
}

# 主函数
main() {
    local use_docker=false
    local dry_run=false
    
    # 解析参数
    while getopts "dt" opt; do
        case $opt in
            d) use_docker=true ;;
            t) dry_run=true ;;
            *) ;;
        esac
    done
    
    if [ "$dry_run" = true ]; then
        log "Dry run模式: 只检查不执行"
        check_dependencies
        log "Dry run完成"
        return 0
    fi
    
    log "开始部署 $APP_NAME"
    
    if [ "$use_docker" = true ]; then
        docker_deploy
    else
        check_dependencies
        install_dependencies
        start_service
    fi
    
    log "部署完成"
}

main "$@"