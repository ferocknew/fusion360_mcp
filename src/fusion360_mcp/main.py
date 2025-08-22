#!/usr/bin/env python3
"""
Fusion360 MCP 服务器入口点
"""

import argparse
import asyncio
import logging
import sys
from typing import Optional

import uvicorn
from fastmcp import FastMCP

from .server import app
from .config import get_settings
from .help import show_full_help, show_quick_help


def setup_logging(level: str = "INFO") -> None:
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Fusion360 MCP 服务器 - 基于 FastMCP 和 Fusion 360 API 的语义化建模系统"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="服务器绑定的主机地址 (默认: localhost)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器绑定的端口号 (默认: 8000)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用自动重载 (开发模式)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"fusion360-mcp 0.1.0"
    )

    parser.add_argument(
        "--help-tools",
        action="store_true",
        help="显示可用的 Fusion 360 工具列表"
    )

    return parser


async def start_server(
    host: str = "localhost",
    port: int = 8000,
    log_level: str = "INFO",
    reload: bool = False
) -> None:
    """启动 MCP 服务器"""
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"启动 Fusion360 MCP 服务器在 {host}:{port}")
    logger.info(f"日志级别: {log_level}")

    # 配置 uvicorn
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level=log_level.lower(),
        reload=reload,
        access_log=True,
    )

    server = uvicorn.Server(config)

    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)


def main() -> None:
    """主入口函数"""
    parser = create_argument_parser()
    args = parser.parse_args()

    # 处理工具帮助
    if args.help_tools:
        show_full_help()
        return

    try:
        asyncio.run(start_server(
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload,
        ))
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
