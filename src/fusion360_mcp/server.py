"""
FastMCP 服务器配置和初始化
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from .config import get_settings
from . import tools


logger = logging.getLogger(__name__)


# 创建 FastMCP 应用实例
app = FastMCP("Fusion360 MCP Server")


# 数据模型定义
class DocumentRequest(BaseModel):
    """创建文档请求"""
    name: Optional[str] = None
    template: Optional[str] = None
    units: str = "mm"


class ObjectRequest(BaseModel):
    """对象操作请求"""
    object_type: str
    parameters: Dict[str, Any]
    position: Optional[List[float]] = None
    rotation: Optional[List[float]] = None


class CodeRequest(BaseModel):
    """代码执行请求"""
    code: str
    context: Optional[Dict[str, Any]] = None


class ViewRequest(BaseModel):
    """视图请求"""
    camera_position: Optional[List[float]] = None
    target_position: Optional[List[float]] = None
    format: str = "png"
    width: int = 1920
    height: int = 1080


# 注册 MCP 工具
@app.tool()
async def create_document(request: DocumentRequest) -> Dict[str, Any]:
    """在 Fusion 360 中创建新文档"""
    try:
        result = await tools.create_document(
            name=request.name,
            template=request.template,
            units=request.units
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"创建文档失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def create_object(request: ObjectRequest) -> Dict[str, Any]:
    """在 Fusion 360 中创建新对象"""
    try:
        result = await tools.create_object(
            object_type=request.object_type,
            parameters=request.parameters,
            position=request.position,
            rotation=request.rotation
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"创建对象失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def edit_object(object_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """在 Fusion 360 中编辑对象"""
    try:
        result = await tools.edit_object(object_id, parameters)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"编辑对象失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def delete_object(object_id: str) -> Dict[str, Any]:
    """在 Fusion 360 中删除对象"""
    try:
        result = await tools.delete_object(object_id)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"删除对象失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def execute_code(request: CodeRequest) -> Dict[str, Any]:
    """在 Fusion 360 中执行任意 Python 代码"""
    try:
        result = await tools.execute_code(request.code, request.context)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"执行代码失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def insert_part_from_library(library_name: str, part_name: str, position: Optional[List[float]] = None) -> Dict[str, Any]:
    """从零件库中插入零件"""
    try:
        result = await tools.insert_part_from_library(library_name, part_name, position)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"插入零件失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def get_view(request: ViewRequest) -> Dict[str, Any]:
    """获取活动视图的截图"""
    try:
        result = await tools.get_view(
            camera_position=request.camera_position,
            target_position=request.target_position,
            format=request.format,
            width=request.width,
            height=request.height
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"获取视图失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def get_objects() -> Dict[str, Any]:
    """获取文档中的所有对象"""
    try:
        result = await tools.get_objects()
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"获取对象列表失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def get_object(object_id: str) -> Dict[str, Any]:
    """获取文档中的特定对象"""
    try:
        result = await tools.get_object(object_id)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"获取对象失败: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def get_parts_list() -> Dict[str, Any]:
    """获取零件库中的零件列表"""
    try:
        result = await tools.get_parts_list()
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"获取零件列表失败: {e}")
        return {"success": False, "error": str(e)}


# 添加服务器信息
@app.get("/")
async def root():
    """根路径信息"""
    settings = get_settings()
    return {
        "name": settings.mcp_server_name,
        "version": settings.mcp_server_version,
        "description": "Fusion360 LLM 建模助手 - 基于 FastMCP 和 Fusion 360 API 的语义化建模系统",
        "tools_count": len(app.list_tools()),
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "服务器运行正常"}


# 启动时的日志
@app.on_event("startup")
async def startup_event():
    """启动事件"""
    settings = get_settings()
    logger.info(f"Fusion360 MCP 服务器启动完成")
    logger.info(f"服务器名称: {settings.mcp_server_name}")
    logger.info(f"服务器版本: {settings.mcp_server_version}")
    logger.info(f"已注册工具数量: {len(app.list_tools())}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("Fusion360 MCP 服务器正在关闭...")
