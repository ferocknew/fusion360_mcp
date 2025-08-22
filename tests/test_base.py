"""
测试基类和公共测试工具
"""

import unittest
import asyncio
import logging
import time
import sys
import os
from typing import Dict, Any, Optional

# 添加项目根目录到路径，以便导入 src 代码
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入真实的代码
from src.fusion360_mcp import tools
from addin.client import MCPClient

# 设置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncTestCase(unittest.TestCase):
    """异步测试基类"""

    def setUp(self):
        """测试初始化"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """测试清理"""
        self.loop.close()

    def async_test(self, coro):
        """运行异步测试"""
        return self.loop.run_until_complete(coro)


class Fusion360TestBase(AsyncTestCase):
    """Fusion 360 测试基类 - 使用真实的 src 代码和 MCPClient"""

    def setUp(self):
        super().setUp()
        self.fusion360_url = "http://localhost:9000"  # Fusion 360 插件服务地址
        self.mcp_server_url = "http://localhost:8000"  # MCP 服务器地址
        self.test_results = []

        # 创建 MCPClient 实例，用于与 Fusion 360 插件通信
        self.mcp_client = MCPClient(self.mcp_server_url)

        # 直接使用 src 中的工具模块
        self.tools = tools

    def get_mcp_client(self) -> MCPClient:
        """获取 MCP 客户端"""
        return self.mcp_client

    def create_mock_api_response(self, success: bool = True, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """创建模拟 API 响应"""
        return {
            "success": success,
            "result": data or {},
            "error": None if success else "测试错误"
        }

    def assert_api_call_success(self, result: Dict[str, Any], expected_keys: list = None):
        """断言 API 调用成功"""
        self.assertTrue(result.get("success"), f"API 调用失败: {result.get('error')}")
        if expected_keys:
            for key in expected_keys:
                self.assertIn(key, result.get("result", {}), f"缺少期望的键: {key}")

    def assert_api_call_failure(self, result: Dict[str, Any], expected_error: str = None):
        """断言 API 调用失败"""
        self.assertFalse(result.get("success"), "期望 API 调用失败但实际成功")
        if expected_error:
            self.assertIn(expected_error, str(result.get("error", "")))

    def log_test_result(self, test_name: str, result: Dict[str, Any]):
        """记录测试结果"""
        status = "✅ 成功" if result.get("success") else "❌ 失败"
        logger.info(f"{test_name}: {status}")
        self.test_results.append({
            "test": test_name,
            "success": result.get("success"),
            "result": result
        })

    def check_fusion360_connection(self) -> bool:
        """检查 Fusion 360 插件连接"""
        try:
            # 使用 MCPClient 检查连接
            return self.mcp_client.ping()
        except Exception as e:
            logger.warning(f"Fusion 360 连接检查失败: {e}")
            return False

    def check_mcp_server_connection(self) -> bool:
        """检查 MCP 服务器连接"""
        try:
            # 获取服务器信息来验证连接
            server_info = self.mcp_client.get_server_info()
            return server_info is not None
        except Exception as e:
            logger.warning(f"MCP 服务器连接检查失败: {e}")
            return False

    async def call_fusion360_api(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """直接调用 Fusion 360 插件 API"""
        try:
            client = await self.get_client()
            url = f"{self.fusion360_url}{endpoint}"

            if method.upper() == "GET":
                response = await client.get(url)
            elif method.upper() == "POST":
                response = await client.post(url, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.RequestError as e:
            logger.error(f"请求 Fusion 360 API 失败: {e}")
            return {"success": False, "error": f"网络错误: {e}"}
        except httpx.HTTPStatusError as e:
            logger.error(f"Fusion 360 API 返回错误: {e.response.status_code}")
            return {"success": False, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            logger.error(f"调用 Fusion 360 API 异常: {e}")
            return {"success": False, "error": str(e)}

    async def call_real_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """直接调用 src 中的真实工具函数"""
        try:
            # 根据工具名称调用对应的函数
            if tool_name == "create_document":
                result = await self.tools.create_document(
                    name=kwargs.get("name"),
                    template=kwargs.get("template"),
                    units=kwargs.get("units", "mm")
                )
            elif tool_name == "create_object":
                result = await self.tools.create_object(
                    object_type=kwargs.get("object_type"),
                    parameters=kwargs.get("parameters", {}),
                    position=kwargs.get("position"),
                    rotation=kwargs.get("rotation")
                )
            elif tool_name == "edit_object":
                result = await self.tools.edit_object(
                    kwargs.get("object_id"),
                    kwargs.get("parameters", {})
                )
            elif tool_name == "delete_object":
                result = await self.tools.delete_object(kwargs.get("object_id"))
            elif tool_name == "execute_code":
                result = await self.tools.execute_code(
                    kwargs.get("code"),
                    kwargs.get("context")
                )
            elif tool_name == "insert_part_from_library":
                result = await self.tools.insert_part_from_library(
                    kwargs.get("library_name"),
                    kwargs.get("part_name"),
                    kwargs.get("position")
                )
            elif tool_name == "get_view":
                result = await self.tools.get_view(
                    camera_position=kwargs.get("camera_position"),
                    target_position=kwargs.get("target_position"),
                    format=kwargs.get("format", "png"),
                    width=kwargs.get("width", 1920),
                    height=kwargs.get("height", 1080)
                )
            elif tool_name == "get_objects":
                result = await self.tools.get_objects()
            elif tool_name == "get_object":
                result = await self.tools.get_object(kwargs.get("object_id"))
            elif tool_name == "get_parts_list":
                result = await self.tools.get_parts_list()
            else:
                return {"success": False, "error": f"未知的工具: {tool_name}"}

            return result

        except Exception as e:
            logger.error(f"调用真实工具 {tool_name} 失败: {e}")
            return {"success": False, "error": str(e)}

    def call_mcp_client_method(self, method_name: str, **kwargs) -> Dict[str, Any]:
        """调用 MCPClient 的方法"""
        try:
            if method_name == "create_document":
                return self.mcp_client.create_document(
                    name=kwargs.get("name"),
                    template=kwargs.get("template"),
                    units=kwargs.get("units", "mm")
                )
            elif method_name == "create_object":
                return self.mcp_client.create_object(
                    object_type=kwargs.get("object_type"),
                    parameters=kwargs.get("parameters", {}),
                    position=kwargs.get("position"),
                    rotation=kwargs.get("rotation")
                )
            elif method_name == "edit_object":
                return self.mcp_client.edit_object(
                    kwargs.get("object_id"),
                    kwargs.get("parameters", {})
                )
            elif method_name == "delete_object":
                return self.mcp_client.delete_object(kwargs.get("object_id"))
            elif method_name == "execute_code":
                return self.mcp_client.execute_code(
                    kwargs.get("code"),
                    kwargs.get("context")
                )
            elif method_name == "insert_part_from_library":
                return self.mcp_client.insert_part_from_library(
                    kwargs.get("library_name"),
                    kwargs.get("part_name"),
                    kwargs.get("position")
                )
            elif method_name == "get_view":
                return self.mcp_client.get_view(
                    camera_position=kwargs.get("camera_position"),
                    target_position=kwargs.get("target_position"),
                    format=kwargs.get("format", "png"),
                    width=kwargs.get("width", 1920),
                    height=kwargs.get("height", 1080)
                )
            elif method_name == "get_objects":
                return self.mcp_client.get_objects()
            elif method_name == "get_object":
                return self.mcp_client.get_object(kwargs.get("object_id"))
            elif method_name == "get_parts_list":
                return self.mcp_client.get_parts_list()
            else:
                return {"success": False, "error": f"未知的 MCPClient 方法: {method_name}"}

        except Exception as e:
            logger.error(f"调用 MCPClient 方法 {method_name} 失败: {e}")
            return {"success": False, "error": str(e)}

    def print_test_summary(self):
        """打印测试摘要"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed

        logger.info("=" * 50)
        logger.info(f"测试摘要: 总计 {total}, 通过 {passed}, 失败 {failed}")

        if failed > 0:
            logger.info("失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  ❌ {result['test']}: {result['result'].get('error')}")

    def tearDown(self):
        """测试清理"""
        # 这里可以添加其他清理逻辑
        super().tearDown()


class MockFusion360API:
    """模拟 Fusion 360 API"""

    def __init__(self):
        self.documents = []
        self.objects = []
        self.parts = [
            {"library": "标准件", "name": "螺栓M6x20", "category": "紧固件"},
            {"library": "标准件", "name": "螺母M6", "category": "紧固件"},
            {"library": "标准件", "name": "垫圈6", "category": "紧固件"}
        ]
        self.call_history = []

    async def create_document(self, name: str = None, template: str = None, units: str = "mm") -> Dict[str, Any]:
        """模拟创建文档"""
        self.call_history.append(("create_document", {"name": name, "template": template, "units": units}))

        doc_id = f"doc_{len(self.documents) + 1}"
        document = {
            "id": doc_id,
            "name": name or "新建文档",
            "template": template,
            "units": units
        }
        self.documents.append(document)

        return {
            "success": True,
            "result": {
                "document_id": doc_id,
                "name": document["name"],
                "units": units
            }
        }

    async def create_object(self, object_type: str, parameters: Dict[str, Any],
                          position: list = None, rotation: list = None) -> Dict[str, Any]:
        """模拟创建对象"""
        self.call_history.append(("create_object", {
            "object_type": object_type,
            "parameters": parameters,
            "position": position,
            "rotation": rotation
        }))

        obj_id = f"obj_{len(self.objects) + 1}"
        obj = {
            "id": obj_id,
            "type": object_type,
            "parameters": parameters,
            "position": position or [0, 0, 0],
            "rotation": rotation or [0, 0, 0]
        }
        self.objects.append(obj)

        return {
            "success": True,
            "result": {
                "object_id": obj_id,
                "type": object_type,
                "parameters": parameters
            }
        }

    async def get_objects(self) -> Dict[str, Any]:
        """模拟获取对象列表"""
        self.call_history.append(("get_objects", {}))

        return {
            "success": True,
            "result": {
                "objects": [
                    {
                        "id": obj["id"],
                        "name": f"对象_{obj['id']}",
                        "type": obj["type"],
                        "visible": True
                    }
                    for obj in self.objects
                ]
            }
        }

    async def get_object(self, object_id: str) -> Dict[str, Any]:
        """模拟获取特定对象"""
        self.call_history.append(("get_object", {"object_id": object_id}))

        obj = next((o for o in self.objects if o["id"] == object_id), None)
        if not obj:
            return {
                "success": False,
                "error": f"对象 {object_id} 不存在"
            }

        return {
            "success": True,
            "result": {
                "object": {
                    "id": obj["id"],
                    "name": f"对象_{obj['id']}",
                    "type": obj["type"],
                    "parameters": obj["parameters"]
                }
            }
        }

    async def delete_object(self, object_id: str) -> Dict[str, Any]:
        """模拟删除对象"""
        self.call_history.append(("delete_object", {"object_id": object_id}))

        obj_index = next((i for i, o in enumerate(self.objects) if o["id"] == object_id), None)
        if obj_index is None:
            return {
                "success": False,
                "error": f"对象 {object_id} 不存在"
            }

        deleted_obj = self.objects.pop(obj_index)
        return {
            "success": True,
            "result": {
                "deleted_object_id": object_id,
                "message": f"对象 {object_id} 已删除"
            }
        }

    async def get_parts_list(self) -> Dict[str, Any]:
        """模拟获取零件列表"""
        self.call_history.append(("get_parts_list", {}))

        return {
            "success": True,
            "result": {
                "parts": self.parts
            }
        }

    def reset(self):
        """重置模拟 API 状态"""
        self.documents.clear()
        self.objects.clear()
        self.call_history.clear()
