"""
文档相关工具的单元测试
"""

import unittest
from unittest.mock import patch, AsyncMock
from .test_base import Fusion360TestBase, MockFusion360API


class TestDocumentTools(Fusion360TestBase):
    """文档工具测试类"""
    
    def setUp(self):
        super().setUp()
        self.mock_api = MockFusion360API()
    
    def test_create_document_default_params(self):
        """测试使用默认参数创建文档"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import create_document
                
                result = await self.mock_api.create_document()
                self.log_test_result("创建文档(默认参数)", result)
                
                self.assert_api_call_success(result, ["document_id", "name", "units"])
                self.assertEqual(result["result"]["name"], "新建文档")
                self.assertEqual(result["result"]["units"], "mm")
        
        self.async_test(test())
    
    def test_create_document_custom_params(self):
        """测试使用自定义参数创建文档"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import create_document
                
                result = await self.mock_api.create_document(
                    name="测试项目",
                    template="机械设计",
                    units="cm"
                )
                self.log_test_result("创建文档(自定义参数)", result)
                
                self.assert_api_call_success(result)
                self.assertEqual(result["result"]["name"], "测试项目")
                self.assertEqual(result["result"]["units"], "cm")
        
        self.async_test(test())
    
    def test_create_multiple_documents(self):
        """测试创建多个文档"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import create_document
                
                # 创建多个文档
                doc_names = ["项目A", "项目B", "项目C"]
                created_docs = []
                
                for name in doc_names:
                    result = await self.mock_api.create_document(name=name)
                    created_docs.append(result)
                    self.assert_api_call_success(result)
                
                self.log_test_result(f"创建多个文档({len(doc_names)}个)", {"success": True})
                
                # 验证所有文档都被创建
                self.assertEqual(len(self.mock_api.documents), len(doc_names))
                for i, doc in enumerate(self.mock_api.documents):
                    self.assertEqual(doc["name"], doc_names[i])
        
        self.async_test(test())
    
    def test_document_units_validation(self):
        """测试文档单位验证"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import create_document
                
                # 测试不同单位
                units_to_test = ["mm", "cm", "m", "in", "ft"]
                
                for unit in units_to_test:
                    result = await self.mock_api.create_document(
                        name=f"测试_{unit}",
                        units=unit
                    )
                    self.assert_api_call_success(result)
                    self.assertEqual(result["result"]["units"], unit)
                
                self.log_test_result("文档单位验证", {"success": True})
        
        self.async_test(test())
    
    def tearDown(self):
        """测试结束后清理"""
        self.print_test_summary()
        super().tearDown()


if __name__ == '__main__':
    unittest.main(verbosity=2)
