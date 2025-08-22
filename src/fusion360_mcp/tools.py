"""
Fusion 360 工具和 API 接口实现
"""

import asyncio
import base64
import json
import logging
from typing import Any, Dict, List, Optional

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


# 工具函数实现
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


async def get_parts_list() -> Dict[str, Any]:
    """获取零件库中的零件列表"""
    api = get_api()
    
    result = await api._request("GET", "/api/parts")
    logger.info(f"获取零件列表成功，共 {len(result.get('parts', []))} 个零件")
    return result


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
