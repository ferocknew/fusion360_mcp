# Fusion360 MCP 测试说明

这个目录包含了 Fusion360 MCP 项目的所有单元测试，每个工具都有独立的测试文件，便于调试和维护。

## 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── test_base.py             # 测试基类和公共工具
├── test_document_tools.py   # 文档工具测试
├── test_object_tools.py     # 对象工具测试
├── test_part_tools.py       # 零件工具测试
├── test_view_tools.py       # 视图工具测试
├── test_execute_tools.py    # 代码执行工具测试
├── run_tests.py             # 主测试运行器
├── quick_test.py            # 快速测试脚本
└── README.md                # 本文档
```

## 运行测试

### 1. 完整测试套件

运行所有测试：
```bash
# 方式 1: 直接运行
python tests/run_tests.py

# 方式 2: 使用安装的命令
fusion360_mcp_test

# 方式 3: 使用 unittest
python -m unittest discover tests
```

### 2. 运行特定测试

运行单个测试套件：
```bash
python tests/run_tests.py 文档工具
python tests/run_tests.py 对象工具
python tests/run_tests.py 零件工具
```

运行多个指定测试：
```bash
python tests/run_tests.py 文档工具 对象工具
```

### 3. 快速测试

快速验证基本功能：
```bash
# 运行所有快速测试
python tests/quick_test.py

# 或使用安装的命令
fusion360_mcp_quick_test

# 运行特定快速测试
python tests/quick_test.py doc      # 文档测试
python tests/quick_test.py obj      # 对象测试
python tests/quick_test.py part     # 零件测试
python tests/quick_test.py mgmt     # 对象管理测试
```

### 4. 单独运行测试文件

```bash
python -m unittest tests.test_document_tools
python -m unittest tests.test_object_tools.TestObjectTools.test_create_cylinder
```

## 测试类型

### 📄 文档工具测试 (test_document_tools.py)
- 创建文档（默认参数、自定义参数）
- 多文档创建
- 单位验证
- 模板支持

### 🔵 对象工具测试 (test_object_tools.py)
- 基本几何体创建（圆柱、立方体、球体）
- 对象获取和管理
- 对象删除
- 位置定位

### 🔧 零件工具测试 (test_part_tools.py)
- 零件列表获取
- 零件内容验证
- 零件插入模拟
- 库分类测试

### 👁️ 视图工具测试 (test_view_tools.py)
- 视图截图（默认和自定义参数）
- 不同分辨率和格式
- 相机和目标位置
- 性能测试

### 💻 代码执行测试 (test_execute_tools.py)
- 简单代码执行
- Fusion 360 API 代码
- 错误处理和安全检查
- 性能测试

## 测试特性

### 🔄 异步测试支持
所有测试都基于 `AsyncTestCase` 基类，支持异步操作测试。

### 🎭 模拟 API
使用 `MockFusion360API` 类模拟 Fusion 360 API 调用，无需实际 Fusion 360 环境。

### 📊 详细报告
提供详细的测试结果报告，包括：
- 成功率统计
- 执行时间
- 失败详情
- 性能指标

### 🛡️ 错误处理
测试包含完整的错误处理场景：
- 无效参数
- 网络错误
- API 失败
- 安全检查

## 调试测试

### 查看详细输出
```bash
python tests/run_tests.py --verbose
```

### 查看可用测试
```bash
python tests/run_tests.py --list
```

### 获取帮助
```bash
python tests/run_tests.py --help
```

## 编写新测试

### 1. 继承测试基类
```python
from tests.test_base import Fusion360TestBase

class TestMyTool(Fusion360TestBase):
    def setUp(self):
        super().setUp()
        self.mock_api = MockFusion360API()
```

### 2. 编写测试方法
```python
def test_my_feature(self):
    """测试我的功能"""
    async def test():
        result = await self.mock_api.my_function()
        self.log_test_result("我的功能测试", result)
        self.assert_api_call_success(result)

    self.async_test(test())
```

### 3. 添加到测试运行器
在 `run_tests.py` 的 `test_suites` 中添加新的测试类。

## 最佳实践

### ✅ 好的测试
- 每个测试函数测试一个特定功能
- 使用描述性的测试名称
- 包含边界条件和错误情况
- 记录测试结果

### ❌ 避免的做法
- 测试之间相互依赖
- 硬编码的环境特定值
- 过度复杂的测试逻辑
- 忽略异常处理

## 持续集成

这些测试可以集成到 CI/CD 流程中：

```yaml
# .github/workflows/test.yml 示例
- name: Run tests
  run: |
    pip install -e .
    python tests/run_tests.py
```

## 故障排除

### 常见问题

1. **导入错误**
   - 确保项目根目录在 Python 路径中
   - 检查 `__init__.py` 文件是否存在

2. **异步测试失败**
   - 确保使用 `self.async_test()` 包装异步测试
   - 检查 `setUp()` 和 `tearDown()` 调用

3. **模拟 API 问题**
   - 重置 `MockFusion360API` 状态
   - 检查调用历史记录

### 联系支持
如有测试相关问题，请提交 issue 或查看项目文档。
