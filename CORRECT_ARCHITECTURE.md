# Fusion360 MCP 正确架构说明

## 🎯 架构澄清

经过讨论，我们现在有了正确的 MCP 架构理解：

### ✅ 正确的 MCP 协议理解

**MCP (Model Context Protocol)** 是基于 JSON-RPC 的协议，通过 stdio 或 SSE 通信，**不是 HTTP 协议**。

### 🔄 正确的系统架构

```
┌─────────────────┐   JSON-RPC      ┌──────────────────────┐    HTTP API    ┌──────────────────────┐
│   LLM客户端     │◄─────────────►│   MCP 服务器         │──────────────►│  Fusion 360 插件     │
│  (Claude等)     │  (stdio/SSE)   │  (FastMCP)          │   (内部调用)   │  (HTTP服务器)        │
│                 │                │  本项目核心         │               │  端口: 9000          │
└─────────────────┘                └──────────────────────┘               └──────────────────────┘
                                             │                                           │
                                             │ 注册工具                                   │
                                             ▼                                           ▼
                                  ┌──────────────────────┐                   ┌──────────────────────┐
                                  │   工具函数            │                   │    Fusion 360        │
                                  │ @app.tool()         │                   │      软件            │
                                  │ create_document()   │                   │   (本地 API)         │
                                  │ create_object()     │                   │                      │
                                  └──────────────────────┘                   └──────────────────────┘
```

### 📡 通信协议层次

1. **LLM客户端 ↔ MCP服务器**: JSON-RPC over stdio/SSE (MCP协议)
2. **MCP服务器 ↔ Fusion360插件**: HTTP API (内部实现细节)
3. **Fusion360插件 ↔ Fusion360软件**: Python API (本地调用)

### 🔧 组件职责

#### 1. LLM客户端 (Claude等)
- 通过 MCP 协议调用我们的 MCP 服务器
- 发送 JSON-RPC 请求到 stdio
- 接收工具调用结果

#### 2. MCP服务器 (本项目核心)
- 基于 FastMCP 框架
- 提供 `@app.tool()` 装饰的工具函数
- 被动被调用，**无端口**
- 内部调用 Fusion 360 插件的 HTTP API

#### 3. Fusion 360插件
- 内置 HTTP 服务器 (端口 9000)
- 等待 MCP 服务器的 HTTP 请求
- 调用 Fusion 360 本地 Python API
- 返回操作结果

#### 4. 工具函数 (`src/tools.py`)
- 被 MCP 服务器注册为工具
- 实现具体的 Fusion 360 操作逻辑
- 通过 HTTP 调用 Fusion 360 插件

## 🚀 正确的使用流程

### 1. 开发和测试阶段

```bash
# 1. 启动 Fusion 360 并加载插件 (端口 9000)
# 2. 测试工具函数
python tests/test_simple_integration.py
```

### 2. 生产使用阶段

```bash
# 1. 确保 Fusion 360 插件运行在端口 9000
# 2. 在 Claude 中配置 MCP 服务器
{
  "mcpServers": {
    "fusion360": {
      "command": "fusion360_mcp",
      "args": []
    }
  }
}
# 3. Claude 会自动调用我们的 MCP 服务器
```

## ❌ 之前的错误理解

1. **错误**: 认为 MCP 服务器需要 HTTP 端口 8000
   **正确**: MCP 服务器通过 stdio 通信，无端口

2. **错误**: 创建了 MCPClient 来调用 MCP 服务器
   **正确**: 只有 LLM 客户端调用 MCP 服务器，插件不需要客户端

3. **错误**: 认为需要手动启动 MCP 服务器
   **正确**: MCP 服务器由 LLM 客户端按需调用

## 🧪 单元测试策略

由于架构澄清，我们的测试策略：

1. **直接测试工具函数**: 测试 `src/tools.py` 中的函数
2. **模拟 Fusion 360 插件**: 确保 HTTP API 调用正确
3. **端到端测试**: 测试完整的工具调用链路

```bash
# 主要测试：直接调用工具函数
python tests/test_simple_integration.py

# 检查 Fusion 360 插件状态
curl http://localhost:9000/api/health
```

## 🎉 总结

现在我们有了正确的架构理解：

- **MCP 服务器**: FastMCP + JSON-RPC + stdio，无端口
- **Fusion 360 插件**: HTTP 服务器，端口 9000
- **通信流**: LLM → MCP服务器 → Fusion360插件 → Fusion360软件

这样的架构更符合 MCP 协议的设计理念，也更容易与 Claude 等 LLM 客户端集成。
