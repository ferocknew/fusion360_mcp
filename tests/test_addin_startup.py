#!/usr/bin/env python3
"""
测试 Fusion360 MCP Addin 启动和基本功能
"""

import requests
import time
import json
import sys


def check_plugin_status():
    """检查插件是否启动"""
    try:
        response = requests.get("http://localhost:9000/api/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result.get("status") == "healthy"
        return False
    except Exception:
        return False


def wait_for_plugin(max_wait=30):
    """等待插件启动"""
    print("🔍 检查 Fusion360 MCP Addin 是否已启动...")
    
    for i in range(max_wait):
        if check_plugin_status():
            print("✅ 插件已启动！")
            return True
        
        if i == 0:
            print("❌ 插件未启动，请：")
            print("   1. 启动 Fusion 360")
            print("   2. 进入 工具 > 附加模块 > 开发")
            print("   3. 点击 '添加插件'")
            print("   4. 选择 addin/fusion360_mcp_addin/ 文件夹")
            print("   5. 确认插件运行")
            print()
            print(f"⏳ 等待插件启动... (最多等待 {max_wait} 秒)")
        
        print(f"   等待中... {i+1}/{max_wait}", end="\r")
        time.sleep(1)
    
    print(f"\n❌ 超时！插件在 {max_wait} 秒内未启动")
    return False


def run_basic_tests():
    """运行基本测试"""
    
    print("\n🧪 开始基本功能测试")
    print("=" * 50)
    
    tests = [
        {
            "name": "健康检查",
            "method": "GET",
            "url": "http://localhost:9000/api/health"
        },
        {
            "name": "状态查询", 
            "method": "GET",
            "url": "http://localhost:9000/api/status"
        },
        {
            "name": "对象列表",
            "method": "GET", 
            "url": "http://localhost:9000/api/objects"
        },
        {
            "name": "创建简单文档",
            "method": "POST",
            "url": "http://localhost:9000/api/document",
            "data": {
                "parameters": {
                    "name": "测试文档",
                    "units": "mm"
                }
            }
        },
        {
            "name": "创建简单圆柱体",
            "method": "POST",
            "url": "http://localhost:9000/api/object", 
            "data": {
                "parameters": {
                    "type": "extrude",
                    "parameters": {
                        "base_feature": "circle",
                        "radius": 25.0,
                        "height": 50.0
                    }
                }
            }
        }
    ]
    
    success_count = 0
    
    for i, test in enumerate(tests, 1):
        print(f"\n🔍 测试 {i}: {test['name']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            else:  # POST
                response = requests.post(
                    test['url'],
                    json=test.get('data', {}),
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功: {result}")
                success_count += 1
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
        
        # 测试间隔，避免过快的连续请求
        if i < len(tests):
            time.sleep(2)
    
    # 测试总结
    print(f"\n{'='*50}")
    print(f"📊 测试总结:")
    print(f"✅ 成功: {success_count}/{len(tests)}")
    print(f"❌ 失败: {len(tests) - success_count}/{len(tests)}")
    
    if success_count == len(tests):
        print("🎉 所有测试通过！插件工作正常")
        return True
    elif success_count > 0:
        print("⚠️  部分测试通过，插件部分功能可用")
        return True
    else:
        print("💥 所有测试失败，插件可能有问题")
        return False


def main():
    """主测试函数"""
    print("🧪 Fusion360 MCP Addin 启动测试")
    print("=" * 50)
    
    # 第一步：检查插件是否启动
    if not wait_for_plugin():
        print("\n💡 提示:")
        print("   1. 确保 Fusion 360 已启动")
        print("   2. 确保插件已正确加载")
        print("   3. 检查防火墙是否阻止了端口 9000")
        sys.exit(1)
    
    # 第二步：运行基本测试
    success = run_basic_tests()
    
    if not success:
        sys.exit(1)
    
    print("\n🎯 测试完成！插件已就绪，可以进行进一步开发和测试。")


if __name__ == '__main__':
    main()
