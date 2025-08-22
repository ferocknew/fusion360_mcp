#!/usr/bin/env python3
"""
快速测试启动脚本
"""

import subprocess
import sys
import os

def main():
    """主函数"""
    print("🚀 Fusion360 MCP 快速测试")
    print("=" * 50)

    # 检查是否在项目根目录
    if not os.path.exists("src/fusion360_mcp"):
        print("❌ 请在项目根目录运行此脚本")
        return 1

    print("📋 可用的测试:")
    print("1. 简单集成测试 (推荐)")
    print("2. 完整集成测试")
    print("3. 文档工具测试")
    print("4. 检查端口状态")

    choice = input("\n请选择测试 (1-4): ").strip()

    if choice == "1":
        print("\n🧪 运行简单集成测试...")
        cmd = [sys.executable, "tests/test_simple_integration.py"]
    elif choice == "2":
        print("\n🧪 运行完整集成测试...")
        cmd = [sys.executable, "tests/test_real_integration.py"]
    elif choice == "3":
        print("\n🧪 运行文档工具测试...")
        cmd = [sys.executable, "tests/test_document_tools.py"]
    elif choice == "4":
        print("\n🔍 检查端口状态...")
        cmd = [sys.executable, "scripts/check_ports.py"]
    else:
        print("❌ 无效选择")
        return 1

    # 运行选择的测试
    try:
        result = subprocess.run(cmd, cwd=".")
        return result.returncode
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 运行测试失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
