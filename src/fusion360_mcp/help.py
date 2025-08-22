"""
帮助信息和工具简介模块
"""

import sys
from typing import List, Dict, Any


def print_version_info():
    """打印版本信息"""
    print("🚀 Fusion360 MCP Server")
    print("=" * 50)
    print(f"版本: 0.1.0")
    print(f"描述: 基于 FastMCP 和 Fusion 360 API 的语义化建模系统")
    print(f"Python: {sys.version}")
    print()


def print_tools_help():
    """打印工具帮助信息"""
    print("🔧 可用的 Fusion 360 工具")
    print("=" * 50)
    
    tools = [
        {
            "name": "create_document",
            "description": "在 Fusion 360 中创建新文档",
            "parameters": [
                {"name": "name", "type": "str", "description": "文档名称", "optional": True},
                {"name": "template", "type": "str", "description": "模板类型", "optional": True},
                {"name": "units", "type": "str", "description": "单位系统 (mm/cm/m/in/ft)", "optional": True, "default": "mm"}
            ],
            "example": 'create_document(name="我的项目", units="mm")'
        },
        {
            "name": "create_object",
            "description": "在 Fusion 360 中创建新对象",
            "parameters": [
                {"name": "object_type", "type": "str", "description": "对象类型 (extrude/revolve)", "optional": False},
                {"name": "parameters", "type": "dict", "description": "对象参数", "optional": False},
                {"name": "position", "type": "list", "description": "位置坐标 [x,y,z]", "optional": True, "default": "[0,0,0]"},
                {"name": "rotation", "type": "list", "description": "旋转角度 [rx,ry,rz]", "optional": True, "default": "[0,0,0]"}
            ],
            "example": 'create_object("extrude", {"base_feature": "circle", "radius": 25, "height": 50})'
        },
        {
            "name": "edit_object", 
            "description": "在 Fusion 360 中编辑对象",
            "parameters": [
                {"name": "object_id", "type": "str", "description": "对象ID", "optional": False},
                {"name": "parameters", "type": "dict", "description": "新的参数", "optional": False}
            ],
            "example": 'edit_object("obj_123", {"radius": 30})'
        },
        {
            "name": "delete_object",
            "description": "在 Fusion 360 中删除对象", 
            "parameters": [
                {"name": "object_id", "type": "str", "description": "对象ID", "optional": False}
            ],
            "example": 'delete_object("obj_123")'
        },
        {
            "name": "execute_code",
            "description": "在 Fusion 360 中执行任意 Python 代码",
            "parameters": [
                {"name": "code", "type": "str", "description": "Python代码", "optional": False},
                {"name": "context", "type": "dict", "description": "执行上下文", "optional": True}
            ],
            "example": 'execute_code("print(\\"Hello Fusion360\\")")'
        },
        {
            "name": "insert_part_from_library",
            "description": "从零件库中插入零件",
            "parameters": [
                {"name": "library_name", "type": "str", "description": "库名称", "optional": False},
                {"name": "part_name", "type": "str", "description": "零件名称", "optional": False},
                {"name": "position", "type": "list", "description": "插入位置 [x,y,z]", "optional": True, "default": "[0,0,0]"}
            ],
            "example": 'insert_part_from_library("标准件", "螺栓M6x20")'
        },
        {
            "name": "get_view",
            "description": "获取活动视图的截图",
            "parameters": [
                {"name": "camera_position", "type": "list", "description": "相机位置 [x,y,z]", "optional": True},
                {"name": "target_position", "type": "list", "description": "目标位置 [x,y,z]", "optional": True},
                {"name": "format", "type": "str", "description": "图片格式", "optional": True, "default": "png"},
                {"name": "width", "type": "int", "description": "图片宽度", "optional": True, "default": "1920"},
                {"name": "height", "type": "int", "description": "图片高度", "optional": True, "default": "1080"}
            ],
            "example": 'get_view(width=800, height=600)'
        },
        {
            "name": "get_objects",
            "description": "获取文档中的所有对象",
            "parameters": [],
            "example": 'get_objects()'
        },
        {
            "name": "get_object",
            "description": "获取文档中的特定对象",
            "parameters": [
                {"name": "object_id", "type": "str", "description": "对象ID", "optional": False}
            ],
            "example": 'get_object("obj_123")'
        },
        {
            "name": "get_parts_list",
            "description": "获取零件库中的零件列表",
            "parameters": [],
            "example": 'get_parts_list()'
        }
    ]
    
    for tool in tools:
        print(f"\n🔹 {tool['name']}")
        print(f"   描述: {tool['description']}")
        
        if tool['parameters']:
            print("   参数:")
            for param in tool['parameters']:
                optional_text = " (可选)" if param['optional'] else " (必需)"
                default_text = f" 默认: {param.get('default', '')}" if param.get('default') else ""
                print(f"     - {param['name']} ({param['type']}){optional_text}: {param['description']}{default_text}")
        else:
            print("   参数: 无")
        
        print(f"   示例: {tool['example']}")
    
    print("\n" + "=" * 50)


def print_basic_shapes_help():
    """打印基本几何体帮助"""
    print("\n🔸 基本几何体快捷创建")
    print("-" * 30)
    
    shapes = [
        {
            "name": "圆柱体 (cylinder)",
            "parameters": ["radius (半径)", "height (高度)"],
            "example": 'create_primitive("cylinder", radius=25.0, height=50.0)'
        },
        {
            "name": "立方体 (box)",
            "parameters": ["length (长度)", "width (宽度)", "height (高度)"],
            "example": 'create_primitive("box", length=50.0, width=30.0, height=20.0)'
        },
        {
            "name": "球体 (sphere)",
            "parameters": ["radius (半径)"],
            "example": 'create_primitive("sphere", radius=20.0)'
        },
        {
            "name": "圆锥体 (cone)", 
            "parameters": ["base_radius (底面半径)", "top_radius (顶面半径)", "height (高度)"],
            "example": 'create_primitive("cone", base_radius=30.0, top_radius=10.0, height=40.0)'
        }
    ]
    
    for shape in shapes:
        print(f"\n  📐 {shape['name']}")
        print(f"     参数: {', '.join(shape['parameters'])}")
        print(f"     示例: {shape['example']}")


def print_usage_examples():
    """打印使用示例"""
    print("\n📚 使用示例")
    print("=" * 50)
    
    print("\n🚀 启动服务器:")
    print("   uvx --from fusion360-mcp fusion360_mcp")
    print("   或者:")
    print("   fusion360_mcp --host localhost --port 8000")
    
    print("\n🔧 查看工具帮助:")
    print("   fusion360_mcp --help-tools")
    
    print("\n📝 基本建模流程:")
    print("   1. 启动 Fusion 360")
    print("   2. 安装并启用 MCP 插件")
    print("   3. 启动 MCP 服务器")
    print("   4. 通过 LLM 或脚本调用 MCP 工具")
    
    print("\n🌐 API 端点:")
    print("   健康检查: GET http://localhost:8000/health")
    print("   服务器信息: GET http://localhost:8000/")
    print("   MCP 工具: POST http://localhost:8000/api/tools/<tool_name>")


def print_system_requirements():
    """打印系统要求"""
    print("\n⚙️  系统要求")
    print("=" * 50)
    print("• Python 3.11+")
    print("• Fusion 360 (最新版本)")
    print("• FastMCP 0.2.0+")
    print("• 支持的操作系统: Windows 10+, macOS 10.15+, Linux")
    print("• 内存: 4GB+ (推荐 8GB+)")
    print("• 网络: Fusion 360 插件与 MCP 服务器通信需要")


def show_full_help():
    """显示完整帮助信息"""
    print_version_info()
    print_tools_help()
    print_basic_shapes_help()
    print_usage_examples()
    print_system_requirements()
    
    print("\n💡 提示:")
    print("• 使用前请确保 Fusion 360 已启动并加载 MCP 插件")
    print("• 查看更多文档: https://github.com/yourusername/fusion360_mcp")
    print("• 报告问题: https://github.com/yourusername/fusion360_mcp/issues")


def show_quick_help():
    """显示快速帮助"""
    print_version_info()
    
    print("🔧 常用命令:")
    print("  fusion360_mcp                    # 启动服务器")
    print("  fusion360_mcp --help-tools       # 显示工具列表")
    print("  fusion360_mcp --port 9000        # 指定端口启动")
    print("  fusion360_mcp --version          # 显示版本")
    
    print("\n📖 获取完整帮助: fusion360_mcp --help-tools")


if __name__ == "__main__":
    show_full_help()
