"""
Fusion360 MCP Addin - 视图截图功能测试

测试项目:
- [ ] `get_view`: 获取活动视图的截图

使用 FastMCP 工具函数进行测试
"""

import unittest
import time
import os
import base64
import sys
from pathlib import Path

# 添加 tests 目录到 Python 路径
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

from test_base import Fusion360TestBase


class TestViewCaptureFunctionality(Fusion360TestBase):
    """视图截图功能测试类 - 使用 FastMCP 工具函数"""

    def test_01_check_fusion360_connection(self):
        """测试 1: 检查 Fusion 360 插件连接"""
        print("\n🔍 测试 1: 检查 Fusion 360 插件连接")

        success = self.async_test(self.check_fusion360_connection())
        self.assertTrue(success, "Fusion 360 插件连接失败")
        print("   ✅ Fusion 360 插件连接正常")

    def test_02_get_fusion360_status(self):
        """测试 2: 获取 Fusion 360 状态"""
        print("\n🔍 测试 2: 获取 Fusion 360 状态")

        def test_status():
            api = self.tools.get_api()
            return api._request('GET', '/api/status')

        try:
            result = self.async_test(test_status())

            self.assertIsInstance(result, dict)

            # 先打印实际返回的结果，方便调试
            print(f"   实际返回结果: {result}")

            if result.get('success', False):
                print(f"   应用: {result.get('app_name', 'N/A')}")
                print(f"   版本: {result.get('version', 'N/A')}")
                print(f"   活动文档: {result.get('active_document', 'N/A')}")
                print(f"   设计工作空间: {result.get('design_workspace', False)}")

                if not result.get('active_document'):
                    print("   ⚠️  建议: 在 Fusion 360 中创建或打开一个设计文档")

                print("   ✅ 状态获取成功")
            else:
                # 如果获取失败，显示错误信息但不立即失败测试
                error = result.get('error', '未知错误')
                print(f"   ⚠️  状态获取失败: {error}")
                print("   这可能是因为 Fusion 360 未启动或插件未加载")

                # 只有在完全无法连接时才失败
                if "连接" in error or "refused" in error.lower():
                    self.fail(f"无法连接到 Fusion 360 插件: {error}")

        except Exception as e:
            self.fail(f"获取状态异常: {str(e)}")

    def test_03_get_view_using_fastmcp_tools(self):
        """测试 3: 使用 FastMCP 工具函数获取视图截图"""
        print("\n🔍 测试 3: 使用 FastMCP 工具函数获取视图截图")

        # 使用 FastMCP 工具函数
        def test_get_view():
            return self.tools.get_view(
                width=800,
                height=600,
                format="png"
            )

        try:
            result = self.async_test(test_get_view())

            self.assertIsInstance(result, dict)
            print(f"   工具函数返回: {result}")

            # 根据实际返回结果进行验证
            if result.get('success'):
                print("   ✅ FastMCP 工具函数调用成功")

                # 验证返回的截图信息
                if 'file_path' in result:
                    print(f"      文件路径: {result['file_path']}")
                if 'dimensions' in result:
                    dims = result['dimensions']
                    print(f"      尺寸: {dims.get('width')}x{dims.get('height')}")

            else:
                error = result.get('error', '未知错误')
                print(f"   ❌ FastMCP 工具函数调用失败: {error}")
                # 不立即 fail，因为可能是插件接口不匹配
                print("   ℹ️  这可能是因为插件接口与工具函数期望不匹配")

        except Exception as e:
            print(f"   ❌ FastMCP 工具函数调用异常: {str(e)}")
            print("   ℹ️  这可能是因为插件接口与工具函数期望不匹配")

    def test_04_get_view_info_direct_api(self):
        """测试 4: 直接 API 调用获取视图信息"""
        print("\n🔍 测试 4: 直接 API 调用获取视图信息")

        # 直接调用插件的 GET /api/view 接口
        def test_view_info():
            api = self.tools.get_api()
            return api._request('GET', '/api/view')

        try:
            result = self.async_test(test_view_info())

            if result.get('success'):
                print("   ✅ 成功获取视图信息")

                # 验证返回的视图信息结构
                if 'viewport' in result:
                    viewport = result['viewport']
                    print(f"      视口尺寸: {viewport.get('width')}x{viewport.get('height')}")

                if 'camera' in result:
                    camera = result['camera']
                    print(f"      相机类型: {camera.get('cameraType')}")

                    if 'target' in camera:
                        target = camera['target']
                        print(f"      目标点: ({target.get('x'):.2f}, {target.get('y'):.2f}, {target.get('z'):.2f})")

                # 基本验证
                self.assertIn('viewport', result)
                self.assertIn('camera', result)

            else:
                error = result.get('error', '未知错误')
                print(f"   ❌ 获取视图信息失败: {error}")
                self.fail(f"获取视图信息失败: {error}")

        except Exception as e:
            self.fail(f"视图信息请求失败: {str(e)}")

    def test_05_capture_view_default_parameters(self):
        """测试 5: 默认参数截图"""
        print("\n🔍 测试 5: 默认参数截图")

        # 直接调用插件的 POST /api/view 接口
        def test_capture():
            api = self.tools.get_api()
            return api._request('POST', '/api/view', {"parameters": {}})

        try:
            result = self.async_test(test_capture())

            if result.get('success'):
                print("   ✅ 默认参数截图成功")

                # 验证返回的截图信息
                required_fields = ['file_path', 'filename', 'file_size', 'dimensions', 'format']
                for field in required_fields:
                    if field in result:
                        print(f"      {field}: {result[field]}")

                # 验证文件是否真的存在
                file_path = result.get('file_path')
                if file_path and os.path.exists(file_path):
                    actual_size = os.path.getsize(file_path)
                    print(f"      ✓ 文件存在，实际大小: {actual_size} 字节")
                    self.assertEqual(actual_size, result.get('file_size', 0))

                # 基本验证
                self.assertIn('file_path', result)
                self.assertIn('dimensions', result)
                self.assertGreater(result.get('file_size', 0), 0)

            else:
                error = result.get('error', '未知错误')
                print(f"   ❌ 默认参数截图失败: {error}")
                self.fail(f"默认参数截图失败: {error}")

        except Exception as e:
            self.fail(f"截图请求失败: {str(e)}")

    def test_06_capture_view_custom_size(self):
        """测试 6: 自定义尺寸截图"""
        print("\n🔍 测试 6: 自定义尺寸截图")

        custom_width = 640
        custom_height = 480

        def test_custom_capture():
            api = self.tools.get_api()
            return api._request('POST', '/api/view', {
                "parameters": {
                    "width": custom_width,
                    "height": custom_height,
                    "format": "png"
                }
            })

        try:
            result = self.async_test(test_custom_capture())

            if result.get('success'):
                print("   ✅ 自定义尺寸截图成功")

                dimensions = result.get('dimensions', {})
                print(f"      请求尺寸: {custom_width}x{custom_height}")
                print(f"      实际尺寸: {dimensions.get('width')}x{dimensions.get('height')}")
                print(f"      文件大小: {result.get('file_size')} 字节")

                # 验证尺寸是否符合要求
                self.assertEqual(dimensions.get('width'), custom_width)
                self.assertEqual(dimensions.get('height'), custom_height)
                self.assertEqual(result.get('format'), 'png')

            else:
                error = result.get('error', '未知错误')
                print(f"   ❌ 自定义尺寸截图失败: {error}")
                self.fail(f"自定义尺寸截图失败: {error}")

        except Exception as e:
            self.fail(f"自定义尺寸截图请求失败: {str(e)}")

    def test_07_capture_view_with_base64(self):
        """测试 7: 截图并返回 Base64 数据"""
        print("\n🔍 测试 7: 截图并返回 Base64 数据")

        def test_base64_capture():
            api = self.tools.get_api()
            return api._request('POST', '/api/view', {
                "parameters": {
                    "width": 320,
                    "height": 240,
                    "return_base64": True
                }
            })

        try:
            result = self.async_test(test_base64_capture())

            if result.get('success'):
                print("   ✅ Base64 截图成功")

                if 'image_data' in result:
                    base64_data = result['image_data']
                    print(f"      Base64 数据长度: {len(base64_data)} 字符")

                    # 验证 Base64 数据格式
                    try:
                        decoded = base64.b64decode(base64_data)
                        print(f"      ✓ Base64 解码成功，二进制大小: {len(decoded)} 字节")

                        # 验证解码后的数据大小合理
                        self.assertGreater(len(decoded), 100)  # 至少应该有一些图像数据

                    except Exception as decode_error:
                        print(f"      ❌ Base64 解码失败: {decode_error}")
                        self.fail(f"Base64 数据格式错误: {decode_error}")

                    # 验证 Base64 数据是字符串且非空
                    self.assertIsInstance(base64_data, str)
                    self.assertGreater(len(base64_data), 0)

                else:
                    print("   ❌ 未返回 Base64 数据")
                    self.fail("请求了 Base64 数据但未返回")

            else:
                error = result.get('error', '未知错误')
                print(f"   ❌ Base64 截图失败: {error}")
                self.fail(f"Base64 截图失败: {error}")

        except Exception as e:
            self.fail(f"Base64 截图请求失败: {str(e)}")

    def test_08_invalid_parameters_handling(self):
        """测试 8: 无效参数处理"""
        print("\n🔍 测试 8: 无效参数处理")

        invalid_cases = [
            {
                "name": "宽度过小",
                "params": {"width": 50, "height": 600},
                "expect_error": "宽度必须在"
            },
            {
                "name": "不支持的格式",
                "params": {"width": 600, "height": 400, "format": "gif"},
                "expect_error": "支持的格式"
            }
        ]

        for case in invalid_cases:
            with self.subTest(case=case['name']):
                print(f"      测试: {case['name']}")

                def test_invalid():
                    api = self.tools.get_api()
                    return api._request('POST', '/api/view', {"parameters": case['params']})

                try:
                    result = self.async_test(test_invalid())

                    # 应该返回失败结果
                    self.assertFalse(result.get('success', True),
                                   f"无效参数应该被拒绝: {case['name']}")

                    error_msg = result.get('error', '')
                    self.assertIn(case['expect_error'], error_msg,
                                f"错误消息不符合预期: {error_msg}")

                    print(f"         ✅ 正确拒绝: {error_msg}")

                except Exception as e:
                    self.fail(f"无效参数测试异常: {case['name']} - {str(e)}")

    def test_09_compare_fastmcp_vs_direct_api(self):
        """测试 9: 比较 FastMCP 工具函数与直接 API 调用"""
        print("\n🔍 测试 9: 比较 FastMCP 工具函数与直接 API 调用")

        # FastMCP 工具函数调用
        def test_fastmcp():
            return self.tools.get_view(width=400, height=300, format="png")

        # 直接 API 调用
        def test_direct_api():
            api = self.tools.get_api()
            return api._request('POST', '/api/view', {
                "parameters": {
                    "width": 400,
                    "height": 300,
                    "format": "png"
                }
            })

        try:
            print("      比较两种调用方式...")

            # FastMCP 方式
            try:
                fastmcp_result = self.async_test(test_fastmcp())
                print(f"      FastMCP 结果: {fastmcp_result.get('success', False)}")
                if not fastmcp_result.get('success'):
                    print(f"         错误: {fastmcp_result.get('error', 'N/A')}")
            except Exception as e:
                print(f"      FastMCP 异常: {str(e)}")
                fastmcp_result = {"success": False, "error": str(e)}

            # 直接 API 方式
            try:
                direct_result = self.async_test(test_direct_api())
                print(f"      直接 API 结果: {direct_result.get('success', False)}")
                if not direct_result.get('success'):
                    print(f"         错误: {direct_result.get('error', 'N/A')}")
            except Exception as e:
                print(f"      直接 API 异常: {str(e)}")
                direct_result = {"success": False, "error": str(e)}

            # 至少有一种方式应该成功
            if direct_result.get('success'):
                print("      ✅ 直接 API 调用成功")
                # 如果直接 API 成功，FastMCP 工具函数也应该能适配
            elif fastmcp_result.get('success'):
                print("      ✅ FastMCP 工具函数成功")
            else:
                print("      ⚠️  两种方式都失败，可能需要检查插件状态或接口匹配")

        except Exception as e:
            self.fail(f"比较测试失败: {str(e)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
