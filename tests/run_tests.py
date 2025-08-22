#!/usr/bin/env python3
"""
Fusion360 MCP 测试运行器
"""

import unittest
import sys
import os
import time
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入所有测试模块
from tests.test_document_tools import TestDocumentTools
from tests.test_object_tools import TestObjectTools
from tests.test_part_tools import TestPartTools
from tests.test_view_tools import TestViewTools
from tests.test_execute_tools import TestExecuteTools


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.test_suites = {
            "文档工具": TestDocumentTools,
            "对象工具": TestObjectTools,
            "零件工具": TestPartTools,
            "视图工具": TestViewTools,
            "代码执行": TestExecuteTools
        }
        self.results = {}

    def run_single_suite(self, suite_name: str, test_class) -> Dict[str, Any]:
        """运行单个测试套件"""
        print(f"\n{'='*60}")
        print(f"🧪 运行测试套件: {suite_name}")
        print(f"{'='*60}")

        # 创建测试套件
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)

        # 运行测试
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True
        )

        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()

        # 收集结果
        suite_result = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
            "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1) * 100,
            "execution_time": end_time - start_time,
            "failure_details": result.failures,
            "error_details": result.errors
        }

        return suite_result

    def run_all_tests(self) -> None:
        """运行所有测试"""
        print("🚀 Fusion360 MCP 工具测试开始")
        print(f"测试套件数量: {len(self.test_suites)}")

        total_start_time = time.time()

        # 运行每个测试套件
        for suite_name, test_class in self.test_suites.items():
            try:
                result = self.run_single_suite(suite_name, test_class)
                self.results[suite_name] = result
            except Exception as e:
                print(f"❌ 测试套件 {suite_name} 运行失败: {e}")
                self.results[suite_name] = {
                    "tests_run": 0,
                    "failures": 0,
                    "errors": 1,
                    "skipped": 0,
                    "success_rate": 0,
                    "execution_time": 0,
                    "error_details": [str(e)]
                }

        total_end_time = time.time()

        # 打印总结报告
        self.print_summary_report(total_end_time - total_start_time)

    def run_specific_tests(self, test_names: List[str]) -> None:
        """运行指定的测试"""
        print(f"🎯 运行指定测试: {', '.join(test_names)}")

        total_start_time = time.time()

        for test_name in test_names:
            if test_name in self.test_suites:
                try:
                    result = self.run_single_suite(test_name, self.test_suites[test_name])
                    self.results[test_name] = result
                except Exception as e:
                    print(f"❌ 测试 {test_name} 运行失败: {e}")
            else:
                print(f"⚠️  测试 {test_name} 不存在")
                available_tests = list(self.test_suites.keys())
                print(f"可用测试: {', '.join(available_tests)}")

        total_end_time = time.time()
        self.print_summary_report(total_end_time - total_start_time)

    def print_summary_report(self, total_time: float) -> None:
        """打印总结报告"""
        print(f"\n{'='*80}")
        print("📊 测试总结报告")
        print(f"{'='*80}")

        total_tests = sum(r["tests_run"] for r in self.results.values())
        total_failures = sum(r["failures"] for r in self.results.values())
        total_errors = sum(r["errors"] for r in self.results.values())
        total_skipped = sum(r["skipped"] for r in self.results.values())

        overall_success_rate = (total_tests - total_failures - total_errors) / max(total_tests, 1) * 100

        print(f"总测试数量: {total_tests}")
        print(f"成功: {total_tests - total_failures - total_errors}")
        print(f"失败: {total_failures}")
        print(f"错误: {total_errors}")
        print(f"跳过: {total_skipped}")
        print(f"成功率: {overall_success_rate:.1f}%")
        print(f"总执行时间: {total_time:.2f}秒")

        print(f"\n📋 各测试套件详情:")
        print("-" * 80)

        for suite_name, result in self.results.items():
            status_icon = "✅" if result["failures"] == 0 and result["errors"] == 0 else "❌"
            print(f"{status_icon} {suite_name:15} | "
                  f"测试: {result['tests_run']:2d} | "
                  f"成功率: {result['success_rate']:5.1f}% | "
                  f"时间: {result['execution_time']:5.2f}s")

        # 如果有失败或错误，显示详情
        if total_failures > 0 or total_errors > 0:
            print(f"\n🔍 失败和错误详情:")
            print("-" * 80)

            for suite_name, result in self.results.items():
                if result["failures"] or result["errors"]:
                    print(f"\n❌ {suite_name}:")

                    for failure in result.get("failure_details", []):
                        print(f"  失败: {failure[0]}")
                        print(f"       {failure[1].split('AssertionError:')[-1].strip()}")

                    for error in result.get("error_details", []):
                        print(f"  错误: {error[0]}")
                        print(f"       {error[1].split('Exception:')[-1].strip()}")

        # 最终状态
        if overall_success_rate == 100:
            print(f"\n🎉 所有测试通过！")
        elif overall_success_rate >= 80:
            print(f"\n👍 大部分测试通过，成功率: {overall_success_rate:.1f}%")
        else:
            print(f"\n⚠️  需要关注，成功率较低: {overall_success_rate:.1f}%")

        print(f"{'='*80}")


def print_help():
    """打印帮助信息"""
    print("🔧 Fusion360 MCP 测试运行器")
    print("=" * 50)
    print("用法:")
    print("  python run_tests.py [options] [test_names...]")
    print()
    print("选项:")
    print("  --help, -h     显示此帮助信息")
    print("  --list, -l     列出所有可用的测试套件")
    print("  --all, -a      运行所有测试 (默认)")
    print()
    print("测试套件:")
    runner = TestRunner()
    for name in runner.test_suites.keys():
        print(f"  {name}")
    print()
    print("示例:")
    print("  python run_tests.py                    # 运行所有测试")
    print("  python run_tests.py 文档工具          # 运行文档工具测试")
    print("  python run_tests.py 文档工具 对象工具  # 运行指定的多个测试")


def main():
    """主函数"""
    args = sys.argv[1:]

    # 处理帮助参数
    if "--help" in args or "-h" in args:
        print_help()
        return

    # 创建测试运行器
    runner = TestRunner()

    # 处理列表参数
    if "--list" in args or "-l" in args:
        print("📋 可用的测试套件:")
        for name in runner.test_suites.keys():
            print(f"  • {name}")
        return

    # 过滤参数
    test_names = [arg for arg in args if not arg.startswith('-')]

    # 运行测试
    if not test_names or "--all" in args or "-a" in args:
        runner.run_all_tests()
    else:
        runner.run_specific_tests(test_names)


if __name__ == "__main__":
    main()
