"""
测试基类和公共测试工具
"""

import unittest
import asyncio
import logging
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, patch

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
    """Fusion 360 测试基类"""
    
    def setUp(self):
        super().setUp()
        self.mock_api = None
        self.test_results = []
    
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
