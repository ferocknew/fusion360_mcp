"""
Fusion 360 零件操作工具
"""

import logging
from typing import Any, Dict, List, Optional

from .fusion360_api import get_api


logger = logging.getLogger(__name__)


async def insert_part_from_library(
    library_name: str,
    part_name: str,
    position: Optional[List[float]] = None
) -> Dict[str, Any]:
    """从零件库中插入零件"""
    api = get_api()

    data = {
        "action": "insert_part",
        "parameters": {
            "library": library_name,
            "part": part_name,
            "position": position or [0, 0, 0]
        }
    }

    result = await api._request("POST", "/api/part", data)
    logger.info(f"插入零件成功: {library_name}/{part_name}")
    return result


async def get_parts_list() -> Dict[str, Any]:
    """获取零件库中的零件列表"""
    api = get_api()

    result = await api._request("GET", "/api/parts")
    logger.info(f"获取零件列表成功，共 {len(result.get('parts', []))} 个零件")
    return result
