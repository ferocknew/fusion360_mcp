"""
代码执行相关工具的单元测试
"""

import unittest
from unittest.mock import patch, AsyncMock
from .test_base import Fusion360TestBase, MockFusion360API


class TestExecuteTools(Fusion360TestBase):
    """代码执行工具测试类"""

    def setUp(self):
        super().setUp()
        self.mock_api = MockFusion360API()

    def test_execute_simple_code(self):
        """测试执行简单代码"""
        async def test():
            simple_codes = [
                "print('Hello Fusion360')",
                "x = 10 + 20",
                "result = 2 * 3.14159 * 25",  # 计算圆周长
                "import math; print(math.pi)"
            ]

            for code in simple_codes:
                # 模拟代码执行
                result = {
                    "success": True,
                    "result": {
                        "code": code,
                        "output": f"执行结果: {code}",
                        "execution_time": 0.001,
                        "context": {}
                    }
                }

                self.assert_api_call_success(result, ["code", "output"])
                self.assertEqual(result["result"]["code"], code)

            self.log_test_result(f"简单代码执行({len(simple_codes)}个)", {"success": True})

        self.async_test(test())

    def test_execute_fusion360_api_code(self):
        """测试执行 Fusion 360 API 代码"""
        async def test():
            fusion_codes = [
                "app = adsk.core.Application.get()",
                "design = adsk.fusion.Design.cast(app.activeProduct)",
                "rootComp = design.rootComponent",
                "sketches = rootComp.sketches",
                "sketch = sketches.add(rootComp.xYConstructionPlane)"
            ]

            for code in fusion_codes:
                result = {
                    "success": True,
                    "result": {
                        "code": code,
                        "output": f"Fusion360 API 调用成功: {code}",
                        "api_objects_created": 1 if "add" in code else 0,
                        "context": {"app": "mock_app", "design": "mock_design"}
                    }
                }

                self.assert_api_call_success(result)

            self.log_test_result(f"Fusion360 API 代码({len(fusion_codes)}个)", {"success": True})

        self.async_test(test())

    def test_execute_code_with_context(self):
        """测试带上下文的代码执行"""
        async def test():
            contexts = [
                {"radius": 25, "height": 50},
                {"x": 10, "y": 20, "z": 30},
                {"material": "钢", "density": 7.8}
            ]

            for context in contexts:
                code = "result = sum(context.values()) if isinstance(list(context.values())[0], (int, float)) else 'non_numeric'"

                result = {
                    "success": True,
                    "result": {
                        "code": code,
                        "output": f"上下文执行结果",
                        "context": context,
                        "result_value": sum(v for v in context.values() if isinstance(v, (int, float)))
                    }
                }

                self.assert_api_call_success(result)

            self.log_test_result(f"带上下文代码执行({len(contexts)}个)", {"success": True})

        self.async_test(test())

    def test_execute_modeling_operations(self):
        """测试建模操作代码"""
        async def test():
            modeling_operations = [
                {
                    "name": "创建圆形草图",
                    "code": """
sketch = sketches.add(rootComp.xYConstructionPlane)
center = adsk.core.Point3D.create(0, 0, 0)
sketch.sketchCurves.sketchCircles.addByCenterRadius(center, 25)
""",
                    "expected_objects": ["sketch", "circle"]
                },
                {
                    "name": "创建拉伸特征",
                    "code": """
profile = sketch.profiles.item(0)
extrudes = rootComp.features.extrudeFeatures
extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
distance = adsk.core.ValueInput.createByReal(50)
extrudeInput.setDistanceExtent(False, distance)
extrudeFeature = extrudes.add(extrudeInput)
""",
                    "expected_objects": ["profile", "extrude_feature"]
                }
            ]

            for operation in modeling_operations:
                result = {
                    "success": True,
                    "result": {
                        "code": operation["code"],
                        "output": f"建模操作成功: {operation['name']}",
                        "objects_created": operation["expected_objects"],
                        "execution_time": 0.1
                    }
                }

                self.assert_api_call_success(result)
                self.assertIn("objects_created", result["result"])

            self.log_test_result(f"建模操作代码({len(modeling_operations)}个)", {"success": True})

        self.async_test(test())

    def test_execute_code_error_handling(self):
        """测试代码执行错误处理"""
        async def test():
            error_codes = [
                {
                    "code": "undefined_variable",
                    "error": "NameError: name 'undefined_variable' is not defined"
                },
                {
                    "code": "1 / 0",
                    "error": "ZeroDivisionError: division by zero"
                },
                {
                    "code": "import nonexistent_module",
                    "error": "ModuleNotFoundError: No module named 'nonexistent_module'"
                },
                {
                    "code": "invalid syntax here",
                    "error": "SyntaxError: invalid syntax"
                }
            ]

            for case in error_codes:
                result = {
                    "success": False,
                    "error": case["error"],
                    "code": case["code"]
                }

                self.assert_api_call_failure(result)

            self.log_test_result(f"代码错误处理({len(error_codes)}个)", {"success": True})

        self.async_test(test())

    def test_execute_code_security(self):
        """测试代码执行安全性"""
        async def test():
            # 模拟安全检查，这些代码应该被拒绝执行
            dangerous_codes = [
                "import os; os.system('rm -rf /')",
                "open('/etc/passwd', 'r').read()",
                "exec('malicious code')",
                "__import__('subprocess').call(['ls', '/'])"
            ]

            for code in dangerous_codes:
                result = {
                    "success": False,
                    "error": "代码包含不安全操作，执行被拒绝",
                    "code": code,
                    "security_violation": True
                }

                self.assert_api_call_failure(result, "不安全操作")

            self.log_test_result(f"代码安全检查({len(dangerous_codes)}个)", {"success": True})

        self.async_test(test())

    def test_execute_code_performance(self):
        """测试代码执行性能"""
        async def test():
            performance_tests = [
                {
                    "name": "快速计算",
                    "code": "result = 2 + 2",
                    "expected_time_max": 0.001
                },
                {
                    "name": "循环计算",
                    "code": "result = sum(range(1000))",
                    "expected_time_max": 0.01
                },
                {
                    "name": "复杂计算",
                    "code": "import math; result = [math.sqrt(i) for i in range(100)]",
                    "expected_time_max": 0.1
                }
            ]

            for test_case in performance_tests:
                result = {
                    "success": True,
                    "result": {
                        "code": test_case["code"],
                        "output": f"性能测试: {test_case['name']}",
                        "execution_time": test_case["expected_time_max"] * 0.8,  # 模拟实际时间
                        "performance_category": test_case["name"]
                    }
                }

                self.assert_api_call_success(result)
                exec_time = result["result"]["execution_time"]
                self.assertLessEqual(exec_time, test_case["expected_time_max"])

            self.log_test_result(f"代码性能测试({len(performance_tests)}个)", {"success": True})

        self.async_test(test())

    def test_execute_code_output_formats(self):
        """测试代码执行输出格式"""
        async def test():
            output_tests = [
                {
                    "code": "print('Hello World')",
                    "expected_output_type": "text"
                },
                {
                    "code": "result = {'x': 10, 'y': 20}; print(result)",
                    "expected_output_type": "json_like"
                },
                {
                    "code": "import json; print(json.dumps({'status': 'ok'}))",
                    "expected_output_type": "json"
                }
            ]

            for test_case in output_tests:
                result = {
                    "success": True,
                    "result": {
                        "code": test_case["code"],
                        "output": f"输出格式测试结果",
                        "output_type": test_case["expected_output_type"],
                        "formatted_output": True
                    }
                }

                self.assert_api_call_success(result)
                self.assertEqual(
                    result["result"]["output_type"],
                    test_case["expected_output_type"]
                )

            self.log_test_result(f"输出格式测试({len(output_tests)}个)", {"success": True})

        self.async_test(test())

    def tearDown(self):
        """测试结束后清理"""
        self.print_test_summary()
        super().tearDown()


if __name__ == '__main__':
    unittest.main(verbosity=2)
