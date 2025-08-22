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
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
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


async def run_mcp_server() -> None:
    """运行 MCP 服务器"""
    setup_logging("INFO")
    logger = logging.getLogger(__name__)

    logger.info("启动 Fusion360 MCP 服务器 (FastMCP)")

    try:
        # FastMCP 服务器通过 stdio 运行，不需要端口
        # 这里应该调用 FastMCP 的运行方法
        await app.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭 MCP 服务器...")
    except Exception as e:
        logger.error(f"MCP 服务器运行失败: {e}")
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
        # MCP 服务器不需要 host/port 参数，通过 stdio 通信
        asyncio.run(run_mcp_server())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
