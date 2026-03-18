# Metis_ParseBot - 智能知识采集与分析系统

## 项目概述

Metis_ParseBot 是一个多智能体协作系统，专注于自动采集、筛选和总结人工智能、信息安全及其交叉领域的前沿知识，帮助用户高效掌握新知识。

### 核心功能

- **自动采集**: 从多个数据源采集学术论文和工程新闻
- **智能筛选**: AI驱动的五维度价值评分机制，过滤低质量内容
- **深度分析**: 总结核心内容，关联相关知识，辨析易混淆点
- **学习管理**: 结构化存储学习记录，支持已读标记、收藏、笔记
- **可视化配置**: 前端直接配置LLM参数，无需手动编辑配置文件

### 项目状态

| 阶段 | 状态 | 说明 |
|------|------|------|
| 基础架构 | ✅ 完成 | 项目结构、配置、数据库模型 |
| 三智能体 | ✅ 完成 | 采集、预审、分析智能体 |
| API开发 | ✅ 完成 | FastAPI RESTful API |
| 前端界面 | ✅ 完成 | React + TypeScript + TailwindCSS |
| 功能优化 | ✅ 完成 | 搜索、分页、设置重构 |
| 文档完善 | ✅ 完成 | architecture.md、更新README |

---

## 系统架构

### 三智能体协作流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   采集智能体     │────▶│   预审智能体     │────▶│   分析智能体     │
│   Collector     │     │   Reviewer      │     │   Analyzer      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   多数据源采集            五维度评分              内容总结分析
   自动分类标签            及格线过滤              知识关联辨析
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  学习记录存储  │
                        │  LearningRecord│
                        └───────────────┘
```

### 数据源

| 类型 | 来源 | 说明 |
|------|------|------|
| 学术论文 | arXiv, OpenReview, Semantic Scholar, Papers with Code | AI/安全/交叉领域论文 |
| 技术新闻 | Hacker News, GitHub Trending, Hugging Face | 开源项目、模型发布 |
| 安全资讯 | FreeBuf, 安全牛 | 网络安全动态 |
| AI博客 | OpenAI, Anthropic, Google AI | 一手发布信息 |

### 内容分类标签

格式：`主题+分类`

- **主题**: AI / 安全 / AI&安全
- **分类**: 学术 / 工程

示例：`AI+学术`、`安全+工程`、`AI&安全+学术`

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| **前端** | React + TypeScript + TailwindCSS + Vite | 18.x |
| **后端** | FastAPI (Python 3.10+) | 0.100+ |
| **智能体** | LangChain | 0.1+ |
| **LLM** | OpenAI API / 兼容API | - |
| **数据库** | SQLite (开发) / PostgreSQL (生产) | - |
| **任务调度** | APScheduler | 3.x |
| **容器化** | Docker + Docker Compose | - |

---

## 项目结构

```
Metis_ParseBot/
├── src/                        # 后端源码
│   ├── agents/                 # 三智能体
│   │   ├── collector/          # 采集智能体
│   │   │   ├── agent.py        # 采集逻辑
│   │   │   ├── sources/        # 数据源适配器
│   │   │   └── prompts.py      # 提示词模板
│   │   ├── reviewer/           # 预审智能体
│   │   │   ├── agent.py        # 预审逻辑
│   │   │   ├── scorer.py       # 评分引擎
│   │   │   └── prompts.py
│   │   └── analyzer/           # 分析智能体
│   │       ├── agent.py        # 分析逻辑
│   │       ├── summarizer.py   # 总结生成
│   │       ├── knowledge.py    # 知识关联
│   │       └── prompts.py
│   ├── api/                    # FastAPI 应用
│   │   ├── main.py             # 应用入口
│   │   ├── routes/             # API路由
│   │   └── schemas.py          # 数据模型
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── logging.py          # 日志配置
│   │   └── exceptions.py       # 异常定义
│   ├── db/                     # 数据库
│   │   ├── models.py           # ORM模型
│   │   └── crud.py             # 数据操作
│   └── services/               # 业务服务
│       ├── pipeline.py         # 处理流水线
│       └── scheduler.py        # 任务调度
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── components/         # UI组件
│   │   ├── pages/              # 页面
│   │   ├── services/           # API调用
│   │   └── types/              # 类型定义
│   └── ...
├── tests/                      # 测试代码
├── docker/                     # Docker配置
├── data/                       # 数据目录
├── architecture.md             # 架构文档
├── worklog.md                  # 工作日志
├── workplan.md                 # 工作规划
├── TODO.md                     # 待办事项
├── requirements.txt            # Python依赖
└── .env.example                # 环境变量模板
```

---

## 核心功能模块

### 1. 仪表盘 (Dashboard)
- 系统状态概览：总内容数、待预审、已采纳、已分析
- 最近采集内容列表
- 快捷操作：采集、预审、分析、完整流水线
- 进度条显示（预审/分析时实时更新）

### 2. 内容库 (Contents)
- 四个标签页：已采纳(待分析)、已分析、已拒绝、待预审
- 列表/网格视图切换
- 后端搜索功能（跨页搜索）
- 分页显示（支持跳转）
- 内容卡片：标题、来源、分类、评分、标签

### 3. 学习中心 (Learning)
- 三个标签页：未学习、已学习、收藏（带计数）
- 按分数降序排列
- 原地展开详情：完整总结、关键要点、知识关联、易混淆辨析、学习建议
- 学习笔记编辑功能
- 标记已读、收藏操作

### 4. 设置 (Settings)
- 系统状态：应用名称、版本、数据库类型/地址、LLM提供商/模型
- LLM配置可视化编辑：API Key、Base URL、模型名称、Temperature、及格分数、采集间隔
- 定时任务调度器：功能说明、启停控制

---

## 预审评分系统

五维度评分（总分100）：

| 维度 | 权重 | 说明 |
|------|------|------|
| 新颖性 | 25% | 内容的创新程度 |
| 实用性 | 25% | 对学习者的实际价值 |
| 权威性 | 20% | 来源可靠性 |
| 时效性 | 15% | 内容的时效价值 |
| 完整性 | 15% | 信息完整程度 |

及格线：60分

---

## 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone <repository_url>
cd Metis_ParseBot

# 2. 运行启动脚本（Windows）
start.bat
# 选择 1. 运行服务
# 脚本会自动检测环境、安装依赖、启动后端和前端

# 3. 或手动启动
# 后端
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY
python -m src.api.main

# 前端
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
# 配置环境变量
copy .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 启动所有服务
docker-compose up -d

# 访问
# 前端: http://localhost
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 访问地址

- 前端界面: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

---

## 环境配置

创建 `.env` 文件：

```env
# LLM API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4
MODEL_TEMPERATURE=0.2

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/metis.db

# 采集配置
COLLECT_INTERVAL_HOURS=6
MAX_ITEMS_PER_RUN=50
CONTENT_AGE_LIMIT_DAYS=15

# 预审配置
PASSING_SCORE=60
```

> 也可以在前端设置页面直接配置LLM参数

---

## API 接口概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/contents` | GET | 获取内容列表（支持搜索、分页） |
| `/api/contents/dashboard` | GET | 获取仪表盘统计数据 |
| `/api/collect` | POST | 触发采集 |
| `/api/review` | POST | 触发预审 |
| `/api/review/progress` | GET | 获取预审进度 |
| `/api/analyze` | POST | 触发分析 |
| `/api/analyze/progress` | GET | 获取分析进度 |
| `/api/learning` | GET | 获取学习记录列表 |
| `/api/learning/{id}` | PATCH | 更新学习记录（已读/收藏/笔记） |
| `/api/settings` | GET | 获取系统设置 |
| `/api/settings/env` | GET/POST | 读取/保存环境配置 |
| `/api/pipeline` | POST | 执行完整流水线 |

---

## 开发规范

- **代码风格**: PEP 8 (Python) / ESLint (TypeScript)
- **提交规范**: Conventional Commits
- **分支策略**: Git Flow
- **文档**: 所有模块需包含docstring

---

## 文档索引

| 文档 | 说明 |
|------|------|
| `architecture.md` | 系统架构、模块说明、API索引 |
| `worklog.md` | 开发工作日志 |
| `workplan.md` | 项目规划与进度 |
| `TODO.md` | 待办事项与问题记录 |
| `AGENTS.md` | 智能体详细设计 |

---

## License

MIT License