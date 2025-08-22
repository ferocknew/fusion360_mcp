"""
Fusion 360 工具和 API 接口 - 统一导入入口
"""

# 从各个模块导入功能
from .document_tools import create_document
from .object_tools import (
    create_object, edit_object, delete_object, get_objects, get_object,
    create_primitive, OBJECT_TEMPLATES
)
from .view_tools import get_view
from .part_tools import insert_part_from_library, get_parts_list
from .execute_tools import execute_code
from .fusion360_api import (
    Fusion360API, get_api, validate_fusion360_connection, get_fusion360_status
)

# 导出所有公共接口
__all__ = [
    # 文档操作
    "create_document",

    # 对象操作
    "create_object",
    "edit_object",
    "delete_object",
    "get_objects",
    "get_object",
    "create_primitive",
    "OBJECT_TEMPLATES",

    # 视图操作
    "get_view",

    # 零件操作
    "insert_part_from_library",
    "get_parts_list",

    # 代码执行
    "execute_code",

    # API基础
    "Fusion360API",
    "get_api",
    "validate_fusion360_connection",
    "get_fusion360_status",
]
