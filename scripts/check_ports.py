#!/usr/bin/env python3
"""
端口检查脚本 - 检查 Fusion360 MCP 所需端口是否可用
"""

import socket
import subprocess
import sys
import platform


def check_port(host: str, port: int) -> bool:
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        return result == 0  # 0 表示端口被占用
    except Exception:
        return False
    finally:
        sock.close()


def get_port_process(port: int) -> str:
    """获取占用端口的进程信息"""
    try:
        if platform.system() == "Windows":
            cmd = f"netstat -ano | findstr :{port}"
        else:
            cmd = f"lsof -i :{port}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.stdout else "未找到进程信息"
    except Exception as e:
        return f"获取进程信息失败: {e}"


def main():
    """主函数"""
    print("🔍 Fusion360 MCP 端口检查")
    print("=" * 50)

    ports_to_check = [
        (8000, "MCP 服务器 (MCP协议)", "可配置，供LLM客户端连接"),
        (9000, "Fusion 360 插件HTTP服务", "固定，接收MCP服务器请求")
    ]

    all_clear = True

    for port, service, note in ports_to_check:
        print(f"\n📡 检查端口 {port} ({service})")
        print(f"   说明: {note}")

        is_occupied = check_port("localhost", port)

        if is_occupied:
            print(f"   状态: ❌ 端口被占用")
            process_info = get_port_process(port)
            print(f"   进程: {process_info}")
            all_clear = False

            if port == 9000:
                print(f"   ⚠️  警告: Fusion 360 插件HTTP服务端口被占用！")
                print(f"   建议: 关闭占用端口 9000 的应用程序")
                print(f"   说明: 此端口用于MCP服务器与Fusion 360插件的HTTP通信")
            else:
                print(f"   建议: 可使用 --port 参数指定其他端口")
                print(f"   说明: 此端口用于LLM客户端与MCP服务器的MCP协议通信")
        else:
            print(f"   状态: ✅ 端口可用")

    print("\n" + "=" * 50)

    if all_clear:
        print("🎉 所有端口都可用，可以启动 Fusion360 MCP 系统！")
        print("\n启动步骤:")
        print("1. 启动 MCP 服务器: fusion360_mcp")
        print("2. 在 Fusion 360 中加载插件")
        print("3. 验证连接:")
        print("   - curl http://localhost:8000/health")
        print("   - curl http://localhost:9000/api/health")
    else:
        print("⚠️  发现端口冲突，请先解决端口占用问题")
        print("\n解决方案:")
        print("• 关闭占用端口的应用程序")
        print("• 对于端口 8000: 可使用 --port 参数指定其他端口")
        print("• 对于端口 9000: 必须释放，因为 Fusion 360 插件端口不可更改")

        print("\n查看端口占用详情:")
        if platform.system() == "Windows":
            print("• netstat -ano | findstr :8000")
            print("• netstat -ano | findstr :9000")
        else:
            print("• lsof -i :8000")
            print("• lsof -i :9000")

    return 0 if all_clear else 1


if __name__ == "__main__":
    sys.exit(main())
