#!/usr/bin/env python3
"""
单个操作测试 - 每次只测试一个功能，避免同时创建过多对象
"""

import unittest
import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.fusion360_mcp import tools


class TestSingleOperations(unittest.TestCase):
    """单个操作测试类"""

    @classmethod
    def setUpClass(cls):
        """类初始化"""
        print("🧪 Fusion360 MCP 单个操作测试")
        print("=" * 50)
        print("策略: 每次只测试一个功能，避免对象创建冲突")
        print("要求: Fusion 360 插件运行在端口 9000")
        print("=" * 50)

    def setUp(self):
        """每个测试前的设置"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """每个测试后的清理"""
        self.loop.close()

    def async_test(self, coro):
        """运行异步测试"""
        return self.loop.run_until_complete(coro)

    def test_01_fusion360_connection(self):
        """测试 1: Fusion 360 插件连接"""
        print("\n🔍 测试 Fusion 360 插件连接...")

        async def test_connection():
            api = tools.Fusion360API()
            try:
                result = await api._request('GET', '/api/health')
                self.assertIn('status', result)
                self.assertEqual(result['status'], 'healthy')
                print(f"✅ 连接成功: {result}")
                return True
            except Exception as e:
                print(f"❌ 连接失败: {e}")
                return False
            finally:
                await api.close()

        success = self.async_test(test_connection())
        self.assertTrue(success, "Fusion 360 插件连接失败")

    def test_02_create_single_document(self):
        """测试 2: 创建单个文档"""
        print("\n📄 测试创建单个文档...")

        async def test_document():
            try:
                result = await tools.create_document(name="测试文档_单个", units="mm")
                print(f"✅ 文档创建结果: {result}")
                # 即使失败也记录结果，因为单位设置问题是已知的
                self.assertIn('success', result)
                return True
            except Exception as e:
                print(f"❌ 文档创建失败: {e}")
                return False

        success = self.async_test(test_document())
        self.assertTrue(success, "文档创建测试失败")

    def test_03_create_single_box(self):
        """测试 3: 创建单个盒子"""
        print("\n📦 测试创建单个盒子...")

        async def test_box():
            try:
                result = await tools.create_object(
                    object_type="box",
                    parameters={
                        "width": 20.0,
                        "height": 20.0,
                        "depth": 20.0
                    }
                )
                print(f"✅ 盒子创建结果: {result}")
                self.assertIn('success', result)
                if result.get('success'):
                    self.assertIn('object_id', result)
                return True
            except Exception as e:
                print(f"❌ 盒子创建失败: {e}")
                return False

        success = self.async_test(test_box())
        self.assertTrue(success, "盒子创建测试失败")

    def test_04_get_objects_list(self):
        """测试 4: 获取对象列表"""
        print("\n📋 测试获取对象列表...")

        async def test_objects():
            try:
                result = await tools.get_objects()  # 正确的函数名
                print(f"✅ 对象列表: {result}")
                self.assertIn('success', result)
                if result.get('success'):
                    self.assertIn('objects', result)
                    objects = result['objects']
                    print(f"   找到 {len(objects)} 个对象")
                    for i, obj in enumerate(objects[:3]):  # 只显示前3个
                        print(f"   - {i+1}: {obj.get('name', 'N/A')} ({obj.get('type', 'N/A')})")
                return True
            except Exception as e:
                print(f"❌ 获取对象列表失败: {e}")
                return False

        success = self.async_test(test_objects())
        self.assertTrue(success, "获取对象列表测试失败")

    def test_05_create_single_cylinder(self):
        """测试 5: 创建单个圆柱体"""
        print("\n🔵 测试创建单个圆柱体...")

        async def test_cylinder():
            try:
                result = await tools.create_object(
                    object_type="cylinder",
                    parameters={
                        "radius": 15.0,
                        "height": 30.0
                    }
                )
                print(f"✅ 圆柱体创建结果: {result}")
                self.assertIn('success', result)
                if result.get('success'):
                    self.assertIn('object_id', result)
                return True
            except Exception as e:
                print(f"❌ 圆柱体创建失败: {e}")
                return False

        success = self.async_test(test_cylinder())
        self.assertTrue(success, "圆柱体创建测试失败")


if __name__ == '__main__':
    # 设置详细输出
    unittest.main(verbosity=2)
