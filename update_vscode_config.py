#!/usr/bin/env python3
"""
更新VS Code的MCP配置文件，添加arxiv-mcp-server配置
"""

import json
import os
import shutil

def update_vscode_mcp_config():
    """更新VS Code的MCP配置文件"""
    # VS Code用户目录路径
    vscode_user_dir = "/Users/jintinghou/Library/Application Support/Code/User"
    mcp_config_path = os.path.join(vscode_user_dir, "mcp.json")
    
    # 检查配置文件是否存在
    if not os.path.exists(mcp_config_path):
        print("错误: VS Code MCP配置文件不存在")
        return False
    
    # 备份当前配置文件
    backup_path = mcp_config_path + ".backup3"
    shutil.copy2(mcp_config_path, backup_path)
    print(f"已备份配置文件到: {backup_path}")
    
    # 读取当前配置
    with open(mcp_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 添加arxiv-mcp-server配置
    arxiv_config = {
        "type": "stdio",
        "command": "python",
        "args": [
            "-m",
            "arxiv_mcp_server",
            "--storage-path",
            "/Users/jintinghou/Documents/arxiv-papers"
        ],
        "gallery": True
    }
    
    # 更新配置
    config["servers"]["arxiv-mcp-server"] = arxiv_config
    
    # 写入更新后的配置
    with open(mcp_config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("已成功更新VS Code MCP配置文件")
    print("添加了arxiv-mcp-server配置:")
    print(json.dumps(arxiv_config, indent=4, ensure_ascii=False))
    
    return True

if __name__ == "__main__":
    try:
        success = update_vscode_mcp_config()
        if success:
            print("\n配置更新成功！")
            print("现在您可以在VS Code中使用arxiv-mcp-server了。")
        else:
            print("\n配置更新失败！")
    except Exception as e:
        print(f"更新配置时出现错误: {e}")