"""
Fusion360 LLM 建模助手

一个基于 FastMCP 和 Fusion 360 API 的语义化建模系统，让大语言模型可以通过自然语言进行 3D 建模操作。
"""

__version__ = "0.1.0"
__author__ = "Fusion360 MCP Team"
__email__ = ""
__description__ = "一个基于 FastMCP 和 Fusion 360 API 的语义化建模系统"

from .server import app
from .tools import (
    create_document,
    create_object,
    edit_object,
    delete_object,
    execute_code,
    insert_part_from_library,
    get_view,
    get_objects,
    get_object,
    get_parts_list,
)

__all__ = [
    "app",
    "create_document",
    "create_object", 
    "edit_object",
    "delete_object",
    "execute_code",
    "insert_part_from_library",
    "get_view",
    "get_objects",
    "get_object",
    "get_parts_list",
]
