"""
Fusion 360 视图操作工具
"""

import logging
from typing import Any, Dict, List, Optional

from .fusion360_api import get_api


logger = logging.getLogger(__name__)


async def get_view(
    camera_position: Optional[List[float]] = None,
    target_position: Optional[List[float]] = None,
    format: str = "png",
    width: int = 1920,
    height: int = 1080
) -> Dict[str, Any]:
    """获取活动视图的截图"""
    api = get_api()

    data = {
        "action": "get_view",
        "parameters": {
            "camera_position": camera_position,
            "target_position": target_position,
            "format": format,
            "width": width,
            "height": height
        }
    }

    result = await api._request("GET", "/api/view", data)
    logger.info("获取视图截图成功")
    return result
