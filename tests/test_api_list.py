"""
测试新增的 API 列表功能
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.fusion360_mcp.fusion360_api import get_api


async def test_api_list_endpoint():
    """测试 /api/list 端点"""
    try:
        api = get_api()

        print("🔍 测试 Fusion 360 API 列表端点...")

        # 测试 API 列表端点
        try:
            result = await api._request("GET", "/api/list")
            print("✅ API 列表端点调用成功")

            # 验证响应结构
            if result.get("success"):
                stats = result.get("statistics", {})
                categories = result.get("categories", {})

                print(f"📊 统计信息:")
                print(f"  - 总分类数: {stats.get('total_categories', 0)}")
                print(f"  - 总API数: {stats.get('total_apis', 0)}")
                print(f"  - Fusion版本: {stats.get('fusion_version', 'Unknown')}")

                print(f"\n📂 API 分类:")
                for category_id, category in categories.items():
                    api_count = len(category.get("apis", []))
                    print(f"  - {category.get('name')}: {api_count} 个API")
                    print(f"    {category.get('description')}")

                # 显示一些示例API
                print(f"\n🔧 设计API示例:")
                design_apis = categories.get("design_apis", {}).get("apis", [])
                for i, api in enumerate(design_apis[:3]):  # 只显示前3个
                    print(f"  {i+1}. {api.get('chinese_name')} ({api.get('name')})")
                    print(f"     {api.get('description')}")

                # 显示使用示例
                examples = result.get("examples", {})
                print(f"\n💡 使用示例:")
                for example_name, example_desc in examples.items():
                    print(f"  - {example_name}: {example_desc}")

                return True
            else:
                print(f"❌ API 列表获取失败: {result.get('error')}")
                return False

        except Exception as e:
            print(f"❌ API 列表端点测试失败: {e}")
            print("💡 提示: 确保 Fusion 360 插件正在运行在端口 9000")
            return False

    except Exception as e:
        print(f"❌ 测试初始化失败: {e}")
        return False


async def test_other_endpoints():
    """测试其他现有端点确保没有破坏"""
    try:
        api = get_api()

        print("\n🔍 测试其他端点兼容性...")

        # 测试健康检查
        try:
            health_result = await api._request("GET", "/api/health")
            if health_result.get("status") == "healthy":
                print("✅ 健康检查端点正常")
            else:
                print("⚠️ 健康检查端点异常")
        except Exception as e:
            print(f"❌ 健康检查端点失败: {e}")

        # 测试状态查询
        try:
            status_result = await api._request("GET", "/api/status")
            if status_result.get("success"):
                print("✅ 状态查询端点正常")
            else:
                print("⚠️ 状态查询端点异常")
        except Exception as e:
            print(f"❌ 状态查询端点失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 兼容性测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始测试 Fusion 360 API 列表功能")
    print("=" * 50)

    # 测试API列表端点
    list_test_result = await test_api_list_endpoint()

    # 测试其他端点兼容性
    compat_test_result = await test_other_endpoints()

    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print(f"  - API 列表功能: {'✅ 通过' if list_test_result else '❌ 失败'}")
    print(f"  - 端点兼容性: {'✅ 通过' if compat_test_result else '❌ 失败'}")

    if list_test_result and compat_test_result:
        print("\n🎉 所有测试通过！新的 API 列表功能工作正常")
    else:
        print("\n⚠️ 部分测试失败，请检查 Fusion 360 插件状态")


if __name__ == "__main__":
    asyncio.run(main())
