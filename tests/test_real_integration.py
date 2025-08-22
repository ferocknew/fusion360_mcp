"""
真实集成测试 - 演示如何使用 src 中的真实代码和 MCPClient
"""

import unittest
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tests.test_base import Fusion360TestBase


class TestRealIntegration(Fusion360TestBase):
    """真实集成测试类 - 演示完整的测试流程"""

    def setUp(self):
        super().setUp()
        print(f"\n{'='*60}")
        print("🧪 真实集成测试开始")
        print(f"{'='*60}")

    def test_connection_check(self):
        """测试连接检查"""
        print("🔍 检查 Fusion 360 和 MCP 服务器连接...")

        fusion_ok = self.check_fusion360_connection()
        mcp_ok = self.check_mcp_server_connection()

        print(f"Fusion 360 连接: {'✅ 正常' if fusion_ok else '❌ 失败'}")
        print(f"MCP 服务器连接: {'✅ 正常' if mcp_ok else '❌ 失败'}")

        if fusion_ok and mcp_ok:
            print("🎉 所有连接正常，可以进行测试")
            self.log_test_result("连接检查", {"success": True})
        else:
            print("⚠️  连接检查失败，请检查服务状态")
            self.log_test_result("连接检查", {"success": False, "error": "连接失败"})

            # 提供帮助信息
            if not fusion_ok:
                print("📋 Fusion 360 插件启动步骤:")
                print("  1. 启动 Fusion 360")
                print("  2. 进入 '工具' > '附加模块' > '开发'")
                print("  3. 加载 addin/fusion360_mcp_addin.py")
                print("  4. 确保插件在 localhost:9000 启动")

            if not mcp_ok:
                print("📋 MCP 服务器启动步骤:")
                print("  1. 运行: fusion360_mcp")
                print("  2. 或者: python src/fusion360_mcp/main.py")
                print("  3. 确保服务器在 localhost:8000 启动")

    def test_document_creation_real_tool(self):
        """测试通过真实工具创建文档"""
        async def test():
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("📄 测试通过真实工具创建文档...")

            # 使用 src 中的真实工具
            result = await self.call_real_tool("create_document",
                name="真实工具测试文档",
                units="mm"
            )

            if result.get("success"):
                print("✅ 真实工具创建文档成功")
                print(f"   结果: {result}")
                self.log_test_result("真实工具创建文档", result)
                self.assert_api_call_success(result)
            else:
                print(f"❌ 真实工具创建文档失败: {result.get('error')}")
                self.log_test_result("真实工具创建文档", result)

        self.async_test(test())

    def test_document_creation_mcp_client(self):
        """测试通过 MCPClient 创建文档"""
        def test():
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("📞 测试通过 MCPClient 创建文档...")

            # 使用 MCPClient
            result = self.call_mcp_client_method("create_document",
                name="MCPClient测试文档",
                units="mm"
            )

            if result.get("success"):
                print("✅ MCPClient 创建文档成功")
                print(f"   结果: {result}")
                self.log_test_result("MCPClient创建文档", result)
                self.assert_api_call_success(result)
            else:
                print(f"❌ MCPClient 创建文档失败: {result.get('error')}")
                self.log_test_result("MCPClient创建文档", result)

        test()

    def test_object_creation_workflow(self):
        """测试对象创建工作流"""
        async def test():
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("🔵 测试对象创建工作流...")

            # 1. 先创建文档
            doc_result = await self.call_real_tool("create_document",
                name="对象测试文档"
            )

            if not doc_result.get("success"):
                print("❌ 文档创建失败，跳过对象创建测试")
                return

            print("✅ 文档创建成功，开始创建对象")

            # 2. 创建圆柱体
            cylinder_result = await self.call_real_tool("create_object",
                object_type="extrude",
                parameters={
                    "base_feature": "circle",
                    "radius": 25.0,
                    "height": 50.0
                }
            )

            if cylinder_result.get("success"):
                print("✅ 圆柱体创建成功")
                self.log_test_result("创建圆柱体", cylinder_result)
            else:
                print(f"❌ 圆柱体创建失败: {cylinder_result.get('error')}")
                self.log_test_result("创建圆柱体", cylinder_result)

            # 3. 创建立方体
            box_result = await self.call_real_tool("create_object",
                object_type="extrude",
                parameters={
                    "base_feature": "rectangle",
                    "length": 40.0,
                    "width": 30.0,
                    "height": 20.0
                },
                position=[60, 0, 0]
            )

            if box_result.get("success"):
                print("✅ 立方体创建成功")
                self.log_test_result("创建立方体", box_result)
            else:
                print(f"❌ 立方体创建失败: {box_result.get('error')}")
                self.log_test_result("创建立方体", box_result)

            # 4. 获取对象列表
            objects_result = await self.call_real_tool("get_objects")

            if objects_result.get("success"):
                objects = objects_result.get("result", {}).get("objects", [])
                print(f"✅ 获取对象列表成功，共 {len(objects)} 个对象")
                self.log_test_result("获取对象列表", objects_result)
            else:
                print(f"❌ 获取对象列表失败: {objects_result.get('error')}")
                self.log_test_result("获取对象列表", objects_result)

        self.async_test(test())

    def test_parts_library_access(self):
        """测试零件库访问"""
        async def test():
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("🔧 测试零件库访问...")

            # 获取零件列表
            parts_result = await self.call_real_tool("get_parts_list")

            if parts_result.get("success"):
                parts = parts_result.get("result", {}).get("parts", [])
                print(f"✅ 获取零件列表成功，共 {len(parts)} 个零件")

                # 显示前几个零件
                for i, part in enumerate(parts[:3]):
                    print(f"   {i+1}. {part.get('library', 'N/A')}/{part.get('name', 'N/A')} ({part.get('category', 'N/A')})")

                if len(parts) > 3:
                    print(f"   ... 还有 {len(parts) - 3} 个零件")

                self.log_test_result("获取零件列表", parts_result)
                self.assert_api_call_success(parts_result)
            else:
                print(f"❌ 获取零件列表失败: {parts_result.get('error')}")
                self.log_test_result("获取零件列表", parts_result)

        self.async_test(test())

    def tearDown(self):
        """测试清理"""
        print(f"\n{'='*60}")
        print("📊 真实集成测试结果:")
        self.print_test_summary()
        print(f"{'='*60}")
        super().tearDown()


if __name__ == '__main__':
    # 设置详细输出
    unittest.main(verbosity=2)
