"""
配置管理模块
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """应用配置"""

    # 服务器配置
    host: str = Field(default="localhost", description="服务器主机地址")
    port: int = Field(default=8000, description="服务器端口")
    log_level: str = Field(default="INFO", description="日志级别")

    # Fusion 360 配置
    fusion360_api_timeout: int = Field(default=30, description="Fusion 360 API 超时时间（秒）")
    fusion360_max_retry: int = Field(default=3, description="Fusion 360 API 最大重试次数")

    # MCP 配置
    mcp_server_name: str = Field(default="fusion360_mcp", description="MCP 服务器名称")
    mcp_server_version: str = Field(default="0.1.0", description="MCP 服务器版本")

    # 安全配置
    cors_origins: list[str] = Field(default=["*"], description="CORS 允许的源")
    max_request_size: int = Field(default=10 * 1024 * 1024, description="最大请求大小（字节）")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# 全局设置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局设置实例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """重新加载设置"""
    global _settings
    _settings = Settings()
    return _settings
