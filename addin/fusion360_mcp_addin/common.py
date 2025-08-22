"""
Fusion360 MCP Addin 公共方法模块
"""

import os
import sys
import logging
import traceback
from datetime import datetime


def setup_logging():
    """设置日志记录"""
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

        return logger

    except Exception as e:
        return None


def log_safe(logger, level, message, exception=None):
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


def get_fusion360_status(app, logger=None):
    """获取 Fusion 360 状态"""
    try:
        if logger:
            log_safe(logger, 'debug', "获取 Fusion 360 状态")

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

        if logger:
            log_safe(logger, 'info', f"Fusion 360 状态: {status}")

        return status
    except Exception as e:
        if logger:
            log_safe(logger, 'error', "获取 Fusion 360 状态失败", e)
        return {"success": False, "error": str(e)}


def get_objects_safe(app, logger=None):
    """安全地获取对象列表"""
    try:
        if logger:
            log_safe(logger, 'debug', "获取对象列表")

        if not app or not app.activeDocument:
            return {"success": False, "error": "没有活动文档"}

        import adsk.fusion
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

        result = {"success": True, "objects": objects}

        if logger:
            log_safe(logger, 'info', f"获取到 {len(objects)} 个对象")

        return result
    except Exception as e:
        if logger:
            log_safe(logger, 'error', "获取对象列表失败", e)
        return {"success": False, "error": str(e)}


def handle_document_request_safe(app, data, logger=None):
    """安全处理文档创建请求"""
    try:
        if logger:
            log_safe(logger, 'info', f"处理文档创建请求: {data}")

        import adsk.core

        parameters = data.get('parameters', {})
        name = parameters.get('name', '新建文档')

        # 创建新文档（简化版本，避免单位设置问题）
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        if doc:
            doc.name = name
            result = {"success": True, "document_id": doc.name}

            if logger:
                log_safe(logger, 'info', f"文档创建成功: {result}")
        else:
            result = {"success": False, "error": "文档创建失败"}

            if logger:
                log_safe(logger, 'error', "文档创建失败")

        return result

    except Exception as e:
        if logger:
            log_safe(logger, 'error', "文档创建失败", e)
        return {"success": False, "error": str(e)}


def handle_object_request_safe(app, data, logger=None):
    """安全处理对象创建请求"""
    try:
        if logger:
            log_safe(logger, 'info', f"处理对象创建请求: {data}")

        parameters = data.get('parameters', {})
        object_type = parameters.get('type')
        obj_params = parameters.get('parameters', {})

        # 只支持简单的圆柱体创建
        if object_type == 'extrude' and obj_params.get('base_feature') == 'circle':
            return create_simple_cylinder_safe(app, obj_params, logger)
        else:
            result = {"success": False, "error": f"不支持的对象类型: {object_type}"}

            if logger:
                log_safe(logger, 'warning', f"不支持的对象类型: {object_type}")

            return result

    except Exception as e:
        if logger:
            log_safe(logger, 'error', "对象创建请求处理失败", e)
        return {"success": False, "error": str(e)}


def create_simple_cylinder_safe(app, params, logger=None):
    """安全创建简单圆柱体"""
    try:
        if logger:
            log_safe(logger, 'info', f"开始创建圆柱体，参数: {params}")

        import adsk.core
        import adsk.fusion

        if not app or not app.activeDocument:
            if logger:
                log_safe(logger, 'error', "没有活动文档")
            return {"success": False, "error": "没有活动文档"}

        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            if logger:
                log_safe(logger, 'error', "当前不是设计环境")
            return {"success": False, "error": "当前不是设计环境"}

        if logger:
            log_safe(logger, 'debug', "获取根组件")
        rootComp = design.rootComponent

        # 创建草图
        if logger:
            log_safe(logger, 'debug', "创建草图")
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)

        # 创建圆
        radius = float(params.get('radius', 2.5))
        if logger:
            log_safe(logger, 'debug', f"创建圆，半径: {radius}")
        center = adsk.core.Point3D.create(0, 0, 0)
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)

        # 创建拉伸
        if logger:
            log_safe(logger, 'debug', "创建拉伸特征")
        profile = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        height = float(params.get('height', 5.0))
        if logger:
            log_safe(logger, 'debug', f"设置拉伸高度: {height}")
        distance = adsk.core.ValueInput.createByReal(height)
        extrudeInput.setDistanceExtent(False, distance)

        if logger:
            log_safe(logger, 'debug', "执行拉伸操作")
        extrudeFeature = extrudes.add(extrudeInput)

        result = {
            "success": True,
            "object_id": extrudeFeature.entityToken,
            "type": "extrude",
            "parameters": params
        }

        if logger:
            log_safe(logger, 'info', f"圆柱体创建成功: {result}")
        return result

    except Exception as e:
        if logger:
            log_safe(logger, 'error', f"创建圆柱体失败", e)
        return {"success": False, "error": str(e)}
