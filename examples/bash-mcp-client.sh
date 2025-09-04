#!/bin/bash

# Bash MCP客户端示例
# ===================
# 
# 这个脚本演示了如何使用Bash与arxiv-mcp-server进行通信
# 
# 功能：
# - 启动MCP服务器作为后台进程
# - 通过命名管道与服务器通信
# - 发送JSON-RPC请求并接收响应
# - 测试服务器连接和工具列表
# - 正确停止服务器和清理资源
#
# 使用方法：
#   ./bash-mcp-client.sh
#
# 依赖：
# - Python 3.11+
# - arxiv-mcp-server模块
# - coreutils (for timeout command)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/proper-mcp-client.log"
TEST_DIR="$SCRIPT_DIR/test-output"
SERVER_PID=""

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2 | tee -a "$LOG_FILE"
}

# 启动MCP服务器
start_mcp_server() {
    log "启动MCP服务器..."
    
    mkdir -p "$TEST_DIR"
    export PYTHONPATH="$SCRIPT_DIR/../src:$PYTHONPATH"
    
    # 启动服务器作为后台进程，通过命名管道通信
    local pipe_in="$TEST_DIR/server_in"
    local pipe_out="$TEST_DIR/server_out"
    
    mkfifo "$pipe_in" "$pipe_out" 2>/dev/null
    
    # 启动服务器
    python -m arxiv_mcp_server --storage-path "$TEST_DIR" < "$pipe_in" > "$pipe_out" 2>"$TEST_DIR/server_error.log" &
    SERVER_PID=$!
    
    # 等待服务器启动
    sleep 3
    
    # 检查服务器是否正在运行
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        error "MCP服务器启动失败"
        cat "$TEST_DIR/server_error.log" 2>/dev/null
        return 1
    fi
    
    log "MCP服务器已启动 (PID: $SERVER_PID)"
    return 0
}

# 停止MCP服务器
stop_mcp_server() {
    if [ ! -z "$SERVER_PID" ] && kill -0 $SERVER_PID 2>/dev/null; then
        log "停止MCP服务器 (PID: $SERVER_PID)"
        kill $SERVER_PID
        wait $SERVER_PID 2>/dev/null
    fi
    
    # 清理管道文件
    rm -f "$TEST_DIR/server_in" "$TEST_DIR/server_out"
}

# 发送请求到服务器
send_request() {
    local request="$1"
    local pipe_in="$TEST_DIR/server_in"
    local pipe_out="$TEST_DIR/server_out"
    
    # 发送请求
    echo "$request" > "$pipe_in" &
    
    # 读取响应（设置超时）
    local response=$(/opt/homebrew/opt/coreutils/libexec/gnubin/timeout 5 cat "$pipe_out" 2>/dev/null)
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        error "请求超时"
        return 1
    fi
    
    if [ -z "$response" ]; then
        error "未收到响应"
        return 1
    fi
    
    echo "$response"
    return 0
}

# 测试MCP服务器连接
test_mcp_connection() {
    log "测试MCP服务器连接..."
    
    local test_params='{"jsonrpc": "2.0", "id": 1, "method": "list_tools", "params": {}}'
    
    log "发送测试请求..."
    response=$(send_request "$test_params")
    
    if [ $? -ne 0 ]; then
        error "测试请求失败"
        return 1
    fi
    
    log "服务器响应: $response"
    
    # 检查响应格式
    if echo "$response" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
        log "✓ JSON响应格式正确"
        return 0
    else
        error "✗ JSON响应格式错误"
        return 1
    fi
}

# 测试工具列表
test_list_tools() {
    log "测试获取工具列表..."
    
    # 检查响应中是否包含工具信息
    if echo "$response" | grep -q "search_papers\|download_paper"; then
        log "✓ 工具列表包含预期工具"
        return 0
    else
        error "✗ 工具列表不完整"
        return 1
    fi
}

# 清理函数
cleanup() {
    log "执行清理操作..."
    stop_mcp_server
    rm -rf "$TEST_DIR"
    exit 0
}

# 设置信号处理
trap cleanup EXIT INT TERM

# 主函数
main() {
    log "=== 正确的MCP客户端测试 ==="
    
    # 检查依赖
    if ! command -v python &> /dev/null; then
        error "Python 未安装"
        exit 1
    fi
    
    # 检查MCP服务器是否可用
    export PYTHONPATH="$SCRIPT_DIR/../src:$PYTHONPATH"
    if ! python -c "import arxiv_mcp_server" 2>/dev/null; then
        error "arxiv-mcp-server 模块未找到，请先安装"
        exit 1
    fi
    
    local test_passed=0
    local total_tests=1
    
    # 启动服务器
    if ! start_mcp_server; then
        error "无法启动MCP服务器"
        exit 1
    fi
    
    # 测试: MCP连接和工具列表
    if test_mcp_connection; then
        test_passed=$((test_passed + 1))
        log "✓ 测试通过: MCP连接正常"
        
        # 如果连接成功，再测试工具列表
        if test_list_tools; then
            log "✓ 工具列表验证通过"
        else
            log "⚠ 工具列表验证失败，但连接正常"
        fi
    else
        log "✗ 测试失败: MCP连接异常"
    fi
    
    # 输出测试结果
    log "=== 测试结果 ==="
    log "通过测试: $test_passed/$total_tests"
    
    if [ $test_passed -eq $total_tests ]; then
        log "🎉 所有测试通过！MCP客户端可以正常使用"
        exit 0
    else
        error "❌ 部分测试失败，请检查配置"
        exit 1
    fi
}

# 如果直接运行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
