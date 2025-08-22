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

# 导入公共方法
import common

# 全局变量
app = None
ui = None
http_server = None
server_thread = None
logger = None

# 安全标志
request_in_progress = False
request_lock = threading.Lock()


class SafeFusion360Handler(BaseHTTPRequestHandler):
    """安全的 Fusion360 HTTP 请求处理器"""

    def do_GET(self):
        """处理 GET 请求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            common.log_safe(logger, 'info', f"收到 GET 请求: {path}")
            
            if path == '/api/health':
                result = {"status": "healthy", "message": "Fusion 360 插件运行正常"}
            elif path == '/api/status':
                common.log_safe(logger, 'debug', "处理状态查询请求")
                result = common.get_fusion360_status(app, logger)
            elif path == '/api/objects':
                common.log_safe(logger, 'debug', "处理对象列表查询请求")
                result = common.get_objects_safe(app, logger)
            else:
                common.log_safe(logger, 'warning', f"未知的 GET 路径: {path}")
                result = {"success": False, "error": f"未知的 GET 路径: {path}"}
            
            common.log_safe(logger, 'debug', f"GET 请求结果: {result}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            common.log_safe(logger, 'error', f"GET 请求处理失败: {path}", e)
            self.send_error(500, f"服务器错误: {str(e)}")

    def do_POST(self):
        """处理 POST 请求"""
        global request_in_progress
        
        path = urllib.parse.urlparse(self.path).path
        common.log_safe(logger, 'info', f"收到 POST 请求: {path}")
        
        # 防止并发请求
        with request_lock:
            if request_in_progress:
                common.log_safe(logger, 'warning', "服务器繁忙，拒绝并发请求")
                self.send_error(429, "服务器忙，请稍后重试")
                return
            request_in_progress = True
        
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            common.log_safe(logger, 'debug', f"请求数据大小: {content_length} 字节")
            
            post_data = self.rfile.read(content_length)

            if post_data:
                data = json.loads(post_data.decode('utf-8'))
                common.log_safe(logger, 'debug', f"请求数据: {data}")
            else:
                data = {}
                common.log_safe(logger, 'debug', "空请求数据")

            # 路由处理
            if path == '/api/document':
                common.log_safe(logger, 'info', "处理文档创建请求")
                result = common.handle_document_request_safe(app, data, logger)
            elif path == '/api/object':
                common.log_safe(logger, 'info', "处理对象创建请求")
                result = common.handle_object_request_safe(app, data, logger)
            else:
                common.log_safe(logger, 'warning', f"未知的 POST 路径: {path}")
                result = {"success": False, "error": f"未知的 POST 路径: {path}"}

            common.log_safe(logger, 'info', f"POST 请求处理完成: {result}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            error_msg = f"处理请求失败: {str(e)}"
            common.log_safe(logger, 'error', f"POST 请求处理失败: {path}", e)
            
            if ui:
                ui.messageBox(f"插件错误: {error_msg}")
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_result = {"success": False, "error": error_msg}
            self.wfile.write(json.dumps(error_result).encode('utf-8'))
        
        finally:
            request_in_progress = False
            common.log_safe(logger, 'debug', "POST 请求处理结束，释放锁")

    def log_message(self, format, *args):
        """禁用默认日志输出"""
        pass


def start_http_server():
    """启动 HTTP 服务器"""
    global http_server, server_thread
    
    try:
        common.log_safe(logger, 'info', "准备启动 HTTP 服务器")
        
        # 创建服务器
        http_server = HTTPServer(('localhost', 9000), SafeFusion360Handler)
        
        # 在单独线程中运行
        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        common.log_safe(logger, 'info', "HTTP 服务器已启动在端口 9000")
        
        if ui:
            ui.messageBox("HTTP 服务器已启动在端口 9000")
            
    except Exception as e:
        common.log_safe(logger, 'error', "启动 HTTP 服务器失败", e)
        if ui:
            ui.messageBox(f"启动 HTTP 服务器失败: {str(e)}")


def stop_http_server():
    """停止 HTTP 服务器"""
    global http_server, server_thread
    
    try:
        common.log_safe(logger, 'info', "准备停止 HTTP 服务器")
        
        if http_server:
            http_server.shutdown()
            http_server.server_close()
            http_server = None
            
        if server_thread:
            server_thread.join(timeout=1)
            server_thread = None
            
        common.log_safe(logger, 'info', "HTTP 服务器已停止")
        
        if ui:
            ui.messageBox("HTTP 服务器已停止")
            
    except Exception as e:
        common.log_safe(logger, 'error', "停止 HTTP 服务器失败", e)
        if ui:
            ui.messageBox(f"停止 HTTP 服务器失败: {str(e)}")


def run(context):
    """插件入口函数"""
    global app, ui, logger
    
    try:
        # 设置日志
        logger = common.setup_logging()
        common.log_safe(logger, 'info', "=== 插件启动开始 ===")
        
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        common.log_safe(logger, 'info', f"Fusion 360 应用已获取: {app.productName} {app.version}")
        
        # 启动 HTTP 服务器，等待 MCP 服务器的请求
        start_http_server()
        
        common.log_safe(logger, 'info', "=== 插件启动完成 ===")
        
    except Exception as e:
        common.log_safe(logger, 'critical', "插件启动失败", e)
        if ui:
            ui.messageBox('启动失败:\n{}'.format(traceback.format_exc()))


def stop(context):
    """插件停止函数"""
    global app, ui, logger
    
    try:
        common.log_safe(logger, 'info', "=== 插件停止开始 ===")
        
        # 停止 HTTP 服务器
        stop_http_server()
        
        common.log_safe(logger, 'info', "=== 插件停止完成 ===")
        
    except Exception as e:
        common.log_safe(logger, 'critical', "插件停止失败", e)
        if ui:
            ui.messageBox('停止失败:\n{}'.format(traceback.format_exc()))
