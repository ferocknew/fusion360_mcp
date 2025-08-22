# Fusion360 LLM 建模助手

一个基于 FastMCP 和 Fusion 360 API 的语义化建模系统，让大语言模型可以通过自然语言进行 3D 建模操作。

## 系统架构

```
┌─────────────────┐    natural    ┌──────────────────────┐
│   User (LLM)    │◄──────────────┤  Natural Language    │
└─────────┬───────┘   language   └──────────────────────┘
          │
          │ API Calls
          ▼
┌─────────────────┐    Fusion360  ┌──────────────────────┐
│   MCP Server    │◄──────────────┤  Fusion 360 Add-in   │
│  (FastMCP)      │    API Calls  │                      │
└─────────────────┘               └──────────────────────┘
```

## 功能特点

- 🗣️ **自然语言建模**: 使用自然语言描述创建 3D 模型
- 🔧 **API 集成**: 直接调用 Fusion 360 原生 API
- ⚡ **实时处理**: 快速响应和执行建模命令
- 🤖 **AI 驱动**: 利用大语言模型理解用户意图
- 📦 **易于安装**: 通过 PyPI 分发，使用 uvx 执行

## 项目结构

```
fusion360_mcp/
├── mcp_server/         # FastMCP 服务器实现
├── addin/              # Fusion 360 插件
└── examples/           # 使用示例
```

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
uvx fusion360-mcp

# 或者安装后运行
pip install fusion360-mcp
fusion360-mcp
```

### 3. MCP 服务器设置

```bash
# 克隆项目（开发用途）
git clone <repository-url>
cd fusion360_mcp

# 安装依赖
pip install fastmcp fusion360-api-wrapper

# 启动 MCP 服务器
python mcp_server/main.py
```

### 4. Fusion 360 插件安装

1. 打开 Fusion 360
2. 进入 `工具` > `附加模块` > `开发`
3. 安装 `addin/` 目录中的插件
4. 配置插件连接 MCP 服务器地址

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

1. 启动 MCP 服务器
2. 在 Fusion 360 中启用插件
3. 使用自然语言描述建模需求
4. 系统自动转换并执行建模操作

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

## 开发指南

### 添加新功能

1. 在 `mcp_server/` 中扩展 API 端点
2. 在 Fusion 360 插件中实现对应的 API 调用
3. 更新 LLM 提示词以识别新功能

### 代码结构

```
project/
├── mcp_server/
│   ├── main.py              # 服务器入口点
│   ├── api/                 # API 路由定义
│   ├── handlers/            # 请求处理逻辑
│   └── fusion360_client.py  # Fusion 360 API 客户端
├── addin/
│   ├── addin.py             # 插件主文件
│   └── api_client.py        # API 客户端
├── llm_interface.py         # LLM 接口处理
└── examples/                # 使用示例
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

项目链接: [https://github.com/yourusername/fusion360_mcp](https://github.com/yourusername/fusion360_mcp)

## 注意事项

- 确保 Fusion 360 已正确配置开发环境
- MCP 服务器需要与 Fusion 360 插件保持网络连接
- 某些复杂建模操作可能需要手动调整
- 建议在测试环境中验证所有操作