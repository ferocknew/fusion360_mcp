"""
Fusion 360 代码执行工具
"""

import logging
from typing import Any, Dict, Optional

from .fusion360_api import get_api


logger = logging.getLogger(__name__)


async def execute_code(code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """在 Fusion 360 中执行任意 Python 代码"""
    api = get_api()

    data = {
        "action": "execute_code",
        "parameters": {
            "code": code,
            "context": context or {}
        }
    }

    result = await api._request("POST", "/api/execute", data)
    logger.info("代码执行成功")
    return result
