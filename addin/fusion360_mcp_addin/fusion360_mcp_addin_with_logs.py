import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import json
import threading
import time
import os
import sys
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# 全局变量
app = None
ui = None
http_server = None
server_thread = None

# 安全标志
request_in_progress = False
request_lock = threading.Lock()

# 日志设置
logger = None


def setup_logging():
    """设置日志记录"""
    global logger
    
    try:
        # 获取插件目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, 'logs')
        
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建日志文件名（按日期）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'fusion360_mcp_addin_{timestamp}.log')
        
        # 配置日志器
        logger = logging.getLogger('fusion360_mcp_addin')
        logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        
        logger.info("=== Fusion360 MCP Addin 启动 ===")
        logger.info(f"日志文件: {log_file}")
        logger.info(f"Python 版本: {sys.version}")
        logger.info(f"工作目录: {os.getcwd()}")
        
        return True
        
    except Exception as e:
        # 如果日志设置失败，至少显示错误
        if ui:
            ui.messageBox(f"日志设置失败: {str(e)}")
        return False


def log_safe(level, message, exception=None):
    """安全的日志记录"""
    try:
        if logger:
            if exception:
                message = f"{message}\n异常详情: {str(exception)}\n堆栈跟踪:\n{traceback.format_exc()}"
            
            if level == 'debug':
                logger.debug(message)
            elif level == 'info':
                logger.info(message)
            elif level == 'warning':
                logger.warning(message)
            elif level == 'error':
                logger.error(message)
            elif level == 'critical':
                logger.critical(message)
        else:
            # 如果日志器不可用，写入临时文件
            script_dir = os.path.dirname(os.path.abspath(__file__))
            temp_log = os.path.join(script_dir, 'temp_error.log')
            with open(temp_log, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {level.upper()} - {message}\n")
                if exception:
                    f.write(f"异常: {str(exception)}\n")
                    f.write(f"堆栈: {traceback.format_exc()}\n")
                f.write("-" * 50 + "\n")
    except:
        pass  # 即使日志记录失败也不应该影响主程序


class SafeFusion360Handler(BaseHTTPRequestHandler):
    """安全的 Fusion360 HTTP 请求处理器"""

    def do_GET(self):
        """处理 GET 请求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            log_safe('info', f"收到 GET 请求: {path}")
            
            if path == '/api/health':
                result = {"status": "healthy", "message": "Fusion 360 插件运行正常"}
            elif path == '/api/status':
                log_safe('debug', "处理状态查询请求")
                result = get_fusion360_status()
            elif path == '/api/objects':
                log_safe('debug', "处理对象列表查询请求")
                result = get_objects_safe()
            else:
                log_safe('warning', f"未知的 GET 路径: {path}")
                result = {"success": False, "error": f"未知的 GET 路径: {path}"}
            
            log_safe('debug', f"GET 请求结果: {result}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            log_safe('error', f"GET 请求处理失败: {path}", e)
            self.send_error(500, f"服务器错误: {str(e)}")

    def do_POST(self):
        """处理 POST 请求"""
        global request_in_progress
        
        path = urllib.parse.urlparse(self.path).path
        log_safe('info', f"收到 POST 请求: {path}")
        
        # 防止并发请求
        with request_lock:
            if request_in_progress:
                log_safe('warning', "服务器繁忙，拒绝并发请求")
                self.send_error(429, "服务器忙，请稍后重试")
                return
            request_in_progress = True
        
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            log_safe('debug', f"请求数据大小: {content_length} 字节")
            
            post_data = self.rfile.read(content_length)

            if post_data:
                data = json.loads(post_data.decode('utf-8'))
                log_safe('debug', f"请求数据: {data}")
            else:
                data = {}
                log_safe('debug', "空请求数据")

            # 路由处理
            if path == '/api/document':
                log_safe('info', "处理文档创建请求")
                result = handle_document_request_safe(data)
            elif path == '/api/object':
                log_safe('info', "处理对象创建请求")
                result = handle_object_request_safe(data)
            else:
                log_safe('warning', f"未知的 POST 路径: {path}")
                result = {"success": False, "error": f"未知的 POST 路径: {path}"}

            log_safe('info', f"POST 请求处理完成: {result}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            error_msg = f"处理请求失败: {str(e)}"
            log_safe('error', f"POST 请求处理失败: {path}", e)
            
            if ui:
                ui.messageBox(f"插件错误: {error_msg}")
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_result = {"success": False, "error": error_msg}
            self.wfile.write(json.dumps(error_result).encode('utf-8'))
        
        finally:
            request_in_progress = False
            log_safe('debug', "POST 请求处理结束，释放锁")

    def log_message(self, format, *args):
        """禁用默认日志输出"""
        pass


def get_fusion360_status():
    """获取 Fusion 360 状态"""
    try:
        if not app:
            return {"success": False, "error": "应用未初始化"}
        
        status = {
            "success": True,
            "app_name": app.productName,
            "version": app.version,
            "active_document": None,
            "units": "mm"
        }
        
        if app.activeDocument:
            status["active_document"] = app.activeDocument.name
            
        return status
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_objects_safe():
    """安全地获取对象列表"""
    try:
        if not app or not app.activeDocument:
            return {"success": False, "error": "没有活动文档"}
        
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {"success": False, "error": "当前不是设计环境"}
        
        objects = []
        rootComp = design.rootComponent
        
        # 获取实体
        for i, body in enumerate(rootComp.bRepBodies):
            if i >= 10:  # 限制返回数量，避免过多数据
                break
            objects.append({
                "id": body.entityToken,
                "name": body.name if body.name else f"实体{i+1}",
                "type": "body",
                "visible": body.isVisible
            })
        
        return {"success": True, "objects": objects}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_document_request_safe(data):
    """安全处理文档创建请求"""
    try:
        parameters = data.get('parameters', {})
        name = parameters.get('name', '新建文档')
        
        # 创建新文档（简化版本，避免单位设置问题）
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        if doc:
            doc.name = name
            return {"success": True, "document_id": doc.name}
        else:
            return {"success": False, "error": "文档创建失败"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_object_request_safe(data):
    """安全处理对象创建请求"""
    try:
        parameters = data.get('parameters', {})
        object_type = parameters.get('type')
        obj_params = parameters.get('parameters', {})
        
        # 只支持简单的圆柱体创建
        if object_type == 'extrude' and obj_params.get('base_feature') == 'circle':
            return create_simple_cylinder_safe(obj_params)
        else:
            return {"success": False, "error": f"不支持的对象类型: {object_type}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_simple_cylinder_safe(params):
    """安全创建简单圆柱体"""
    try:
        log_safe('info', f"开始创建圆柱体，参数: {params}")
        
        if not app or not app.activeDocument:
            log_safe('error', "没有活动文档")
            return {"success": False, "error": "没有活动文档"}
            
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            log_safe('error', "当前不是设计环境")
            return {"success": False, "error": "当前不是设计环境"}
        
        log_safe('debug', "获取根组件")
        rootComp = design.rootComponent
        
        # 创建草图
        log_safe('debug', "创建草图")
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        
        # 创建圆
        radius = float(params.get('radius', 2.5))
        log_safe('debug', f"创建圆，半径: {radius}")
        center = adsk.core.Point3D.create(0, 0, 0)
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
        
        # 创建拉伸
        log_safe('debug', "创建拉伸特征")
        profile = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        height = float(params.get('height', 5.0))
        log_safe('debug', f"设置拉伸高度: {height}")
        distance = adsk.core.ValueInput.createByReal(height)
        extrudeInput.setDistanceExtent(False, distance)
        
        log_safe('debug', "执行拉伸操作")
        extrudeFeature = extrudes.add(extrudeInput)
        
        result = {
            "success": True,
            "object_id": extrudeFeature.entityToken,
            "type": "extrude",
            "parameters": params
        }
        
        log_safe('info', f"圆柱体创建成功: {result}")
        return result
        
    except Exception as e:
        log_safe('error', f"创建圆柱体失败", e)
        return {"success": False, "error": str(e)}


def start_http_server():
    """启动 HTTP 服务器"""
    global http_server, server_thread
    
    try:
        # 创建服务器
        http_server = HTTPServer(('localhost', 9000), SafeFusion360Handler)
        
        # 在单独线程中运行
        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        if ui:
            ui.messageBox("HTTP 服务器已启动在端口 9000")
            
    except Exception as e:
        if ui:
            ui.messageBox(f"启动 HTTP 服务器失败: {str(e)}")


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
            ui.messageBox(f"停止 HTTP 服务器失败: {str(e)}")


def run(context):
    """插件入口函数"""
    global app, ui
    
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # 启动 HTTP 服务器，等待 MCP 服务器的请求
        start_http_server()
        
    except:
        if ui:
            ui.messageBox('启动失败:\n{}'.format(traceback.format_exc()))


def stop(context):
    """插件停止函数"""
    global app, ui
    
    try:
        # 停止 HTTP 服务器
        stop_http_server()
        
    except:
        if ui:
            ui.messageBox('停止失败:\n{}'.format(traceback.format_exc()))
