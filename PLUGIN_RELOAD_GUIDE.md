# Fusion 360 插件重新加载指南

## 🔄 当您修改了插件代码后，需要重新加载插件

### 问题现象
- 修改了 `addin/fusion360_mcp_addin/fusion360_mcp_addin.py` 文件
- 测试仍然显示旧的错误信息
- API 调用返回过期的错误

### 原因
Fusion 360 插件在运行时不会自动重新加载 Python 代码。需要手动重新启动插件。

### 解决步骤

#### 1. 停止当前插件
1. 打开 Fusion 360
2. 进入 **工具 > 附加模块 > 开发**
3. 在插件列表中找到 **"Fusion360 MCP Addin"**
4. 点击 **"停止"** 按钮

#### 2. 重新启动插件
1. 在同一个界面中，点击 **"运行"** 按钮
2. 或者删除插件后重新添加：
   - 点击 **"删除"**
   - 点击 **"添加插件"**
   - 选择 `addin/fusion360_mcp_addin/` 文件夹

#### 3. 验证重新加载
检查插件是否使用新代码：
```bash
curl http://localhost:9000/api/status
```

应该看到新的状态信息，没有 `productName` 错误。

### 🔧 最新修复
我们已经修复了插件中的 `productName` 属性错误：

**修复内容：**
- 安全地检查 Application 对象的属性
- 使用 `hasattr()` 检查属性是否存在
- 提供默认值避免崩溃
- 更好的错误处理

**修复位置：**
`addin/fusion360_mcp_addin/fusion360_mcp_addin.py` 的 `get_fusion_status()` 函数

### 📝 测试验证
重新加载插件后，运行以下测试验证修复：

```bash
cd tests
python -m pytest test_view_functionality.py::TestViewCaptureFunctionality::test_02_get_fusion360_status -v -s
```

应该看到：
- ✅ 状态获取成功
- 显示正确的应用名称和版本信息
- 没有 `productName` 错误

### 💡 开发提示
在开发过程中，每次修改插件代码后都需要重新加载插件。建议：

1. **频繁测试**：每次修改后立即重新加载和测试
2. **日志记录**：查看插件的日志输出了解运行状态
3. **增量修改**：小步骤修改，方便定位问题

---

**下一步：** 重新加载插件后，继续运行视图截图功能的完整测试！
