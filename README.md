# 智扫通机器人智能客服系统

基于 **FastAPI + Vue 3** 的智能客服系统，集成了 RAG（检索增强生成）和 AI Agent 能力。

## 项目简介

针对智能家居场景下用户咨询需求多样化、知识库检索精度不足的问题，设计实现的扫地机器人领域智能客服系统。

### 核心功能

- **智能问答**：基于 RAG 检索增强生成，从知识库精准检索并生成专业回答
- **Agent 工具调用**：集成 ReAct Agent，支持自主工具选择、多轮推理和场景切换
- **流式对话**：基于 SSE 实现 Token 级别实时响应
- **多会话管理**：每个会话维护独立的对话上下文
- **用户认证**：JWT + Refresh Token 双令牌机制
- **知识库管理**：支持 PDF、TXT、CSV 等格式文档的解析和向量化存储

### 技术亮点

- **混合检索架构**：向量检索 + 标题关键词匹配 + 语义重排序
- **ReAct 推理模式**：思考-行动-观察循环，支持多次工具调用
- **MCP 协议集成**：支持外部工具统一接入
- **前后端分离**：FastAPI 后端 + Vue 3 前端

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     前端层 (Vue 3)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  登录页   │  │  聊天页   │  │  仪表盘   │  │ 个人中心  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/SSE
┌──────────────────────┴──────────────────────────────────┐
│                   API 层 (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ 认证模块  │  │ 聊天模块  │  │ 用户模块  │  │ 仪表盘模块 │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│              核心能力层                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ReAct Agent│ │RAG Service│ │VectorStore│              │
│  └──────────┘  └──────────┘  └──────────┘              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  MCP工具  │  │ 混合检索  │  │ 模型工厂  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                  数据存储层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   MySQL   │  │  Chroma  │  │  文件系统  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 技术         | 说明                |
| ------------ | ------------------- |
| FastAPI      | 高性能异步 Web 框架 |
| LangChain    | LLM 应用框架        |
| LangGraph    | Agent 工作流编排    |
| Chroma       | 向量数据库          |
| Tortoise-ORM | 异步 ORM 框架       |
| MySQL        | 关系型数据库        |
| JWT          | 用户认证            |
| Vue 3 + Vite | 前端框架与构建工具  |
| Element Plus | Vue 3 UI 组件库     |

## 项目结构

```
zst_agent-master/
├── agent/                      # Agent 模块
│   ├── react_agent.py         # ReAct Agent
│   ├── mcp/                   # MCP 工具集成
│   └── tools/                 # Agent 工具与中间件
├── rag/                        # RAG 模块
│   ├── rag_service.py         # RAG 服务
│   ├── vector_store.py        # 向量存储
│   └── hybrid_retrieval.py    # 混合检索
├── model/                      # 模型工厂 (LLM + Embedding + Reranker)
│   └── factory.py
├── app/                        # FastAPI 后端应用
│   ├── api/v1/                # API 路由
│   ├── core/                  # 核心配置 (DB/JWT/Agent管理)
│   ├── models/                # 数据库模型
│   ├── schemas/               # Pydantic 模式
│   └── services/              # 业务服务层
├── config/                     # 配置文件 (仅 Chroma 和 Prompts 路径)
│   ├── chroma.yml
│   └── prompts.yml
├── prompts/                    # 提示词模板
├── data/                       # 知识库文档
├── frontend/                   # Vue 3 前端
├── scripts/                    # SQL 初始化脚本
├── utils/                      # 工具模块
├── .env.example               # 环境变量模板
├── pyproject.toml             # uv 项目配置
└── uv.lock                    # 依赖锁定文件
```

## 快速开始

### 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理器
- Node.js 16+
- MySQL 8.0+
- 阿里云 DashScope API Key

### 1. 安装依赖

```bash
# 进入项目目录
cd zst_agent-master

# 使用 uv 安装依赖
uv sync
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入真实配置（API Key、数据库密码等）
```

### 3. 初始化数据库

**Linux / macOS / Windows CMD：**

```bash
mysql -u root -p < scripts/init_db.sql
```

**Windows PowerShell：**

```powershell
Get-Content scripts/init_db.sql | mysql -u root -p"你的密码"
```

### 4. 启动后端

```bash
uv run uvicorn app.main:app --reload --port 8000
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 6. 访问系统

- **前端地址**: http://127.0.0.1:3000
- **后端 API 文档**: http://127.0.0.1:8000/docs
- **默认账号**: admin / admin123

## 核心模块详解

### 1. RAG 混合检索

三级混合检索架构：向量检索（Chroma 语义相似度） + 标题关键词匹配（Jieba 分词 + Embedding 精排） + 统一重排序（BGE-Reranker）。

核心文件：[`rag/`](file:///d:/总结/大模型/黑马程序员大模型RAG与Agent智能体项目实战/zst_agent-master/rag)

```python
from rag.rag_service import RagSummarizeService
from rag.vector_store import VectorStoreService

vector_store = VectorStoreService()
rag_service = RagSummarizeService(vector_store)
result = rag_service.rag_summarize(query="小户型适合哪种扫地机器人？", search_mode="hybrid")
```

### 2. ReAct Agent

Thinking → Acting → Observing 循环模式。自定义工具 + MCP 工具（WebSearch 等），支持中间件机制（日志、场景切换）。

核心文件：[`agent/react_agent.py`](file:///d:/总结/大模型/黑马程序员大模型RAG与Agent智能体项目实战/zst_agent-master/agent/react_agent.py)

```python
from agent.react_agent import ReactAgent

agent = ReactAgent()
for chunk in agent.execute_stream("推荐一款适合小户型的扫地机器人"):
    print(chunk, end="", flush=True)
```

### 3. SSE 流式响应

基于 Server-Sent Events 实现 Token 级别流式输出，核心在 `app/api/v1/chat.py`。

### 4. JWT 双令牌认证

Access Token（30分钟） + Refresh Token（7天），核心在 `app/core/security.py`。

## 环境变量配置

所有运行配置通过 `.env` 管理，参考 [.env.example](file:///d:/总结/大模型/黑马程序员大模型RAG与Agent智能体项目实战/zst_agent-master/.env.example)：

| 变量                     | 说明                  | 默认值                                   |
| ------------------------ | --------------------- | ---------------------------------------- |
| `CHAT_MODEL_NAME`      | 聊天模型              | `qwen3-max`                            |
| `EMBEDDING_MODEL_NAME` | Embedding 模型        | `text-embedding-v4`                    |
| `DASHSCOPE_API_KEY`    | 阿里云 DashScope 密钥 | 必填                                     |
| `RERANKER_API_URL`     | 重排序 API 地址       | `https://api.siliconflow.cn/v1/rerank` |
| `RERANKER_MODEL`       | 重排序模型            | `BAAI/bge-reranker-v2-m3`              |
| `RERANKER_API_KEY`     | 重排序 API 密钥       | 可选                                     |
| `MYSQL_HOST`           | 数据库地址            | `localhost`                            |
| `MYSQL_PASSWORD`       | 数据库密码            | 必填                                     |

## 常见问题

### 如何更换大模型？

修改 `.env` 中的 `CHAT_MODEL_NAME`，或修改 `model/factory.py` 中的模型工厂类。

### 如何添加新的知识文档？

将文档放入 `data/` 目录，删除 `chroma_db/`，重启服务即可自动重建索引。

### 向量数据库如何初始化？

系统首次调用 RAG 服务时自动初始化，无需手动操作。

### Agent 工具调用失败？

检查 DashScope API Key 是否正确配置，查看 `logs/` 目录下的日志文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0

- RAG 混合检索功能
- ReAct Agent 工作流
- SSE 流式对话
- JWT 双令牌认证
- 前后端分离架构
