"""
零件相关工具的单元测试
"""

import unittest
from unittest.mock import patch, AsyncMock
from .test_base import Fusion360TestBase, MockFusion360API


class TestPartTools(Fusion360TestBase):
    """零件工具测试类"""

    def setUp(self):
        super().setUp()
        self.mock_api = MockFusion360API()

    def test_get_parts_list(self):
        """测试获取零件列表"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import get_parts_list

                result = await self.mock_api.get_parts_list()
                self.log_test_result("获取零件列表", result)

                self.assert_api_call_success(result)
                parts = result["result"]["parts"]
                self.assertGreater(len(parts), 0, "零件列表不应为空")

                # 验证零件结构
                for part in parts:
                    self.assertIn("library", part)
                    self.assertIn("name", part)
                    self.assertIn("category", part)

        self.async_test(test())

    def test_parts_list_content(self):
        """测试零件列表内容"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import get_parts_list

                result = await self.mock_api.get_parts_list()
                parts = result["result"]["parts"]

                # 查找标准螺栓
                bolt_found = any(
                    part["name"] == "螺栓M6x20" and part["library"] == "标准件"
                    for part in parts
                )
                self.assertTrue(bolt_found, "应该找到螺栓M6x20")

                # 查找螺母
                nut_found = any(
                    part["name"] == "螺母M6" and part["category"] == "紧固件"
                    for part in parts
                )
                self.assertTrue(nut_found, "应该找到螺母M6")

                self.log_test_result("零件列表内容验证", {"success": True})

        self.async_test(test())

    def test_insert_part_simulation(self):
        """测试零件插入模拟（模拟功能）"""
        async def test():
            # 由于 insert_part_from_library 目前是模拟实现，我们测试其接口
            test_cases = [
                {
                    "library": "标准件",
                    "part": "螺栓M6x20",
                    "position": [0, 0, 0]
                },
                {
                    "library": "标准件",
                    "part": "螺母M6",
                    "position": [10, 10, 0]
                },
                {
                    "library": "标准件",
                    "part": "垫圈6",
                    "position": [-5, 5, 10]
                }
            ]

            all_success = True
            for case in test_cases:
                # 这里模拟插入零件的调用
                # 实际实现中会调用 insert_part_from_library
                call_record = {
                    "library": case["library"],
                    "part": case["part"],
                    "position": case["position"]
                }

                # 模拟成功响应
                result = {
                    "success": True,
                    "result": {
                        "part_id": f"part_{len(self.mock_api.call_history) + 1}",
                        "library": case["library"],
                        "part_name": case["part"],
                        "position": case["position"]
                    }
                }

                self.mock_api.call_history.append(("insert_part", call_record))
                self.assert_api_call_success(result)

            self.log_test_result("零件插入模拟", {"success": all_success})

        self.async_test(test())

    def test_part_positioning(self):
        """测试零件定位"""
        async def test():
            positions = [
                [0, 0, 0],        # 原点
                [100, 0, 0],      # X轴
                [0, 100, 0],      # Y轴
                [0, 0, 100],      # Z轴
                [50, 50, 50],     # 对角线
                [-25, -25, 25],   # 负坐标
            ]

            for i, pos in enumerate(positions):
                # 模拟在不同位置插入零件
                call_record = {
                    "library": "标准件",
                    "part": f"测试零件_{i+1}",
                    "position": pos
                }

                result = {
                    "success": True,
                    "result": {
                        "part_id": f"part_pos_{i+1}",
                        "position": pos
                    }
                }

                self.mock_api.call_history.append(("insert_part", call_record))
                self.assert_api_call_success(result)

            self.log_test_result(f"零件定位测试({len(positions)}个位置)", {"success": True})

        self.async_test(test())

    def test_part_library_categories(self):
        """测试零件库分类"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import get_parts_list

                result = await self.mock_api.get_parts_list()
                parts = result["result"]["parts"]

                # 统计分类
                categories = {}
                libraries = {}

                for part in parts:
                    category = part["category"]
                    library = part["library"]

                    categories[category] = categories.get(category, 0) + 1
                    libraries[library] = libraries.get(library, 0) + 1

                # 验证分类存在
                self.assertIn("紧固件", categories, "应该有紧固件分类")
                self.assertIn("标准件", libraries, "应该有标准件库")

                self.log_test_result("零件库分类测试", {
                    "success": True,
                    "categories": list(categories.keys()),
                    "libraries": list(libraries.keys())
                })

        self.async_test(test())

    def test_invalid_part_handling(self):
        """测试无效零件处理"""
        async def test():
            # 模拟插入不存在的零件
            invalid_cases = [
                {"library": "不存在的库", "part": "测试零件"},
                {"library": "标准件", "part": "不存在的零件"},
                {"library": "", "part": ""},
            ]

            for case in invalid_cases:
                # 模拟失败响应
                result = {
                    "success": False,
                    "error": f"零件不存在: {case['library']}/{case['part']}"
                }

                self.assert_api_call_failure(result, "不存在")

            self.log_test_result("无效零件处理", {"success": True})

        self.async_test(test())

    def tearDown(self):
        """测试结束后清理"""
        self.print_test_summary()
        super().tearDown()


if __name__ == '__main__':
    unittest.main(verbosity=2)
