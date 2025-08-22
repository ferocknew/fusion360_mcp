# Fusion 360 API 列表功能使用说明

## 概述

新增的 `/api/list` 接口提供了完整的 Fusion 360 API 功能列表和中文说明，帮助开发者快速了解和使用 Fusion 360 的各种API功能。

## 功能特点

- 📊 **完整统计**: 提供API总数、分类数量等统计信息
- 🏷️ **中文标注**: 每个API都有中文名称和详细说明
- 🔧 **常用操作**: 列出每个API的常用操作方法
- 💡 **使用示例**: 提供实际使用场景示例
- 📂 **分类整理**: 按功能将API分为8大类

## API分类

### 1. 设计API (design_apis) - 10个API
用于创建和编辑3D模型的核心设计功能
- 草图 (sketches)
- 拉伸特征 (features.extrudeFeatures)
- 旋转特征 (features.revolveFeatures)
- 扫掠特征 (features.sweepFeatures)
- 放样特征 (features.loftFeatures)
- 圆角特征 (features.filletFeatures)
- 倒角特征 (features.chamferFeatures)
- 孔特征 (features.holeFeatures)
- 阵列特征 (features.patternFeatures)
- 镜像特征 (features.mirrorFeatures)

### 2. 建模API (modeling_apis) - 5个API
高级建模和几何操作功能
- 实体对象 (bRepBodies)
- 构造平面 (constructionPlanes)
- 构造轴 (constructionAxes)
- 装配约束 (joints)
- 工作平面 (workPlanes)

### 3. 分析API (analysis_apis) - 3个API
仿真分析和计算功能
- 分析研究 (studies)
- 物理属性 (physicalProperties)
- 测量管理器 (measureManager)

### 4. 制造API (manufacturing_apis) - 4个API
CAM加工和制造相关功能
- 加工操作 (cam.operations)
- 刀具管理 (cam.tools)
- 加工设置 (cam.setups)
- 后处理 (cam.postProcess)

### 5. 渲染API (rendering_apis) - 3个API
可视化渲染和外观设置
- 外观 (appearances)
- 场景 (scenes)
- 渲染管理器 (renderManager)

### 6. 数据API (data_apis) - 4个API
文档管理和数据交换功能
- 文档管理 (documents)
- 导出管理器 (exportManager)
- 导入管理器 (importManager)
- 数据文件 (dataFile)

### 7. 用户界面API (ui_apis) - 4个API
自定义用户界面和交互
- 命令定义 (commandDefinitions)
- 工具栏 (toolbars)
- 面板 (palettes)
- 消息框 (messageBox)

### 8. 工具API (utilities_apis) - 4个API
实用工具和辅助功能
- 时间线 (timeline)
- 选择 (selections)
- 活动视口 (activeViewport)
- 进度对话框 (progressDialog)

## 使用方法

### 1. HTTP GET 请求
```bash
curl http://localhost:9000/api/list
```

### 2. Python 调用
```python
from src.fusion360_mcp.fusion360_api import get_api

api = get_api()
result = await api._request("GET", "/api/list")
```

### 3. 获取特定信息

#### 查看统计信息
```bash
curl -s http://localhost:9000/api/list | jq '.statistics'
```

#### 查看所有分类
```bash
curl -s http://localhost:9000/api/list | jq '.categories | keys'
```

#### 查看设计API详情
```bash
curl -s http://localhost:9000/api/list | jq '.categories.design_apis'
```

#### 查看使用示例
```bash
curl -s http://localhost:9000/api/list | jq '.examples'
```

## 响应结构

```json
{
  "success": true,
  "message": "Fusion 360 API 功能列表",
  "statistics": {
    "total_categories": 8,
    "total_apis": 37,
    "fusion_version": "版本号"
  },
  "categories": {
    "design_apis": {
      "name": "设计API",
      "description": "功能描述",
      "apis": [
        {
          "name": "API名称",
          "chinese_name": "中文名称",
          "description": "详细说明",
          "common_operations": ["常用操作1", "常用操作2"]
        }
      ]
    }
  },
  "usage_notes": ["使用注意事项"],
  "examples": {
    "示例名称": "示例说明"
  }
}
```

## 注意事项

1. **许可证要求**: 某些功能可能需要特定的 Fusion 360 许可证级别
2. **模块访问**: 实际使用时需要通过 `adsk.core` 和 `adsk.fusion` 模块访问这些API
3. **错误处理**: 建议在实际使用中添加适当的错误处理机制
4. **版本兼容**: API功能可能随 Fusion 360 版本更新而变化

## 测试

运行包含的测试脚本验证功能：
```bash
python tests/test_api_list.py
```

## 贡献

如发现API信息有误或需要补充，请提交问题或pull request。
