# Fusion360 MCP 真实集成测试指南

本指南说明如何运行使用真实 src 代码和 MCPClient 的集成测试。

## 测试架构

```
测试架构:
┌─────────────────┐    真实调用    ┌─────────────────┐    HTTP API    ┌─────────────────┐
│   单元测试      │◄──────────────►│ src/工具模块     │◄──────────────►│ Fusion360 插件  │
│  (test_*.py)    │               │                 │                │                 │
└─────────────────┘               └─────────────────┘                └─────────────────┘
        │                                   │                                   │
        │                                   │                                   │
        ▼                                   ▼                                   ▼
┌─────────────────┐                ┌─────────────────┐                ┌─────────────────┐
│   MCPClient     │                │  MCP 服务器     │                │   Fusion 360    │
│                 │                │  (FastMCP)      │                │     软件        │
└─────────────────┘                └─────────────────┘                └─────────────────┘
```

## 准备工作

### 1. 启动 Fusion 360 并加载插件

```bash
# 1. 启动 Fusion 360
# 2. 进入菜单: 工具 > 附加模块 > 开发
# 3. 点击 "添加插件"
# 4. 选择项目中的 addin/fusion360_mcp_addin.py
# 5. 确认插件启动成功，在 localhost:9000 提供服务
```

### 2. 启动 MCP 服务器

```bash
# 方式 1: 使用安装的命令
fusion360_mcp

# 方式 2: 直接运行
python src/fusion360_mcp/main.py

# 方式 3: 指定端口
fusion360_mcp --port 8000
```

### 3. 验证连接

⚠️ **重要端口说明**
- **MCP 服务器**: 端口 8000 (可配置)
- **Fusion 360 插件**: 端口 9000 (固定，不可更改)

**请确保端口 9000 没有被其他应用占用！**

```bash
# 检查端口是否被占用
lsof -i :8000  # MCP 服务器端口
lsof -i :9000  # Fusion 360 插件端口

# 检查 Fusion 360 插件
curl http://localhost:9000/api/health

# 检查 MCP 服务器
curl http://localhost:8000/health
```

## 运行测试

### 1. 真实集成测试

```bash
# 运行完整的真实集成测试
python tests/test_real_integration.py

# 详细输出
python tests/test_real_integration.py -v
```

### 2. 特定工具测试

```bash
# 文档工具测试
python tests/test_document_tools.py

# 对象工具测试
python tests/test_object_tools.py

# 所有测试
python tests/run_tests.py
```

### 3. 快速验证测试

```bash
# 快速测试所有功能
python tests/quick_test.py

# 测试特定功能
python tests/quick_test.py doc      # 文档
python tests/quick_test.py obj      # 对象
python tests/quick_test.py part     # 零件
```

## 测试类型详解

### 1. 真实工具调用 (`call_real_tool`)

直接调用 `src/fusion360_mcp/tools.py` 中的函数:

```python
# 示例: 创建文档
result = await self.call_real_tool("create_document",
    name="测试文档",
    units="mm"
)
```

这种方式：
- ✅ 使用真实的业务逻辑
- ✅ 测试完整的代码路径
- ✅ 发现代码中的真实问题

### 2. MCPClient 调用 (`call_mcp_client_method`)

通过 `addin/client.py` 中的 MCPClient:

```python
# 示例: 创建对象
result = self.call_mcp_client_method("create_object",
    object_type="extrude",
    parameters={"radius": 25, "height": 50}
)
```

这种方式：
- ✅ 测试客户端-服务器通信
- ✅ 验证 API 接口
- ✅ 模拟真实的插件调用

## 测试结果解释

### 成功示例
```
🧪 测试通过真实工具创建文档(默认参数)...
✅ 真实工具创建文档成功

📞 测试通过 MCPClient 创建文档...
✅ MCPClient 创建文档成功

📊 真实集成测试结果:
测试摘要: 总计 4, 通过 4, 失败 0
```

### 失败示例及解决方案

#### 连接失败
```
❌ Fusion 360 连接: 失败
⚠️  Fusion 360 插件未运行，请启动 Fusion 360 并加载 MCP 插件
```

**解决方案:**
1. 确保 Fusion 360 已启动
2. 检查插件是否正确加载
3. 验证插件在 localhost:9000 运行

#### API 调用失败
```
❌ 真实工具创建文档失败: 网络错误
```

**解决方案:**
1. 检查 MCP 服务器状态
2. 确认端口配置正确
3. 查看服务器日志

## 调试技巧

### 1. 开启详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 单步调试

```python
# 在测试中添加断点
import pdb; pdb.set_trace()
```

### 3. 检查网络连接

```bash
# 检查端口是否开放
netstat -an | grep 9000
netstat -an | grep 8000

# 测试 API 端点
curl -X POST http://localhost:9000/api/health
curl -X GET http://localhost:8000/health
```

### 4. 查看 Fusion 360 控制台

在 Fusion 360 中:
1. 工具 > 附加模块 > 开发
2. 查看控制台输出
3. 检查错误信息

## 常见问题

### Q: 测试总是失败，提示连接错误
A:
1. **检查端口占用**:
   ```bash
   lsof -i :8000  # MCP 服务器
   lsof -i :9000  # Fusion 360 插件
   ```
2. 确认 Fusion 360 插件已启动 (`curl http://localhost:9000/api/health`)
3. 确认 MCP 服务器已启动 (`curl http://localhost:8000/health`)
4. 检查防火墙设置
5. 如端口 9000 被占用，需要释放该端口（插件端口不可更改）

### Q: 某些测试通过，某些失败
A:
1. 查看具体的错误信息
2. 检查 Fusion 360 API 文档
3. 验证参数格式正确性
4. 确认 Fusion 360 当前状态

### Q: 如何添加新的测试
A:
1. 继承 `Fusion360TestBase`
2. 使用 `call_real_tool` 或 `call_mcp_client_method`
3. 添加适当的错误处理
4. 更新 `run_tests.py`

## 最佳实践

### 1. 测试顺序
1. 先测试连接
2. 再测试基础功能
3. 最后测试复杂工作流

### 2. 错误处理
```python
if not self.check_prerequisites():
    self.skipTest("缺少必要的服务连接")
    return
```

### 3. 结果验证
```python
if result.get("success"):
    self.assert_api_call_success(result)
    print("✅ 操作成功")
else:
    print(f"❌ 操作失败: {result.get('error')}")
```

### 4. 资源清理
```python
def tearDown(self):
    # 清理创建的对象
    # 关闭连接
    super().tearDown()
```

## 贡献测试

如需添加新的测试用例:

1. 在 `tests/` 目录创建新的测试文件
2. 继承 `Fusion360TestBase`
3. 实现具体的测试方法
4. 添加到 `run_tests.py` 的测试套件中
5. 更新文档

测试用例应该覆盖:
- 正常情况
- 边界条件
- 错误处理
- 性能验证
