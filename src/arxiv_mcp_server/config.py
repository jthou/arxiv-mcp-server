"""Configuration settings for the arXiv MCP stdio server."""

import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

# 全局配置实例
_settings = None

# 解析命令行参数以获取存储路径
def get_storage_path_from_args():
    """从命令行参数或环境变量获取存储路径"""
    # 首先检查环境变量
    storage_path = os.environ.get("ARXIV_STORAGE_PATH")
    
    # 如果环境变量不存在，检查命令行参数
    if not storage_path:
        try:
            # 查找 --storage-path 参数
            for i, arg in enumerate(sys.argv):
                if arg == "--storage-path" and i + 1 < len(sys.argv):
                    storage_path = sys.argv[i + 1]
                    break
                # 也支持 --storage-path= 参数
                elif arg.startswith("--storage-path="):
                    storage_path = arg.split("=", 1)[1]
                    break
        except Exception:
            pass  # 如果解析失败，使用默认值
    
    return storage_path

def get_settings():
    """获取全局配置实例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reset_settings():
    """重置全局配置实例，用于测试"""
    global _settings
    _settings = None

class Settings(BaseSettings):
    """Stdio server configuration settings."""

    APP_NAME: str = "arxiv-mcp-server"
    APP_VERSION: str = "0.3.1"
    MAX_RESULTS: int = 50
    BATCH_SIZE: int = 20
    REQUEST_TIMEOUT: int = 60
    model_config = SettingsConfigDict(extra="allow")

    @property
    def STORAGE_PATH(self) -> Path:
        """Get the resolved storage path and ensure it exists."""
        # 获取存储路径（从命令行参数或环境变量）
        storage_path = get_storage_path_from_args()
        
        # 如果没有指定存储路径，使用默认路径
        if storage_path:
            path = Path(storage_path)
        else:
            path = Path.home() / ".arxiv-mcp-server" / "papers"
            
        # 确保存储路径存在
        path.mkdir(parents=True, exist_ok=True)
        return path

__all__ = ["Settings", "get_settings", "reset_settings"]