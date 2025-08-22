import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# 全局变量
app = None
ui = None
http_server = None
server_thread = None


class SimpleFusion360Handler(BaseHTTPRequestHandler):
    """简单的 Fusion360 HTTP 请求处理器"""

    def do_GET(self):
        """处理 GET 请求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            
            if path == '/api/health':
                result = {"status": "healthy", "message": "Fusion 360 插件运行正常"}
            elif path == '/api/status':
                result = get_simple_status()
            elif path == '/api/objects':
                result = get_simple_objects()
            else:
                result = {"success": False, "error": f"未知路径: {path}"}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"错误: {str(e)}")

    def do_POST(self):
        """处理 POST 请求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            
            # 读取数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8')) if post_data else {}

            if path == '/api/document':
                result = create_simple_document(data)
            elif path == '/api/object':
                result = create_simple_object(data)
            else:
                result = {"success": False, "error": f"未知路径: {path}"}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def log_message(self, format, *args):
        """禁用日志"""
        pass


def get_simple_status():
    """获取简单状态"""
    try:
        if not app:
            return {"success": False, "error": "应用未初始化"}
        
        return {
            "success": True,
            "app_name": app.productName,
            "version": app.version,
            "active_document": app.activeDocument.name if app.activeDocument else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_simple_objects():
    """获取简单对象列表"""
    try:
        if not app or not app.activeDocument:
            return {"success": False, "error": "没有活动文档"}
        
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {"success": False, "error": "不是设计环境"}
        
        objects = []
        rootComp = design.rootComponent
        
        for i, body in enumerate(rootComp.bRepBodies):
            if i >= 5:  # 限制数量
                break
            objects.append({
                "id": body.entityToken,
                "name": body.name or f"实体{i+1}",
                "type": "body",
                "visible": body.isVisible
            })
        
        return {"success": True, "objects": objects}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_simple_document(data):
    """创建简单文档"""
    try:
        parameters = data.get('parameters', {})
        name = parameters.get('name', '新文档')
        
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        if doc:
            doc.name = name
            return {"success": True, "document_id": doc.name}
        else:
            return {"success": False, "error": "创建失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_simple_object(data):
    """创建简单对象"""
    try:
        parameters = data.get('parameters', {})
        object_type = parameters.get('type')
        obj_params = parameters.get('parameters', {})
        
        if object_type == 'extrude' and obj_params.get('base_feature') == 'circle':
            return create_simple_cylinder(obj_params)
        else:
            return {"success": False, "error": f"不支持: {object_type}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_simple_cylinder(params):
    """创建简单圆柱"""
    try:
        if not app or not app.activeDocument:
            return {"success": False, "error": "没有活动文档"}
            
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {"success": False, "error": "不是设计环境"}
        
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        
        radius = float(params.get('radius', 2.5))
        center = adsk.core.Point3D.create(0, 0, 0)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
        
        profile = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        height = float(params.get('height', 5.0))
        distance = adsk.core.ValueInput.createByReal(height)
        extrudeInput.setDistanceExtent(False, distance)
        
        extrudeFeature = extrudes.add(extrudeInput)
        
        return {
            "success": True,
            "object_id": extrudeFeature.entityToken,
            "type": "extrude",
            "parameters": params
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def start_http_server():
    """启动 HTTP 服务器"""
    global http_server, server_thread
    
    try:
        http_server = HTTPServer(('localhost', 9000), SimpleFusion360Handler)
        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        if ui:
            ui.messageBox("HTTP 服务器已启动在端口 9000")
    except Exception as e:
        if ui:
            ui.messageBox(f"启动失败: {str(e)}")


def stop_http_server():
    """停止 HTTP 服务器"""
    global http_server, server_thread
    
    try:
        if http_server:
            http_server.shutdown()
            http_server.server_close()
            http_server = None
            
        if server_thread:
            server_thread.join(timeout=1)
            server_thread = None
            
        if ui:
            ui.messageBox("HTTP 服务器已停止")
    except Exception as e:
        if ui:
            ui.messageBox(f"停止失败: {str(e)}")


def run(context):
    """插件入口"""
    global app, ui
    
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        start_http_server()
    except:
        if ui:
            ui.messageBox('启动失败:\n{}'.format(traceback.format_exc()))


def stop(context):
    """插件停止"""
    global app, ui
    
    try:
        stop_http_server()
    except:
        if ui:
            ui.messageBox('停止失败:\n{}'.format(traceback.format_exc()))
