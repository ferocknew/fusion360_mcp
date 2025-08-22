#!/usr/bin/env python3
"""
快速测试脚本 - 用于快速验证单个工具功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tests.test_base import Fusion360TestBase


class QuickTester(Fusion360TestBase):
    """快速测试器 - 使用真实代码"""

    def __init__(self):
        # 手动初始化，因为不是标准的 unittest
        import unittest
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # 初始化基类
        super().__init__()
        self.test_results = []

    async def test_document_creation(self):
        """快速测试文档创建"""
        print("🧪 测试文档创建...")

        if not self.check_prerequisites():
            print("❌ 连接检查失败")
            return False

        result = await self.call_real_tool("create_document",
            name="快速测试文档",
            units="mm"
        )

        if result.get("success"):
            print(f"✅ 文档创建成功")
        else:
            print(f"❌ 文档创建失败: {result.get('error')}")

        return result.get("success", False)

    async def test_object_creation(self):
        """快速测试对象创建"""
        print("🧪 测试对象创建...")

        # 测试圆柱体
        cylinder_result = await self.api.create_object(
            "extrude",
            {"base_feature": "circle", "radius": 25, "height": 50}
        )

        # 测试立方体
        box_result = await self.api.create_object(
            "extrude",
            {"base_feature": "rectangle", "length": 40, "width": 30, "height": 20},
            position=[60, 0, 0]
        )

        success_count = 0
        if cylinder_result["success"]:
            print(f"✅ 圆柱体创建成功: {cylinder_result['result']['object_id']}")
            success_count += 1
        else:
            print(f"❌ 圆柱体创建失败")

        if box_result["success"]:
            print(f"✅ 立方体创建成功: {box_result['result']['object_id']}")
            success_count += 1
        else:
            print(f"❌ 立方体创建失败")

        return success_count == 2

    async def test_object_management(self):
        """快速测试对象管理"""
        print("🧪 测试对象管理...")

        # 获取对象列表
        objects_result = await self.api.get_objects()

        if not objects_result["success"]:
            print("❌ 获取对象列表失败")
            return False

        objects = objects_result["result"]["objects"]
        print(f"✅ 获取对象列表成功，共 {len(objects)} 个对象")

        if len(objects) == 0:
            print("⚠️  对象列表为空，跳过后续测试")
            return True

        # 测试获取第一个对象
        first_obj_id = objects[0]["id"]
        obj_result = await self.api.get_object(first_obj_id)

        if obj_result["success"]:
            print(f"✅ 获取对象详情成功: {first_obj_id}")
        else:
            print(f"❌ 获取对象详情失败: {first_obj_id}")
            return False

        # 测试删除对象
        delete_result = await self.api.delete_object(first_obj_id)

        if delete_result["success"]:
            print(f"✅ 删除对象成功: {first_obj_id}")
        else:
            print(f"❌ 删除对象失败: {first_obj_id}")
            return False

        return True

    async def test_parts_library(self):
        """快速测试零件库"""
        print("🧪 测试零件库...")

        parts_result = await self.api.get_parts_list()

        if parts_result["success"]:
            parts = parts_result["result"]["parts"]
            print(f"✅ 获取零件列表成功，共 {len(parts)} 个零件")

            # 显示前几个零件
            for i, part in enumerate(parts[:3]):
                print(f"   {i+1}. {part['library']}/{part['name']} ({part['category']})")

            if len(parts) > 3:
                print(f"   ... 还有 {len(parts) - 3} 个零件")

            return True
        else:
            print(f"❌ 获取零件列表失败: {parts_result.get('error')}")
            return False

    async def run_all_quick_tests(self):
        """运行所有快速测试"""
        print("🚀 开始 Fusion360 MCP 快速测试")
        print("=" * 50)

        tests = [
            ("文档创建", self.test_document_creation),
            ("对象创建", self.test_object_creation),
            ("对象管理", self.test_object_management),
            ("零件库", self.test_parts_library),
        ]

        results = []

        for test_name, test_func in tests:
            print(f"\n📋 {test_name} 测试:")
            try:
                success = await test_func()
                results.append((test_name, success))
                status = "✅ 通过" if success else "❌ 失败"
                print(f"   结果: {status}")
            except Exception as e:
                print(f"   结果: ❌ 异常 - {e}")
                results.append((test_name, False))

        # 打印总结
        print("\n" + "=" * 50)
        print("📊 快速测试总结:")

        passed = sum(1 for _, success in results if success)
        total = len(results)

        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"成功率: {passed/total*100:.1f}%")

        print("\n详细结果:")
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")

        if passed == total:
            print("\n🎉 所有快速测试通过！")
        elif passed >= total * 0.8:
            print(f"\n👍 大部分测试通过 ({passed}/{total})")
        else:
            print(f"\n⚠️  需要关注，多个测试失败 ({total-passed}/{total})")

        return passed == total


async def main():
    """主函数"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()

        tester = QuickTester()

        # 单独运行指定测试
        if test_name in ["doc", "document", "文档"]:
            await tester.test_document_creation()
        elif test_name in ["obj", "object", "对象"]:
            await tester.test_object_creation()
        elif test_name in ["mgmt", "management", "管理"]:
            await tester.test_object_management()
        elif test_name in ["part", "parts", "零件"]:
            await tester.test_parts_library()
        else:
            print(f"未知的测试类型: {test_name}")
            print("可用选项: doc/document, obj/object, mgmt/management, part/parts")
            print("或者运行不带参数的完整测试")
    else:
        # 运行所有测试
        tester = QuickTester()
        await tester.run_all_quick_tests()


if __name__ == "__main__":
    asyncio.run(main())
