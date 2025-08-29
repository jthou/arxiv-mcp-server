#!/bin/bash
# Arxiv MCP Server Docker构建脚本

set -euo pipefail

# 配置变量
IMAGE_NAME="arxiv-mcp-server"
TAG="latest"

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# 构建Docker镜像
build_image() {
    log "构建Docker镜像..."
    docker build -t "$IMAGE_NAME:$TAG" .
}

# 运行Docker容器
run_container() {
    log "启动Docker容器..."
    docker run -d \
        --name "$IMAGE_NAME" \
        -p 8000:8000 \
        -v ./data:/app/data \
        "$IMAGE_NAME:$TAG"
}

# 主函数
main() {
    build_image
    run_container
    log "Docker容器已启动"
    log "使用 'docker logs -f $IMAGE_NAME' 查看日志"
}

main "$@"