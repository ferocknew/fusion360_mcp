"""
Fusion 360 API 基础客户端
"""

import logging
from typing import Any, Dict, Optional

import httpx

from .config import get_settings


logger = logging.getLogger(__name__)


class Fusion360API:
    """Fusion 360 API 客户端"""

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.base_url = "http://localhost:9000"  # Fusion 360 插件服务地址

    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.settings.fusion360_api_timeout,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
        return self.client

    async def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送请求到 Fusion 360 插件"""
        client = await self._get_client()
        url = f"{self.base_url}{endpoint}"

        try:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"请求 Fusion 360 API 失败: {e}")
            raise Exception(f"无法连接到 Fusion 360: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Fusion 360 API 返回错误: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Fusion 360 操作失败: {e.response.text}")

    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()


# 全局 API 实例
_api_instance: Optional[Fusion360API] = None


def get_api() -> Fusion360API:
    """获取 Fusion 360 API 实例"""
    global _api_instance
    if _api_instance is None:
        _api_instance = Fusion360API()
    return _api_instance


# 辅助工具函数
async def validate_fusion360_connection() -> bool:
    """验证与 Fusion 360 的连接"""
    try:
        api = get_api()
        await api._request("GET", "/api/health")
        return True
    except Exception as e:
        logger.warning(f"Fusion 360 连接验证失败: {e}")
        return False


async def get_fusion360_status() -> Dict[str, Any]:
    """获取 Fusion 360 状态信息"""
    try:
        api = get_api()
        result = await api._request("GET", "/api/status")
        return result
    except Exception as e:
        logger.error(f"获取 Fusion 360 状态失败: {e}")
        return {"status": "disconnected", "error": str(e)}
