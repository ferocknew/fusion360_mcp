# Fusion360 LLM 建模助手

一个基于 FastMCP 和 Fusion 360 API 的语义化建模系统，让大语言模型可以通过自然语言进行 3D 建模操作。


**正确的协议层次：**
1. **LLM ↔ MCP服务器**: JSON-RPC over stdio/SSE (MCP协议)
2. **MCP服务器 ↔ Fusion360插件**: HTTP API (内部实现)
3. **Fusion360插件 ↔ Fusion360软件**: Python API (本地调用)

## 功能特点

- 🗣️ **自然语言建模**: 使用自然语言描述创建 3D 模型
- 🔧 **API 集成**: 直接调用 Fusion 360 原生 API
- ⚡ **实时处理**: 快速响应和执行建模命令
- 🤖 **AI 驱动**: 利用大语言模型理解用户意图
- 📦 **易于安装**: 通过 PyPI 分发，使用 uvx 执行

## 安装与配置

### 1. 环境要求

- Python 3.11+
- Fusion 360 (最新版本)
- FastMCP
- 支持的 LLM API (如 OpenAI, Qwen 等)

### 2. 安装方式

项目已发布到 PyPI，可以通过以下方式安装和运行：

```bash
# 使用 uvx 直接运行（推荐）
uvx --from fusion360-mcp fusion360_mcp --help
```



### 4. Fusion 360 插件安装

#### 重要端口说明
- **MCP 服务器**: 无端口，被动被调用 (通过 stdio 或 MCP 协议)
- **Fusion 360 插件HTTP服务端口**: `9000` (固定) - 接收工具模块的HTTP请求

⚠️ **请确保端口 9000 没有被其他应用占用**，这是 Fusion 360 插件内置HTTP服务器的专用端口。

#### 安装步骤
1. 打开 Fusion 360
2. 进入 `工具` > `附加模块` > `开发`
3. 点击 "+" 按钮添加插件
4. 选择 `addin/fusion360_mcp_addin/` 文件夹（包含 .py 和 .manifest 文件）
5. 勾选插件以启动
6. 插件启动后会显示确认消息，服务地址为: `http://localhost:9000`

#### 验证插件运行
```bash
# 检查插件是否正常运行
curl http://localhost:9000/api/health

# 预期响应
{"status": "healthy", "message": "Fusion 360 插件运行正常"}
```

### 5. LLM 配置

配置您的 LLM API 密钥和服务端点：

```env
LLM_API_KEY=your_api_key_here
LLM_ENDPOINT=https://api.your-llm-service.com
MCP_SERVER_URL=http://localhost:8000
```

## 支持的 Fusion 360 工具

系统提供以下 Fusion 360 操作方法：

- [ ] `create_document`: 在 Fusion 360 中创建新文档
- [ ] `create_object`: 在 Fusion 360 中创建新对象
- [ ] `edit_object`: 在 Fusion 360 中编辑对象
- [ ] `delete_object`: 在 Fusion 360 中删除对象
- [ ] `execute_code`: 在 Fusion 360 中执行任意 Python 代码
- [ ] `insert_part_from_library`: 从零件库中插入零件
- [ ] `get_view`: 获取活动视图的截图
- [ ] `get_objects`: 获取文档中的所有对象
- [ ] `get_object`: 获取文档中的特定对象
- [ ] `get_parts_list`: 获取零件库中的零件列表

## 使用方法

### 基本工作流程

1. **安装项目**
   ```bash
   # 安装项目
   pip install -e .
   ```

2. **启动 Fusion 360 并加载插件**
   - 确保插件正在端口 9000 运行
   - 验证: `curl http://localhost:9000/api/health`

3. **配置 LLM 客户端 (Claude)**
   ```json
   {
     "mcpServers": {
       "fusion360": {
         "command": "uvx",
         "args": ["fusion360-mcp"]
       }
     }
   }
   ```

4. **测试工具模块 (开发用)**
   ```bash
   # 快速测试工具函数
   python tests/test_simple_integration.py
   ```

5. **使用方式**
   - LLM 客户端通过 MCP 协议调用我们的服务器
   - MCP 服务器内部调用 Fusion 360 插件完成建模
   - 无需手动启动 MCP 服务器 (由 LLM 客户端调用)

### 端口占用检查

如果遇到端口冲突，可以检查端口使用情况：

```bash
# 检查端口 9000 (Fusion 360 插件HTTP服务)
netstat -an | grep 9000
lsof -i :9000

# 使用项目提供的端口检查脚本
python scripts/check_ports.py
```

**注意：**
- MCP 服务器本身没有端口，是被动被调用的
- 只有 Fusion 360 插件需要端口 9000
- 如端口被占用，需要释放该端口

### 示例命令

```
"创建一个高度为 100mm，直径为 50mm 的圆柱体"

"在 XY 平面上绘制一个边长为 80mm 的正方形，并拉伸 30mm"

"创建一个立方体，尺寸为 100x50x200mm，然后在中心钻一个直径 20mm 的孔"

"创建一个齿轮，模数为 2，齿数为 20"
```

## API 接口

### MCP 服务器端点

- `POST /model/create` - 创建新模型
- `POST /feature/add` - 添加特征
- `POST /modify/parameters` - 修改参数
- `GET /model/status` - 获取模型状态

### 请求示例

```json
{
  "command": "create_cylinder",
  "parameters": {
    "height": 100,
    "diameter": 50,
    "position": [0, 0, 0]
  },
  "metadata": {
    "request_id": "uuid-string",
    "timestamp": "ISO-timestamp"
  }
}
```


## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

项目链接: [https://github.com/yourusername/fusion360_mcp](https://github.com/yourusername/fusion360_mcp)

## 注意事项

### 端口管理
- **端口 8000**: MCP 服务器端口（可配置）- 提供MCP协议服务，供LLM客户端连接
- **端口 9000**: Fusion 360 插件HTTP服务端口（固定）- 插件内置的HTTP服务器，接收MCP服务器请求
- 启动前请确保这两个端口未被其他应用占用

### 通信流程
1. **LLM客户端** ↔ **MCP服务器** (端口8000，MCP协议)
2. **MCP服务器** ↔ **Fusion 360插件HTTP服务** (端口9000，HTTP协议)
3. **Fusion 360插件** ↔ **Fusion 360软件** (本地API调用)

### 连接要求
- MCP 服务器与 Fusion 360 插件必须在同一台机器上运行
- 两个服务都使用 localhost 地址，确保防火墙不阻止本地连接
- 插件启动后会在 Fusion 360 中显示确认消息

### 开发环境
- 确保 Fusion 360 已正确配置开发环境
- 插件需要在 Fusion 360 的开发模式下运行
- 某些复杂建模操作可能需要手动调整
- 建议在测试环境中验证所有操作

### 故障排除
如果遇到连接问题：
1. 检查端口是否被占用: `lsof -i :8000` 和 `lsof -i :9000`
2. 确认 MCP 服务器正在运行: `curl http://localhost:8000/health`
3. 确认 Fusion 360 插件已启动: `curl http://localhost:9000/api/health`
4. 查看 Fusion 360 开发控制台的错误信息

## 相关文档
- Fusion 360 api ： https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A