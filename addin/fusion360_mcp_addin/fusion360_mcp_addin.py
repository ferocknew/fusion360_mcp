"""
Fusion360 MCP Addin - 改进版本
基于官方 demo 结构的标准插件实现
"""

import adsk.core
import adsk.fusion
import traceback
import json
import threading
import os
import base64
import tempfile
from datetime import datetime
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
            elif path == '/api/view':
                result = get_fusion_view()
            elif path == '/api/list':
                result = get_fusion_api_list()
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
            elif path == '/api/view':
                result = capture_fusion_view(data)
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

        # 安全地获取应用信息
        app_name = "Fusion 360"
        version = "Unknown"

        try:
            # 尝试不同的属性名
            if hasattr(app, 'productName'):
                app_name = app.productName
            elif hasattr(app, 'name'):
                app_name = app.name
            elif hasattr(app, 'appName'):
                app_name = app.appName
        except:
            app_name = "Fusion 360"  # 默认值

        try:
            if hasattr(app, 'version'):
                version = app.version
        except:
            version = "Unknown"

        status = {
            "success": True,
            "app_name": app_name,
            "version": version,
            "active_document": None,
            "design_workspace": False
        }

        # 检查活动文档
        try:
            if app.activeDocument:
                status["active_document"] = app.activeDocument.name

                # 检查是否在设计工作空间
                if app.activeProduct:
                    design = adsk.fusion.Design.cast(app.activeProduct)
                    status["design_workspace"] = design is not None
        except Exception as doc_error:
            log_message(f"获取文档信息失败: {str(doc_error)}")

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


def get_fusion_view():
    """获取当前视图信息 (GET 请求)"""
    try:
        if not app or not app.activeViewport:
            return {"success": False, "error": "没有活动视图"}

        viewport = app.activeViewport
        camera = viewport.camera

        view_info = {
            "success": True,
            "viewport": {
                "width": viewport.width,
                "height": viewport.height
            },
            "camera": {
                "target": {
                    "x": camera.target.x,
                    "y": camera.target.y,
                    "z": camera.target.z
                },
                "eye": {
                    "x": camera.eye.x,
                    "y": camera.eye.y,
                    "z": camera.eye.z
                },
                "upVector": {
                    "x": camera.upVector.x,
                    "y": camera.upVector.y,
                    "z": camera.upVector.z
                },
                "viewExtents": camera.viewExtents,
                "cameraType": "Perspective" if camera.cameraType == adsk.core.CameraTypes.PerspectiveCameraType else "Orthographic"
            }
        }

        return view_info

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_fusion_api_list():
    """获取 Fusion 360 API 功能列表"""
    try:
        # 详细的 Fusion 360 API 功能列表
        api_categories = {
            "design_apis": {
                "name": "设计API",
                "description": "用于创建和编辑3D模型的核心设计功能",
                "apis": [
                    {
                        "name": "sketches",
                        "chinese_name": "草图",
                        "description": "创建和编辑2D草图，包括线条、圆弧、圆形、矩形等几何元素",
                        "common_operations": ["addLine", "addCircle", "addRectangle", "addArc", "addSpline"]
                    },
                    {
                        "name": "features.extrudeFeatures",
                        "chinese_name": "拉伸特征",
                        "description": "将2D草图拉伸成3D实体",
                        "common_operations": ["add", "createInput", "setDistanceExtent", "setToExtent"]
                    },
                    {
                        "name": "features.revolveFeatures",
                        "chinese_name": "旋转特征",
                        "description": "围绕轴线旋转2D轮廓创建3D实体",
                        "common_operations": ["add", "createInput", "setAngleExtent", "setFullExtent"]
                    },
                    {
                        "name": "features.sweepFeatures",
                        "chinese_name": "扫掠特征",
                        "description": "沿路径扫掠2D轮廓创建3D实体",
                        "common_operations": ["add", "createInput", "setPath", "setProfile"]
                    },
                    {
                        "name": "features.loftFeatures",
                        "chinese_name": "放样特征",
                        "description": "在多个截面之间创建过渡实体",
                        "common_operations": ["add", "createInput", "setSectionProfiles"]
                    },
                    {
                        "name": "features.filletFeatures",
                        "chinese_name": "圆角特征",
                        "description": "在边缘创建圆角或倒角",
                        "common_operations": ["add", "createInput", "setConstantRadius", "setVariableRadius"]
                    },
                    {
                        "name": "features.chamferFeatures",
                        "chinese_name": "倒角特征",
                        "description": "在边缘创建倒角",
                        "common_operations": ["add", "createInput", "setDistances", "setEqualDistance"]
                    },
                    {
                        "name": "features.holeFeatures",
                        "chinese_name": "孔特征",
                        "description": "创建圆孔、螺纹孔等",
                        "common_operations": ["add", "createSimpleInput", "createCounterboreInput"]
                    },
                    {
                        "name": "features.patternFeatures",
                        "chinese_name": "阵列特征",
                        "description": "创建矩形阵列、圆形阵列等重复特征",
                        "common_operations": ["rectangularPatternFeatures", "circularPatternFeatures"]
                    },
                    {
                        "name": "features.mirrorFeatures",
                        "chinese_name": "镜像特征",
                        "description": "创建镜像特征",
                        "common_operations": ["add", "createInput", "setMirrorPlane"]
                    }
                ]
            },
            "modeling_apis": {
                "name": "建模API",
                "description": "高级建模和几何操作功能",
                "apis": [
                    {
                        "name": "bRepBodies",
                        "chinese_name": "实体对象",
                        "description": "管理3D实体对象",
                        "common_operations": ["createSphere", "createBox", "createCylinder", "combineFeatures"]
                    },
                    {
                        "name": "constructionPlanes",
                        "chinese_name": "构造平面",
                        "description": "创建用于建模的辅助平面",
                        "common_operations": ["add", "createInput", "setByOffset", "setByAngle"]
                    },
                    {
                        "name": "constructionAxes",
                        "chinese_name": "构造轴",
                        "description": "创建用于建模的辅助轴线",
                        "common_operations": ["add", "createInput", "setByLine", "setByTwoPoints"]
                    },
                    {
                        "name": "joints",
                        "chinese_name": "装配约束",
                        "description": "创建装配中的约束关系",
                        "common_operations": ["rigidJoints", "revoluteJoints", "sliderJoints"]
                    },
                    {
                        "name": "workPlanes",
                        "chinese_name": "工作平面",
                        "description": "定义草图和特征的工作平面",
                        "common_operations": ["createByPoint", "createByOffset", "createByThreePoints"]
                    }
                ]
            },
            "analysis_apis": {
                "name": "分析API",
                "description": "仿真分析和计算功能",
                "apis": [
                    {
                        "name": "studies",
                        "chinese_name": "分析研究",
                        "description": "创建和管理仿真分析研究",
                        "common_operations": ["staticStressStudies", "modalStudies", "thermalStudies"]
                    },
                    {
                        "name": "physicalProperties",
                        "chinese_name": "物理属性",
                        "description": "计算体积、重量、重心等物理属性",
                        "common_operations": ["getPhysicalProperties", "volume", "mass", "centroid"]
                    },
                    {
                        "name": "measureManager",
                        "chinese_name": "测量管理器",
                        "description": "测量距离、角度、面积等几何量",
                        "common_operations": ["measureDistance", "measureAngle", "measureArea"]
                    }
                ]
            },
            "manufacturing_apis": {
                "name": "制造API",
                "description": "CAM加工和制造相关功能",
                "apis": [
                    {
                        "name": "cam.operations",
                        "chinese_name": "加工操作",
                        "description": "创建铣削、车削等加工操作",
                        "common_operations": ["face", "adaptive", "pocket", "drill", "turning"]
                    },
                    {
                        "name": "cam.tools",
                        "chinese_name": "刀具管理",
                        "description": "管理和配置加工刀具",
                        "common_operations": ["flatEndmill", "ballEndmill", "drill", "chamferMill"]
                    },
                    {
                        "name": "cam.setups",
                        "chinese_name": "加工设置",
                        "description": "配置工件坐标系和加工设置",
                        "common_operations": ["createSetup", "setWorkCoordinateSystem", "setStock"]
                    },
                    {
                        "name": "cam.postProcess",
                        "chinese_name": "后处理",
                        "description": "生成数控程序代码",
                        "common_operations": ["generateCode", "executePostProcessor"]
                    }
                ]
            },
            "rendering_apis": {
                "name": "渲染API",
                "description": "可视化渲染和外观设置",
                "apis": [
                    {
                        "name": "appearances",
                        "chinese_name": "外观",
                        "description": "设置材质外观和贴图",
                        "common_operations": ["addAppearance", "setMaterial", "setTexture"]
                    },
                    {
                        "name": "scenes",
                        "chinese_name": "场景",
                        "description": "配置渲染场景和环境",
                        "common_operations": ["addScene", "setEnvironment", "setLighting"]
                    },
                    {
                        "name": "renderManager",
                        "chinese_name": "渲染管理器",
                        "description": "执行高质量渲染",
                        "common_operations": ["render", "setQuality", "setResolution"]
                    }
                ]
            },
            "data_apis": {
                "name": "数据API",
                "description": "文档管理和数据交换功能",
                "apis": [
                    {
                        "name": "documents",
                        "chinese_name": "文档管理",
                        "description": "创建、打开、保存文档",
                        "common_operations": ["add", "open", "save", "saveAs", "close"]
                    },
                    {
                        "name": "exportManager",
                        "chinese_name": "导出管理器",
                        "description": "导出各种文件格式",
                        "common_operations": ["exportSTL", "exportSTEP", "exportIGES", "exportF3D"]
                    },
                    {
                        "name": "importManager",
                        "chinese_name": "导入管理器",
                        "description": "导入外部文件格式",
                        "common_operations": ["importSTEP", "importIGES", "importMesh"]
                    },
                    {
                        "name": "dataFile",
                        "chinese_name": "数据文件",
                        "description": "访问云端数据文件",
                        "common_operations": ["uploadFile", "downloadFile", "getFileInfo"]
                    }
                ]
            },
            "ui_apis": {
                "name": "用户界面API",
                "description": "自定义用户界面和交互",
                "apis": [
                    {
                        "name": "commandDefinitions",
                        "chinese_name": "命令定义",
                        "description": "创建自定义命令和按钮",
                        "common_operations": ["addButtonDefinition", "addDropdownDefinition"]
                    },
                    {
                        "name": "toolbars",
                        "chinese_name": "工具栏",
                        "description": "管理工具栏和面板",
                        "common_operations": ["addToolbar", "addPanel", "addCommand"]
                    },
                    {
                        "name": "palettes",
                        "chinese_name": "面板",
                        "description": "创建和管理面板窗口",
                        "common_operations": ["add", "show", "hide", "dock"]
                    },
                    {
                        "name": "messageBox",
                        "chinese_name": "消息框",
                        "description": "显示用户消息和对话框",
                        "common_operations": ["show", "showDialog", "showInputDialog"]
                    }
                ]
            },
            "utilities_apis": {
                "name": "工具API",
                "description": "实用工具和辅助功能",
                "apis": [
                    {
                        "name": "timeline",
                        "chinese_name": "时间线",
                        "description": "管理设计历史时间线",
                        "common_operations": ["rollTo", "capture", "restore"]
                    },
                    {
                        "name": "selections",
                        "chinese_name": "选择",
                        "description": "管理对象选择",
                        "common_operations": ["selectEntity", "clearSelection", "addToSelection"]
                    },
                    {
                        "name": "activeViewport",
                        "chinese_name": "活动视口",
                        "description": "控制3D视图显示",
                        "common_operations": ["camera", "fit", "saveAsImageFile", "refresh"]
                    },
                    {
                        "name": "progressDialog",
                        "chinese_name": "进度对话框",
                        "description": "显示操作进度",
                        "common_operations": ["show", "hide", "setProgress", "setMessage"]
                    }
                ]
            }
        }

        # 获取当前可用的API统计
        api_stats = {
            "total_categories": len(api_categories),
            "total_apis": sum(len(category["apis"]) for category in api_categories.values()),
            "fusion_version": app.version if app else "Unknown"
        }

        result = {
            "success": True,
            "message": "Fusion 360 API 功能列表",
            "statistics": api_stats,
            "categories": api_categories,
            "usage_notes": [
                "此列表包含了 Fusion 360 的主要 API 功能分类",
                "每个API都包含中文名称和详细说明",
                "common_operations 列出了常用的操作方法",
                "实际使用时需要通过 adsk.core 和 adsk.fusion 模块访问这些API",
                "某些功能可能需要特定的 Fusion 360 许可证级别"
            ],
            "examples": {
                "创建圆柱体": "使用 sketches 创建圆形，然后用 extrudeFeatures 拉伸",
                "装配约束": "使用 joints 创建零件之间的装配关系",
                "材质渲染": "使用 appearances 设置材质，用 renderManager 执行渲染",
                "导出文件": "使用 exportManager 导出为STL、STEP等格式"
            }
        }

        log_message(f"API列表查询完成，共 {api_stats['total_apis']} 个API")
        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


def capture_fusion_view(data):
    """捕获当前视图截图 (POST 请求)"""
    try:
        if not app or not app.activeViewport:
            return {"success": False, "error": "没有活动视图"}

        # 获取参数
        parameters = data.get('parameters', {})
        width = parameters.get('width', 1024)
        height = parameters.get('height', 768)
        format_type = parameters.get('format', 'png').lower()
        filename = parameters.get('filename', None)
        return_base64 = parameters.get('return_base64', False)

        # 验证参数
        if width < 100 or width > 4096:
            return {"success": False, "error": "宽度必须在 100-4096 像素之间"}
        if height < 100 or height > 4096:
            return {"success": False, "error": "高度必须在 100-4096 像素之间"}
        if format_type not in ['png', 'jpg', 'jpeg']:
            return {"success": False, "error": "支持的格式: png, jpg, jpeg"}

        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"fusion360_view_{timestamp}.{format_type}"

        # 确保文件扩展名正确
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename += f".{format_type}"

        # 创建临时目录和文件路径
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)

        log_message(f"准备截图: {width}x{height}, 保存到: {file_path}")

        # 获取活动视图并截图
        viewport = app.activeViewport

        # 使用 Fusion 360 API 保存视图截图
        success = viewport.saveAsImageFile(file_path, width, height)

        if not success:
            return {"success": False, "error": "视图截图保存失败"}

        # 检查文件是否成功创建
        if not os.path.exists(file_path):
            return {"success": False, "error": "截图文件未创建"}

        file_size = os.path.getsize(file_path)
        log_message(f"截图成功: {file_path}, 大小: {file_size} 字节")

        result = {
            "success": True,
            "file_path": file_path,
            "filename": filename,
            "file_size": file_size,
            "dimensions": {
                "width": width,
                "height": height
            },
            "format": format_type
        }

        # 如果需要返回 base64 数据
        if return_base64:
            try:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    result["image_data"] = base64_data
                    result["image_data_size"] = len(base64_data)
                    log_message(f"Base64 数据大小: {len(base64_data)} 字符")
            except Exception as e:
                log_message(f"Base64 编码失败: {str(e)}")
                result["base64_error"] = str(e)

        return result

    except Exception as e:
        error_msg = str(e)
        log_message(f"视图截图失败: {error_msg}")
        return {"success": False, "error": error_msg}


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
