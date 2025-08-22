import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import json
import threading
import time
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add client module directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# 使用 MCPClient 和 fastmcp 通讯
from client import MCPClient

# 全局变量
app = None
ui = None
mcp_client = None
http_server = None
server_thread = None


class Fusion360Handler(BaseHTTPRequestHandler):
    """处理来自 MCP 服务器的 HTTP 请求"""
    
    def do_POST(self):
        """处理 POST 请求"""
        try:
            # 解析请求路径
            path = urllib.parse.urlparse(self.path).path
            
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if post_data:
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            # 根据路径分发请求
            if path == '/api/document':
                result = handle_document_request(data)
            elif path == '/api/object':
                result = handle_object_request(data)
            elif path.startswith('/api/object/'):
                object_id = path.split('/')[-1]
                result = handle_object_edit_request(object_id, data)
            elif path == '/api/execute':
                result = handle_execute_request(data)
            elif path == '/api/part':
                result = handle_part_request(data)
            elif path == '/api/view':
                result = handle_view_request(data)
            elif path == '/api/objects':
                result = handle_objects_request()
            elif path == '/api/parts':
                result = handle_parts_request()
            elif path == '/api/health':
                result = {"status": "healthy", "message": "Fusion 360 插件运行正常"}
            elif path == '/api/status':
                result = get_fusion360_status()
            else:
                result = {"success": False, "error": f"未知的 API 路径: {path}"}
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = json.dumps(result).encode('utf-8')
            self.wfile.write(response_data)
            
        except Exception as e:
            # 发送错误响应
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = {"success": False, "error": str(e)}
            response_data = json.dumps(error_response).encode('utf-8')
            self.wfile.write(response_data)
    
    def do_GET(self):
        """处理 GET 请求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            
            if path == '/api/objects':
                result = handle_objects_request()
            elif path.startswith('/api/object/'):
                object_id = path.split('/')[-1]
                result = handle_get_object_request(object_id)
            elif path == '/api/parts':
                result = handle_parts_request()
            elif path == '/api/health':
                result = {"status": "healthy", "message": "Fusion 360 插件运行正常"}
            elif path == '/api/status':
                result = get_fusion360_status()
            else:
                result = {"success": False, "error": f"未知的 API 路径: {path}"}
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = json.dumps(result).encode('utf-8')
            self.wfile.write(response_data)
            
        except Exception as e:
            # 发送错误响应
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = {"success": False, "error": str(e)}
            response_data = json.dumps(error_response).encode('utf-8')
            self.wfile.write(response_data)
    
    def do_DELETE(self):
        """处理 DELETE 请求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            
            if path.startswith('/api/object/'):
                object_id = path.split('/')[-1]
                result = handle_delete_object_request(object_id)
            else:
                result = {"success": False, "error": f"未知的 API 路径: {path}"}
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = json.dumps(result).encode('utf-8')
            self.wfile.write(response_data)
            
        except Exception as e:
            # 发送错误响应
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = {"success": False, "error": str(e)}
            response_data = json.dumps(error_response).encode('utf-8')
            self.wfile.write(response_data)
    
    def log_message(self, format, *args):
        """禁用默认日志输出"""
        pass


def handle_document_request(data):
    """处理文档创建请求"""
    try:
        parameters = data.get('parameters', {})
        name = parameters.get('name', '新建文档')
        template = parameters.get('template')
        units = parameters.get('units', 'mm')
        
        # 创建新文档
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        doc.name = name
        
        # 设置单位
        design = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        if design:
            design.fusionUnitsManager.distanceDisplayUnits = units
        
        return {
            "success": True,
            "document_id": doc.name,
            "name": name,
            "units": units
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_object_request(data):
    """处理对象创建请求"""
    try:
        parameters = data.get('parameters', {})
        object_type = parameters.get('type')
        obj_params = parameters.get('parameters', {})
        position = parameters.get('position', [0, 0, 0])
        
        if object_type == 'extrude':
            return create_extrude_feature(obj_params, position)
        elif object_type == 'revolve':
            return create_revolve_feature(obj_params, position)
        else:
            return {"success": False, "error": f"不支持的对象类型: {object_type}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_extrude_feature(params, position):
    """创建拉伸特征"""
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent
        
        # 创建草图
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        
        base_feature = params.get('base_feature', 'rectangle')
        
        if base_feature == 'circle':
            radius = params.get('radius', 2.5)
            center = adsk.core.Point3D.create(position[0], position[1], 0)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
        elif base_feature == 'rectangle':
            length = params.get('length', 5.0)
            width = params.get('width', 5.0)
            corner1 = adsk.core.Point3D.create(position[0] - length/2, position[1] - width/2, 0)
            corner2 = adsk.core.Point3D.create(position[0] + length/2, position[1] + width/2, 0)
            sketch.sketchCurves.sketchLines.addTwoPointRectangle(corner1, corner2)
        
        # 创建拉伸
        profile = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        height = params.get('height', 5.0)
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


def create_revolve_feature(params, position):
    """创建旋转特征"""
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent
        
        # 创建草图
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xZConstructionPlane)
        
        # 创建半圆轮廓
        radius = params.get('radius', 2.5)
        center = adsk.core.Point3D.create(position[0], 0, position[2])
        
        # 绘制半圆弧
        arc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(
            center,
            adsk.core.Point3D.create(position[0], radius, position[2]),
            3.14159  # 180 度
        )
        
        # 添加直线连接
        startPoint = arc.startSketchPoint.geometry
        endPoint = arc.endSketchPoint.geometry
        sketch.sketchCurves.sketchLines.addByTwoPoints(startPoint, endPoint)
        
        # 创建旋转
        profile = sketch.profiles.item(0)
        revolves = rootComp.features.revolveFeatures
        revolveInput = revolves.createInput(profile, rootComp.xConstructionAxis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        angle = adsk.core.ValueInput.createByReal(2 * 3.14159)  # 360 度
        revolveInput.setAngleExtent(False, angle)
        
        revolveFeature = revolves.add(revolveInput)
        
        return {
            "success": True,
            "object_id": revolveFeature.entityToken,
            "type": "revolve",
            "parameters": params
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_object_edit_request(object_id, data):
    """处理对象编辑请求"""
    try:
        # 这里可以实现对象编辑逻辑
        return {"success": True, "message": f"对象 {object_id} 编辑功能待实现"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_delete_object_request(object_id):
    """处理对象删除请求"""
    try:
        # 这里可以实现对象删除逻辑
        return {"success": True, "message": f"对象 {object_id} 删除功能待实现"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_execute_request(data):
    """处理代码执行请求"""
    try:
        code = data.get('parameters', {}).get('code', '')
        context = data.get('parameters', {}).get('context', {})
        
        # 为安全起见，这里只是返回接收到的代码，不实际执行
        return {
            "success": True,
            "message": "代码执行功能待实现",
            "code": code,
            "context": context
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_part_request(data):
    """处理零件插入请求"""
    try:
        parameters = data.get('parameters', {})
        library = parameters.get('library')
        part = parameters.get('part')
        position = parameters.get('position', [0, 0, 0])
        
        return {
            "success": True,
            "message": f"零件插入功能待实现: {library}/{part}",
            "position": position
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_view_request(data):
    """处理视图请求"""
    try:
        return {
            "success": True,
            "message": "视图截图功能待实现",
            "view_data": "base64_encoded_image_placeholder"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_objects_request():
    """处理获取对象列表请求"""
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {"success": True, "objects": []}
        
        rootComp = design.rootComponent
        objects = []
        
        # 获取所有实体
        for body in rootComp.bRepBodies:
            objects.append({
                "id": body.entityToken,
                "name": body.name,
                "type": "body",
                "visible": body.isVisible
            })
        
        return {"success": True, "objects": objects}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_get_object_request(object_id):
    """处理获取特定对象请求"""
    try:
        return {
            "success": True,
            "object": {
                "id": object_id,
                "name": f"对象_{object_id}",
                "type": "unknown",
                "properties": {}
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_parts_request():
    """处理获取零件列表请求"""
    try:
        return {
            "success": True,
            "parts": [
                {"library": "标准件", "name": "螺栓", "category": "紧固件"},
                {"library": "标准件", "name": "螺母", "category": "紧固件"},
                {"library": "标准件", "name": "垫圈", "category": "紧固件"}
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_fusion360_status():
    """获取 Fusion 360 状态"""
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        return {
            "status": "connected",
            "has_active_design": design is not None,
            "document_name": app.activeDocument.name if app.activeDocument else None,
            "version": app.version
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def start_http_server():
    """启动 HTTP 服务器"""
    global http_server, server_thread
    
    try:
        # 创建 HTTP 服务器
        server_address = ('localhost', 9000)
        http_server = HTTPServer(server_address, Fusion360Handler)
        
        # 在单独线程中运行服务器
        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        ui.messageBox(f"Fusion360 MCP 插件已启动\n服务器地址: http://{server_address[0]}:{server_address[1]}")
        
    except Exception as e:
        ui.messageBox(f"启动 HTTP 服务器失败: {str(e)}")


def stop_http_server():
    """停止 HTTP 服务器"""
    global http_server, server_thread
    
    try:
        if http_server:
            http_server.shutdown()
            http_server = None
        
        if server_thread:
            server_thread.join(timeout=1)
            server_thread = None
        
        ui.messageBox("Fusion360 MCP 插件已停止")
        
    except Exception as e:
        ui.messageBox(f"停止 HTTP 服务器失败: {str(e)}")


def run(context):
    """插件入口函数"""
    global app, ui, mcp_client
    
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # 初始化 MCP 客户端
        mcp_client = MCPClient("http://localhost:8000")
        
        # 启动 HTTP 服务器
        start_http_server()
        
    except:
        if ui:
            ui.messageBox('启动失败:\n{}'.format(traceback.format_exc()))


def stop(context):
    """插件停止函数"""
    global app, ui, mcp_client
    
    try:
        # 停止 HTTP 服务器
        stop_http_server()
        
        # 清理资源
        mcp_client = None
        
    except:
        if ui:
            ui.messageBox('停止失败:\n{}'.format(traceback.format_exc()))