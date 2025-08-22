"""
Fusion360 MCP Addin - 改进版本
基于官方 demo 结构的标准插件实现
"""

import adsk.core
import adsk.fusion
import traceback
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# 全局变量
app = None
ui = None
http_server = None
server_thread = None

# 配置
ADDIN_NAME = "Fusion360 MCP Addin"
HTTP_PORT = 9000
HTTP_HOST = 'localhost'


def log_message(message):
    """简单的日志记录"""
    try:
        if ui:
            # 在 Fusion 360 的文本面板中显示消息
            palettes = ui.palettes
            text_palette = palettes.itemById('TextCommands')
            if text_palette:
                text_palette.writeText(f"[MCP] {message}")
    except:
        pass  # 忽略日志错误


def handle_error(error_name, show_message=True):
    """标准错误处理"""
    error_message = traceback.format_exc()
    log_message(f"Error in {error_name}: {error_message}")

    if show_message and ui:
        ui.messageBox(f'{error_name} 失败:\n{error_message}')


class MCPRequestHandler(BaseHTTPRequestHandler):
    """MCP HTTP 请求处理器"""

    def do_GET(self):
        """处理 GET 请求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            log_message(f"GET 请求: {path}")

            # 路由分发
            if path == '/api/health':
                result = {"status": "healthy", "message": f"{ADDIN_NAME} 运行正常"}
            elif path == '/api/status':
                result = get_fusion_status()
            elif path == '/api/objects':
                result = get_fusion_objects()
            else:
                result = {"success": False, "error": f"未知路径: {path}"}

            # 返回 JSON 响应
            self.send_json_response(200, result)

        except Exception as e:
            log_message(f"GET 请求处理失败: {str(e)}")
            self.send_json_response(500, {"success": False, "error": str(e)})

    def do_POST(self):
        """处理 POST 请求"""
        try:
            path = urllib.parse.urlparse(self.path).path

            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8')) if post_data else {}

            log_message(f"POST 请求: {path}, 数据: {data}")

            # 路由分发
            if path == '/api/document':
                result = create_fusion_document(data)
            elif path == '/api/object':
                result = create_fusion_object(data)
            else:
                result = {"success": False, "error": f"未知路径: {path}"}

            # 返回 JSON 响应
            self.send_json_response(200, result)

        except Exception as e:
            log_message(f"POST 请求处理失败: {str(e)}")
            self.send_json_response(500, {"success": False, "error": str(e)})

    def send_json_response(self, status_code, data):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        """禁用 HTTP 服务器默认日志"""
        pass


def get_fusion_status():
    """获取 Fusion 360 状态"""
    try:
        if not app:
            return {"success": False, "error": "应用未初始化"}

        status = {
            "success": True,
            "app_name": app.productName,
            "version": app.version,
            "active_document": None,
            "design_workspace": False
        }

        # 检查活动文档
        if app.activeDocument:
            status["active_document"] = app.activeDocument.name

            # 检查是否在设计工作空间
            if app.activeProduct:
                design = adsk.fusion.Design.cast(app.activeProduct)
                status["design_workspace"] = design is not None

        return status

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_fusion_objects():
    """获取 Fusion 360 对象列表"""
    try:
        if not app or not app.activeDocument:
            return {"success": False, "error": "没有活动文档"}

        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {"success": False, "error": "当前不在设计工作空间"}

        objects = []
        rootComp = design.rootComponent

        # 获取实体（限制数量避免响应过大）
        for i, body in enumerate(rootComp.bRepBodies):
            if i >= 10:  # 最多返回 10 个对象
                break

            objects.append({
                "id": body.entityToken,
                "name": body.name if body.name else f"实体{i+1}",
                "type": "body",
                "visible": body.isVisible,
                "material": body.material.name if body.material else "默认"
            })

        return {"success": True, "objects": objects, "count": len(objects)}

    except Exception as e:
        return {"success": False, "error": str(e)}


def create_fusion_document(data):
    """创建 Fusion 360 文档"""
    try:
        parameters = data.get('parameters', {})
        name = parameters.get('name', '新建文档')

        # 创建新的设计文档
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)

        if doc:
            doc.name = name
            log_message(f"成功创建文档: {name}")
            return {
                "success": True,
                "document_id": doc.name,
                "document_name": doc.name
            }
        else:
            return {"success": False, "error": "文档创建失败"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def create_fusion_object(data):
    """创建 Fusion 360 对象"""
    try:
        parameters = data.get('parameters', {})
        object_type = parameters.get('type')
        obj_params = parameters.get('parameters', {})

        # 目前只支持简单的拉伸圆柱体
        if object_type == 'extrude' and obj_params.get('base_feature') == 'circle':
            return create_cylinder(obj_params)
        else:
            return {
                "success": False,
                "error": f"不支持的对象类型: {object_type}",
                "supported_types": ["extrude (circle base)"]
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


def create_cylinder(params):
    """创建圆柱体"""
    try:
        if not app or not app.activeDocument:
            return {"success": False, "error": "没有活动文档"}

        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {"success": False, "error": "当前不在设计工作空间"}

        rootComp = design.rootComponent

        # 创建草图
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)

        # 创建圆形轮廓
        radius = float(params.get('radius', 2.5))
        center = adsk.core.Point3D.create(0, 0, 0)
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)

        # 创建拉伸特征
        profile = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # 设置拉伸距离
        height = float(params.get('height', 5.0))
        distance = adsk.core.ValueInput.createByReal(height)
        extrudeInput.setDistanceExtent(False, distance)

        # 执行拉伸
        extrudeFeature = extrudes.add(extrudeInput)

        log_message(f"成功创建圆柱体: 半径={radius}, 高度={height}")

        return {
            "success": True,
            "object_id": extrudeFeature.entityToken,
            "type": "extrude",
            "geometry": {
                "radius": radius,
                "height": height
            },
            "parameters": params
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def start_http_server():
    """启动 HTTP 服务器"""
    global http_server, server_thread

    try:
        log_message(f"正在启动 HTTP 服务器: {HTTP_HOST}:{HTTP_PORT}")

        # 创建 HTTP 服务器
        http_server = HTTPServer((HTTP_HOST, HTTP_PORT), MCPRequestHandler)

        # 在后台线程运行服务器
        server_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        server_thread.start()

        log_message(f"HTTP 服务器已启动在 {HTTP_HOST}:{HTTP_PORT}")

        if ui:
            ui.messageBox(f"{ADDIN_NAME} HTTP 服务器已启动\n地址: http://{HTTP_HOST}:{HTTP_PORT}")

    except Exception as e:
        handle_error('start_http_server')


def stop_http_server():
    """停止 HTTP 服务器"""
    global http_server, server_thread

    try:
        log_message("正在停止 HTTP 服务器")

        if http_server:
            http_server.shutdown()
            http_server.server_close()
            http_server = None

        if server_thread:
            server_thread.join(timeout=1)
            server_thread = None

        log_message("HTTP 服务器已停止")

    except Exception as e:
        handle_error('stop_http_server', show_message=False)


def run(context):
    """插件主入口函数"""
    global app, ui

    try:
        # 获取应用和用户界面对象
        app = adsk.core.Application.get()
        ui = app.userInterface

        log_message(f"=== {ADDIN_NAME} 启动 ===")
        log_message(f"Fusion 360 版本: {app.version}")

        # 启动 HTTP 服务器
        start_http_server()

        log_message(f"=== {ADDIN_NAME} 启动完成 ===")

    except Exception as e:
        handle_error('run')


def stop(context):
    """插件停止函数"""
    global app, ui

    try:
        log_message(f"=== {ADDIN_NAME} 停止 ===")

        # 停止 HTTP 服务器
        stop_http_server()

        log_message(f"=== {ADDIN_NAME} 停止完成 ===")

    except Exception as e:
        handle_error('stop')
