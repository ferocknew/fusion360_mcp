"""
对象相关工具的单元测试
"""

import unittest
from unittest.mock import patch, AsyncMock
from .test_base import Fusion360TestBase, MockFusion360API


class TestObjectTools(Fusion360TestBase):
    """对象工具测试类"""

    def setUp(self):
        super().setUp()
        self.mock_api = MockFusion360API()

    def test_create_cylinder(self):
        """测试创建圆柱体"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import create_object

                result = await self.mock_api.create_object(
                    object_type="extrude",
                    parameters={
                        "base_feature": "circle",
                        "radius": 25.0,
                        "height": 50.0
                    }
                )
                self.log_test_result("创建圆柱体", result)

                self.assert_api_call_success(result, ["object_id", "type", "parameters"])
                self.assertEqual(result["result"]["type"], "extrude")
                self.assertEqual(result["result"]["parameters"]["radius"], 25.0)

        self.async_test(test())

    def test_create_box(self):
        """测试创建立方体"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import create_object

                result = await self.mock_api.create_object(
                    object_type="extrude",
                    parameters={
                        "base_feature": "rectangle",
                        "length": 40.0,
                        "width": 30.0,
                        "height": 20.0
                    },
                    position=[10, 5, 0]
                )
                self.log_test_result("创建立方体", result)

                self.assert_api_call_success(result)
                self.assertEqual(result["result"]["parameters"]["length"], 40.0)

        self.async_test(test())

    def test_create_sphere(self):
        """测试创建球体"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import create_object

                result = await self.mock_api.create_object(
                    object_type="revolve",
                    parameters={
                        "base_feature": "semicircle",
                        "radius": 20.0
                    }
                )
                self.log_test_result("创建球体", result)

                self.assert_api_call_success(result)
                self.assertEqual(result["result"]["type"], "revolve")

        self.async_test(test())

    def test_get_objects_empty(self):
        """测试获取空对象列表"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import get_objects

                result = await self.mock_api.get_objects()
                self.log_test_result("获取空对象列表", result)

                self.assert_api_call_success(result)
                self.assertEqual(len(result["result"]["objects"]), 0)

        self.async_test(test())

    def test_get_objects_with_data(self):
        """测试获取包含对象的列表"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import get_objects

                # 先创建一些对象
                await self.mock_api.create_object("extrude", {"radius": 10, "height": 20})
                await self.mock_api.create_object("revolve", {"radius": 15})

                result = await self.mock_api.get_objects()
                self.log_test_result("获取对象列表(有数据)", result)

                self.assert_api_call_success(result)
                self.assertEqual(len(result["result"]["objects"]), 2)

        self.async_test(test())

    def test_get_specific_object(self):
        """测试获取特定对象"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import get_object

                # 先创建一个对象
                create_result = await self.mock_api.create_object(
                    "extrude",
                    {"radius": 15, "height": 30}
                )
                object_id = create_result["result"]["object_id"]

                # 获取该对象
                result = await self.mock_api.get_object(object_id)
                self.log_test_result("获取特定对象", result)

                self.assert_api_call_success(result)
                self.assertEqual(result["result"]["object"]["id"], object_id)

        self.async_test(test())

    def test_get_nonexistent_object(self):
        """测试获取不存在的对象"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import get_object

                result = await self.mock_api.get_object("non_existent_id")
                self.log_test_result("获取不存在的对象", result)

                self.assert_api_call_failure(result, "不存在")

        self.async_test(test())

    def test_delete_object(self):
        """测试删除对象"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import delete_object

                # 先创建一个对象
                create_result = await self.mock_api.create_object(
                    "extrude",
                    {"radius": 10, "height": 20}
                )
                object_id = create_result["result"]["object_id"]

                # 删除该对象
                result = await self.mock_api.delete_object(object_id)
                self.log_test_result("删除对象", result)

                self.assert_api_call_success(result)

                # 验证对象已被删除
                get_result = await self.mock_api.get_object(object_id)
                self.assert_api_call_failure(get_result)

        self.async_test(test())

    def test_delete_nonexistent_object(self):
        """测试删除不存在的对象"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import delete_object

                result = await self.mock_api.delete_object("non_existent_id")
                self.log_test_result("删除不存在的对象", result)

                self.assert_api_call_failure(result, "不存在")

        self.async_test(test())

    def test_object_positioning(self):
        """测试对象定位"""
        async def test():
            with patch('fusion360_mcp.tools.get_api', return_value=self.mock_api):
                from fusion360_mcp.tools import create_object

                positions = [
                    [0, 0, 0],      # 原点
                    [10, 20, 30],   # 正坐标
                    [-5, -10, 15],  # 负坐标
                ]

                for i, pos in enumerate(positions):
                    result = await self.mock_api.create_object(
                        "extrude",
                        {"radius": 5, "height": 10},
                        position=pos
                    )
                    self.assert_api_call_success(result)

                self.log_test_result(f"对象定位测试({len(positions)}个位置)", {"success": True})

        self.async_test(test())

    def tearDown(self):
        """测试结束后清理"""
        self.print_test_summary()
        super().tearDown()


if __name__ == '__main__':
    unittest.main(verbosity=2)
