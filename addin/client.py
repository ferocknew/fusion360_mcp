"""
MCP 客户端模块，用于 Fusion 360 插件与 MCP 服务器通信
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, Optional, List
import logging


class MCPClient:
    """MCP 客户端，处理与 FastMCP 服务器的通信"""

    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url.rstrip('/')
        self.timeout = 30
        self.logger = logging.getLogger(__name__)

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送 HTTP 请求到 MCP 服务器"""
        url = f"{self.server_url}{endpoint}"

        # 准备请求数据
        request_data = None
        headers = {'Content-Type': 'application/json'}

        if data is not None:
            request_data = json.dumps(data).encode('utf-8')

        # 创建请求
        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_text = response.read().decode('utf-8')
                return json.loads(response_text)
        except urllib.error.URLError as e:
            self.logger.error(f"网络请求失败: {e}")
            raise Exception(f"无法连接到 MCP 服务器: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 解析失败: {e}")
            raise Exception(f"服务器响应格式错误: {e}")
        except Exception as e:
            self.logger.error(f"请求处理失败: {e}")
            raise Exception(f"请求失败: {e}")

    def ping(self) -> bool:
        """检查服务器连接"""
        try:
            response = self._request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception:
            return False

    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return self._request("GET", "/")

    def create_document(self, name: str = None, template: str = None, units: str = "mm") -> Dict[str, Any]:
        """创建新文档"""
        data = {
            "name": name,
            "template": template,
            "units": units
        }
        return self._request("POST", "/api/tools/create_document", data)

    def create_object(self, object_type: str, parameters: Dict[str, Any],
                     position: List[float] = None, rotation: List[float] = None) -> Dict[str, Any]:
        """创建新对象"""
        data = {
            "object_type": object_type,
            "parameters": parameters,
            "position": position or [0, 0, 0],
            "rotation": rotation or [0, 0, 0]
        }
        return self._request("POST", "/api/tools/create_object", data)

    def edit_object(self, object_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """编辑对象"""
        return self._request("POST", "/api/tools/edit_object", {
            "object_id": object_id,
            "parameters": parameters
        })

    def delete_object(self, object_id: str) -> Dict[str, Any]:
        """删除对象"""
        return self._request("POST", "/api/tools/delete_object", {"object_id": object_id})

    def execute_code(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行代码"""
        data = {
            "code": code,
            "context": context or {}
        }
        return self._request("POST", "/api/tools/execute_code", data)

    def insert_part_from_library(self, library_name: str, part_name: str,
                                position: List[float] = None) -> Dict[str, Any]:
        """从库中插入零件"""
        data = {
            "library_name": library_name,
            "part_name": part_name,
            "position": position or [0, 0, 0]
        }
        return self._request("POST", "/api/tools/insert_part_from_library", data)

    def get_view(self, camera_position: List[float] = None, target_position: List[float] = None,
                format: str = "png", width: int = 1920, height: int = 1080) -> Dict[str, Any]:
        """获取视图截图"""
        data = {
            "camera_position": camera_position,
            "target_position": target_position,
            "format": format,
            "width": width,
            "height": height
        }
        return self._request("POST", "/api/tools/get_view", data)

    def get_objects(self) -> Dict[str, Any]:
        """获取所有对象"""
        return self._request("POST", "/api/tools/get_objects", {})

    def get_object(self, object_id: str) -> Dict[str, Any]:
        """获取特定对象"""
        return self._request("POST", "/api/tools/get_object", {"object_id": object_id})

    def get_parts_list(self) -> Dict[str, Any]:
        """获取零件列表"""
        return self._request("POST", "/api/tools/get_parts_list", {})
