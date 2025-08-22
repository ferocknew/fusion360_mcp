"""
Fusion 360 对象操作工具
"""

import logging
from typing import Any, Dict, List, Optional

from .fusion360_api import get_api


logger = logging.getLogger(__name__)


async def create_object(
    object_type: str,
    parameters: Dict[str, Any],
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None
) -> Dict[str, Any]:
    """在 Fusion 360 中创建新对象"""
    api = get_api()

    data = {
        "action": "create_object",
        "parameters": {
            "type": object_type,
            "parameters": parameters,
            "position": position or [0, 0, 0],
            "rotation": rotation or [0, 0, 0]
        }
    }

    result = await api._request("POST", "/api/object", data)
    logger.info(f"创建对象成功: {object_type}")
    return result


async def edit_object(object_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """在 Fusion 360 中编辑对象"""
    api = get_api()

    data = {
        "action": "edit_object",
        "parameters": {
            "object_id": object_id,
            "parameters": parameters
        }
    }

    result = await api._request("PUT", f"/api/object/{object_id}", data)
    logger.info(f"编辑对象成功: {object_id}")
    return result


async def delete_object(object_id: str) -> Dict[str, Any]:
    """在 Fusion 360 中删除对象"""
    api = get_api()

    result = await api._request("DELETE", f"/api/object/{object_id}")
    logger.info(f"删除对象成功: {object_id}")
    return result


async def get_objects() -> Dict[str, Any]:
    """获取文档中的所有对象"""
    api = get_api()

    result = await api._request("GET", "/api/objects")
    logger.info(f"获取对象列表成功，共 {len(result.get('objects', []))} 个对象")
    return result


async def get_object(object_id: str) -> Dict[str, Any]:
    """获取文档中的特定对象"""
    api = get_api()

    result = await api._request("GET", f"/api/object/{object_id}")
    logger.info(f"获取对象成功: {object_id}")
    return result


# 预定义的对象创建模板
OBJECT_TEMPLATES = {
    "cylinder": {
        "type": "extrude",
        "base_feature": "circle",
        "parameters": ["radius", "height"]
    },
    "box": {
        "type": "extrude",
        "base_feature": "rectangle",
        "parameters": ["length", "width", "height"]
    },
    "sphere": {
        "type": "revolve",
        "base_feature": "semicircle",
        "parameters": ["radius"]
    },
    "cone": {
        "type": "extrude",
        "base_feature": "circle",
        "parameters": ["base_radius", "top_radius", "height"]
    }
}


async def create_primitive(
    primitive_type: str,
    **kwargs
) -> Dict[str, Any]:
    """创建基本几何体的便捷函数"""
    if primitive_type not in OBJECT_TEMPLATES:
        raise ValueError(f"不支持的基本几何体类型: {primitive_type}")

    template = OBJECT_TEMPLATES[primitive_type]

    # 验证必需参数
    missing_params = []
    for param in template["parameters"]:
        if param not in kwargs:
            missing_params.append(param)

    if missing_params:
        raise ValueError(f"缺少必需参数: {missing_params}")

    return await create_object(
        object_type=template["type"],
        parameters={
            "base_feature": template["base_feature"],
            **kwargs
        }
    )
