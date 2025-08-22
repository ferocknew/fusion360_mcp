"""
Fusion360 MCP Addin - 视图截图功能测试

测试项目:
- [ ] `get_view`: 获取活动视图的截图
"""

import unittest
import requests
import json
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
    """视图截图功能测试类"""

    def test_01_check_fusion360_connection(self):
        """测试 1: 检查 Fusion 360 插件连接"""
        print("\n🔍 测试 1: 检查 Fusion 360 插件连接")

        success = self.check_fusion360_connection()
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
            self.assertTrue(result.get('success', False))

            print(f"   应用: {result.get('app_name', 'N/A')}")
            print(f"   版本: {result.get('version', 'N/A')}")
            print(f"   活动文档: {result.get('active_document', 'N/A')}")
            print(f"   设计工作空间: {result.get('design_workspace', False)}")

            if not result.get('active_document'):
                print("   ⚠️  建议: 在 Fusion 360 中创建或打开一个设计文档")

            print("   ✅ 状态获取成功")

        except Exception as e:
            self.fail(f"获取状态失败: {str(e)}")

    def test_03_get_view_info_get_request(self):
        """测试 3: 获取视图信息 (GET 请求)"""
        print("\n🔍 测试 3: 获取视图信息 (GET 请求)")

        def test_view_info():
            api = self.tools.get_api()
            return api._request('GET', '/api/view')

        try:
            result = self.async_test(test_view_info())

            if result.get('success'):
                print("   ✅ 成功获取视图信息")

                # 验证返回的视图信息结构
                self.assertIn('viewport', result)
                self.assertIn('camera', result)

                viewport = result['viewport']
                camera = result['camera']

                print(f"      视口尺寸: {viewport.get('width')}x{viewport.get('height')}")
                print(f"      相机类型: {camera.get('cameraType')}")

                # 验证相机信息完整性
                self.assertIn('target', camera)
                self.assertIn('eye', camera)
                self.assertIn('upVector', camera)

                target = camera['target']
                print(f"      目标点: ({target.get('x'):.2f}, {target.get('y'):.2f}, {target.get('z'):.2f})")

            else:
                error = result.get('error', '未知错误')
                print(f"   ❌ 获取视图信息失败: {error}")
                self.fail(f"获取视图信息失败: {error}")

        except Exception as e:
            self.fail(f"视图信息请求失败: {str(e)}")

    def test_04_capture_view_default_parameters(self):
        """测试 4: 默认参数截图"""
        print("\n🔍 测试 4: 默认参数截图")

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
                    self.assertIn(field, result, f"缺少字段: {field}")

                dimensions = result['dimensions']
                print(f"      文件名: {result['filename']}")
                print(f"      尺寸: {dimensions['width']}x{dimensions['height']}")
                print(f"      大小: {result['file_size']} 字节")
                print(f"      格式: {result['format']}")

                # 验证文件是否真的存在
                file_path = result['file_path']
                if os.path.exists(file_path):
                    actual_size = os.path.getsize(file_path)
                    print(f"      ✓ 文件存在，实际大小: {actual_size} 字节")
                    self.assertEqual(actual_size, result['file_size'])
                else:
                    print(f"      ⚠️  文件不存在: {file_path}")

                # 验证尺寸合理性
                self.assertGreater(dimensions['width'], 0)
                self.assertGreater(dimensions['height'], 0)
                self.assertGreater(result['file_size'], 0)

            else:
                error = result.get('error', '未知错误')
                print(f"   ❌ 默认参数截图失败: {error}")
                self.fail(f"默认参数截图失败: {error}")

        except Exception as e:
            self.fail(f"截图请求失败: {str(e)}")

    def test_05_capture_view_custom_size(self):
        """测试 5: 自定义尺寸截图"""
        print("\n🔍 测试 5: 自定义尺寸截图")

        custom_width = 800
        custom_height = 600

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

                dimensions = result['dimensions']
                print(f"      请求尺寸: {custom_width}x{custom_height}")
                print(f"      实际尺寸: {dimensions['width']}x{dimensions['height']}")
                print(f"      文件大小: {result['file_size']} 字节")

                # 验证尺寸是否符合要求
                self.assertEqual(dimensions['width'], custom_width)
                self.assertEqual(dimensions['height'], custom_height)
                self.assertEqual(result['format'], 'png')

            else:
                error = result.get('error', '未知错误')
                print(f"   ❌ 自定义尺寸截图失败: {error}")
                self.fail(f"自定义尺寸截图失败: {error}")

        except Exception as e:
            self.fail(f"自定义尺寸截图请求失败: {str(e)}")

    def test_06_capture_view_with_base64(self):
        """测试 6: 截图并返回 Base64 数据"""
        print("\n🔍 测试 6: 截图并返回 Base64 数据")

        def test_base64_capture():
            api = self.tools.get_api()
            return api._request('POST', '/api/view', {
                "parameters": {
                    "width": 400,
                    "height": 300,
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

    def test_07_invalid_parameters_handling(self):
        """测试 7: 无效参数处理"""
        print("\n🔍 测试 7: 无效参数处理")

        invalid_cases = [
            {
                "name": "宽度过小",
                "params": {"width": 50, "height": 600},
                "expect_error": "宽度必须在"
            },
            {
                "name": "宽度过大",
                "params": {"width": 5000, "height": 600},
                "expect_error": "宽度必须在"
            },
            {
                "name": "高度过小",
                "params": {"width": 600, "height": 50},
                "expect_error": "高度必须在"
            },
            {
                "name": "高度过大",
                "params": {"width": 600, "height": 5000},
                "expect_error": "高度必须在"
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

    def test_08_concurrent_capture_requests(self):
        """测试 8: 并发截图请求处理"""
        print("\n🔍 测试 8: 并发截图请求处理")

        import concurrent.futures
        import threading

        def single_capture(index):
            """单个截图请求"""
            try:
                api = self.tools.get_api()
                result = self.async_test(api._request('POST', '/api/view', {
                    "parameters": {
                        "width": 300 + index * 10,
                        "height": 200 + index * 10,
                        "filename": f"concurrent_test_{index}.png"
                    }
                }))
                return index, result
            except Exception as e:
                return index, {"success": False, "error": str(e)}

        print("      发起 3 个并发截图请求...")

        # 使用线程池执行并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(single_capture, i) for i in range(3)]
            results = []

            for future in concurrent.futures.as_completed(futures):
                index, result = future.result()
                results.append((index, result))

                if result.get('success'):
                    print(f"         ✅ 请求 {index} 成功")
                else:
                    print(f"         ❌ 请求 {index} 失败: {result.get('error')}")

        # 验证至少有一些请求成功
        success_count = sum(1 for _, result in results if result.get('success'))
        print(f"      并发测试完成: {success_count}/3 个请求成功")

        # 至少应该有一个请求成功（如果插件支持并发）
        # 或者所有请求都返回合理的错误信息
        self.assertGreater(success_count, 0, "所有并发请求都失败")


if __name__ == '__main__':
    unittest.main(verbosity=2)
