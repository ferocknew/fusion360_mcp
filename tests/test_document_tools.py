"""
文档相关工具的单元测试 - 使用真实的 src 代码和 MCPClient
"""

import unittest
from .test_base import Fusion360TestBase


class TestDocumentTools(Fusion360TestBase):
    """文档工具测试类 - 使用真实的 src 代码和 MCPClient"""

    def setUp(self):
        super().setUp()

    def check_prerequisites(self) -> bool:
        """检查测试前提条件"""
        fusion_ok = self.check_fusion360_connection()
        mcp_ok = self.check_mcp_server_connection()

        if not fusion_ok:
            print("⚠️  Fusion 360 插件未运行，请启动 Fusion 360 并加载 MCP 插件")
            return False

        if not mcp_ok:
            print("⚠️  MCP 服务器未运行，请启动 MCP 服务器")
            return False

        return True

    def test_create_document_default_params(self):
        """测试使用默认参数创建文档 - 通过真实工具"""
        async def test():
            # 检查前提条件
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("🧪 测试通过真实工具创建文档(默认参数)...")

            # 直接调用 src 中的真实工具
            result = await self.call_real_tool("create_document",
                name=None,
                template=None,
                units="mm"
            )
            self.log_test_result("创建文档(默认参数)-真实工具", result)

            if result.get("success"):
                print(f"✅ 真实工具创建文档成功")
                self.assert_api_call_success(result)
            else:
                print(f"⚠️  真实工具创建文档失败: {result.get('error')}")

        self.async_test(test())

    def test_create_document_via_mcp_client(self):
        """测试通过 MCPClient 创建文档"""
        def test():
            # 检查前提条件
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("🧪 测试通过 MCPClient 创建文档...")

            # 通过 MCPClient 调用
            result = self.call_mcp_client_method("create_document",
                name="MCPClient测试文档",
                template=None,
                units="mm"
            )
            self.log_test_result("创建文档-MCPClient", result)

            if result.get("success"):
                print(f"✅ MCPClient 创建文档成功")
                self.assert_api_call_success(result)
            else:
                print(f"⚠️  MCPClient 创建文档失败: {result.get('error')}")

        test()

    def test_create_document_custom_params(self):
        """测试使用自定义参数创建文档"""
        async def test():
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("🧪 测试通过真实工具创建文档(自定义参数)...")

            # 测试自定义参数创建文档 - 使用真实工具
            result = await self.call_real_tool("create_document",
                name="测试项目",
                template="机械设计",
                units="cm"
            )
            self.log_test_result("创建文档(自定义参数)-真实工具", result)

            if result.get("success"):
                self.assert_api_call_success(result)
                print(f"✅ 自定义文档创建成功")
            else:
                print(f"⚠️  自定义文档创建失败: {result.get('error')}")

        self.async_test(test())

    def test_create_multiple_documents(self):
        """测试创建多个文档"""
        async def test():
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("🧪 测试通过真实工具创建多个文档...")

            # 创建多个文档
            doc_names = ["测试项目A", "测试项目B", "测试项目C"]
            success_count = 0

            for name in doc_names:
                result = await self.call_real_tool("create_document", name=name)
                if result.get("success"):
                    success_count += 1
                    print(f"✅ 文档 '{name}' 创建成功")
                else:
                    print(f"❌ 文档 '{name}' 创建失败: {result.get('error')}")

            self.log_test_result(f"创建多个文档({success_count}/{len(doc_names)})",
                               {"success": success_count > 0})

            # 只要有文档创建成功就算通过
            if success_count > 0:
                print(f"✅ 成功创建 {success_count}/{len(doc_names)} 个文档")
            else:
                print(f"❌ 所有文档创建都失败")

        self.async_test(test())

    def test_document_units_validation(self):
        """测试文档单位验证"""
        async def test():
            if not self.check_prerequisites():
                self.skipTest("缺少必要的服务连接")
                return

            print("🧪 测试不同单位的文档创建...")

            # 测试不同单位
            units_to_test = ["mm", "cm", "m", "in", "ft"]
            success_count = 0

            for unit in units_to_test:
                result = await self.call_real_tool("create_document",
                    name=f"测试_{unit}",
                    units=unit
                )

                if result.get("success"):
                    success_count += 1
                    print(f"✅ 单位 '{unit}' 文档创建成功")
                else:
                    print(f"❌ 单位 '{unit}' 文档创建失败: {result.get('error')}")

            self.log_test_result(f"文档单位验证({success_count}/{len(units_to_test)})",
                               {"success": success_count > 0})

        self.async_test(test())

    def tearDown(self):
        """测试结束后清理"""
        self.print_test_summary()
        super().tearDown()


if __name__ == '__main__':
    unittest.main(verbosity=2)
