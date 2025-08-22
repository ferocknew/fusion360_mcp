"""
Fusion 360 文档操作工具
"""

import logging
from typing import Any, Dict, Optional

from .fusion360_api import get_api


logger = logging.getLogger(__name__)


async def create_document(
    name: Optional[str] = None,
    template: Optional[str] = None,
    units: str = "mm"
) -> Dict[str, Any]:
    """在 Fusion 360 中创建新文档"""
    api = get_api()

    data = {
        "action": "create_document",
        "parameters": {
            "name": name or "新建文档",
            "template": template,
            "units": units
        }
    }

    result = await api._request("POST", "/api/document", data)
    logger.info(f"创建文档成功: {result}")
    return result
