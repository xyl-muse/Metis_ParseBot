# Metis_ParseBot 架构文档

> 本文档用于上下文窗口用尽时快速回顾项目结构和关键信息。

## 项目概述

**Metis_ParseBot** 是一个多智能体协作系统，专注于自动采集、筛选和总结人工智能、信息安全及其交叉领域的前沿知识。

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + TypeScript + TailwindCSS + Vite |
| 后端 | FastAPI (Python 3.10+) |
| 智能体框架 | LangChain + OpenAI API |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| 任务调度 | APScheduler |
| 容器化 | Docker + Docker Compose |

---

## 项目结构

```
Metis_ParseBot/
├── src/                          # 后端源码
│   ├── agents/                   # 三智能体模块
│   │   ├── base.py              # 智能体基类 (BaseAgent)
│   │   ├── collector/           # 采集智能体
│   │   │   ├── agent.py         # CollectorAgent - 内容采集和分类
│   │   │   ├── prompts.py       # 采集相关提示词模板
│   │   │   └── sources/         # 数据源适配器
│   │   │       ├── base.py      # BaseSource - 数据源基类
│   │   │       ├── arxiv.py     # arXiv 论文采集
│   │   │       ├── academic.py  # OpenReview/Semantic Scholar
│   │   │       ├── news.py      # HackerNews/Reddit
│   │   │       └── tech_news.py # GitHub Trending/HuggingFace
│   │   ├── reviewer/            # 预审智能体
│   │   │   ├── agent.py         # ReviewerAgent - 五维度评分
│   │   │   ├── scorer.py        # 评分引擎 (加权计算)
│   │   │   └── prompts.py       # 预审提示词模板
│   │   └── analyzer/            # 分析智能体
│   │       ├── agent.py         # AnalyzerAgent - 深度分析
│   │       ├── summarizer.py    # 内容总结生成
│   │       ├── knowledge.py     # 知识关联分析
│   │       └── prompts.py       # 分析提示词模板
│   │
│   ├── api/                     # FastAPI 应用
│   │   ├── main.py              # 应用入口、路由注册、生命周期
│   │   ├── schemas.py           # Pydantic 数据模型
│   │   └── routes/              # API 路由模块
│   │       ├── contents.py      # 内容管理 API
│   │       ├── collect.py       # 采集 API
│   │       ├── review.py        # 预审 API
│   │       ├── analyze.py       # 分析 API
│   │       ├── learning.py      # 学习记录 API
│   │       └── settings.py      # 系统设置 API
│   │
│   ├── core/                    # 核心配置
│   │   ├── config.py            # Settings - 环境变量配置
│   │   ├── logging.py           # 日志配置
│   │   └── exceptions.py        # 自定义异常
│   │
│   ├── db/                      # 数据库层
│   │   ├── models.py            # SQLAlchemy ORM 模型
│   │   ├── crud.py              # CRUD 操作封装
│   │   └── migrations/          # 数据库迁移
│   │
│   └── services/                # 业务服务
│       ├── pipeline.py          # 处理流水线 (采集→预审→分析)
│       └── scheduler.py         # 定时任务调度
│
├── frontend/                    # 前端项目
│   └── src/
│       ├── components/          # UI 组件
│       │   ├── Layout.tsx       # 页面布局 (侧边栏+顶栏)
│       │   ├── Card.tsx         # 卡片容器
│       │   ├── Button.tsx       # 按钮
│       │   ├── Badge.tsx        # 标签徽章
│       │   ├── ScoreDisplay.tsx # 分数显示
│       │   ├── ContentCard.tsx  # 内容卡片
│       │   └── ContentListItem.tsx # 内容列表项
│       │
│       ├── pages/               # 页面组件
│       │   ├── Dashboard.tsx    # 仪表盘 (概览+快捷操作)
│       │   ├── Contents.tsx     # 内容库 (按状态分类)
│       │   ├── ContentDetail.tsx# 内容详情
│       │   ├── LearningRecords.tsx # 学习中心 (未学习/已学习/收藏)
│       │   └── Settings.tsx     # 系统设置
│       │
│       ├── services/
│       │   └── api.ts           # API 调用封装
│       │
│       └── types/
│           └── index.ts         # TypeScript 类型定义
│
├── data/                        # 数据目录 (SQLite 数据库)
├── tests/                       # 测试代码
├── docker/                      # Docker 配置
└── requirements.txt             # Python 依赖
```

---

## 核心模块详解

### 1. 三智能体架构

系统采用三智能体协作模式，形成完整的处理流水线：

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  CollectorAgent │ ──► │  ReviewerAgent  │ ──► │  AnalyzerAgent  │
│    采集智能体    │     │    预审智能体    │     │    分析智能体    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   Content.status           Review.passed          LearningRecord
   = "pending"              = True/False           (最终输出)
```

#### CollectorAgent (采集智能体)
- **职责**: 从多数据源采集内容并分类
- **数据源**:
  - 学术论文: arXiv, OpenReview, Semantic Scholar, Papers with Code
  - 技术新闻: GitHub Trending, Hugging Face
  - 安全资讯: FreeBuf, 安全牛
  - AI博客: OpenAI, Anthropic, Google AI
- **分类标签**: `academic_ai`, `academic_security`, `academic_cross`, `news_ai`, `news_security`, `news_cross`
- **关键特性**: 时效性过滤（仅采集近15天内容）、去重检查

#### ReviewerAgent (预审智能体)
- **职责**: 评估内容价值，过滤低质量内容
- **五维度评分** (总分100):
  - 新颖性 (novelty): 0-25
  - 实用性 (utility): 0-25
  - 权威性 (authority): 0-20
  - 时效性 (timeliness): 0-15
  - 完整性 (completeness): 0-15
- **及格线**: 60分 (可配置)
- **API限流保护**: 每次评分间隔2秒

#### AnalyzerAgent (分析智能体)
- **职责**: 对通过预审的内容进行深度分析
- **输出内容**:
  - 核心总结 (summary)
  - 关键要点 (key_points)
  - 知识关联 (knowledge_links)
  - 易混淆辨析 (confusion_notes)
  - 学习建议 (learning_suggestions)
- **双语支持**: 英文内容输出双语对照
- **API限流保护**: 每次分析间隔3秒

### 2. 数据模型 (ORM)

| 模型 | 说明 | 关键字段 |
|------|------|----------|
| **Content** | 采集内容 | id, title, source, source_url, category, status, tags |
| **Review** | 预审记录 | content_id, total_score, novelty_score, utility_score, passed |
| **Analysis** | 分析结果 | content_id, summary, key_points, knowledge_links, confusion_notes |
| **LearningRecord** | 学习记录 | content_id, title, total_score, is_read, is_bookmarked, user_notes |
| **CollectionJob** | 采集任务 | source, status, items_found, items_collected |

**内容状态流转**:
```
pending (待预审) → reviewed (已采纳/待分析) → analyzed (已分析)
                ↘ rejected (已拒绝)
```

### 3. 配置管理 (Settings)

位置: `src/core/config.py`

**关键配置项**:
```python
# LLM 配置
openai_api_key: str           # API Key
openai_api_base: str          # API 端点 (支持自定义)
model_name: str = "gpt-4"     # 模型名称
model_temperature: float = 0.2 # 温度 (降低随机性)

# 数据库
database_url: str             # 数据库连接字符串

# 预审
passing_score: int = 60       # 及格线
score_weights: dict           # 评分权重

# 采集
content_age_limit_days: int = 15  # 内容时效限制
```

---

## API 接口文档

### 基础端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 系统状态 |
| GET | `/health` | 健康检查 |
| GET | `/status` | 系统详情 |

### 内容管理 (`/api/contents`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/contents` | 获取内容列表 (支持分页、搜索、状态筛选) |
| GET | `/api/contents/{id}` | 获取单个内容详情 |
| DELETE | `/api/contents/{id}` | 删除内容 |
| GET | `/api/contents/dashboard` | 获取仪表盘统计数据 |

**查询参数**:
- `status`: 状态筛选 (pending/reviewed/analyzed/rejected)
- `category`: 分类筛选
- `search`: 标题搜索
- `page`, `page_size`: 分页

### 采集 (`/api/collect`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/collect` | 触发采集任务 |
| GET | `/api/collect/sources` | 获取可用数据源列表 |

### 预审 (`/api/review`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/review` | 触发预审任务 (后台执行) |
| GET | `/api/review/progress` | 获取预审进度 |
| GET | `/api/review/pending` | 获取待预审内容 |
| GET | `/api/review/{content_id}` | 获取内容的预审结果 |

### 分析 (`/api/analyze`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/analyze` | 触发分析任务 (后台执行) |
| GET | `/api/analyze/progress` | 获取分析进度 |
| GET | `/api/analyze/{content_id}` | 获取内容的分析结果 |

### 学习记录 (`/api/learning`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/learning` | 获取学习记录列表 |
| GET | `/api/learning/{id}` | 获取单个学习记录 |
| PATCH | `/api/learning/{id}` | 更新学习记录 (已读/收藏/笔记) |
| DELETE | `/api/learning/{id}` | 删除学习记录 |

### 流水线 (`/api/pipeline`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/pipeline` | 执行完整流水线 (采集→预审→分析) |

**请求体**:
```json
{
  "collect": true,
  "review": true,
  "analyze": true,
  "limit": 20
}
```

### 系统设置 (`/api/settings`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/settings` | 获取系统详细状态 |
| GET | `/api/settings/env` | 读取环境配置 |
| POST | `/api/settings/env` | 保存环境配置到.env文件 |
| POST | `/api/settings/scheduler/start` | 启动定时调度器 |
| POST | `/api/settings/scheduler/stop` | 停止定时调度器 |

---

## 前端页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | Dashboard | 仪表盘，显示统计和快捷操作 |
| `/contents` | Contents | 内容库，按状态分标签页展示 |
| `/contents/:id` | ContentDetail | 内容详情页 |
| `/learning` | LearningRecords | 学习中心，未学习/已学习/收藏 |
| `/settings` | Settings | 系统设置 |

---

## 依赖关系图

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │Dashboard│  │Contents │  │Learning │  │    Settings     │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘ │
│       └────────────┴────────────┴─────────────────┘          │
│                           │                                  │
│                      services/api.ts                         │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    API Routes                         │   │
│  │  contents | collect | review | analyze | learning    │   │
│  └───────────────────────────┬──────────────────────────┘   │
│                              │                               │
│  ┌───────────────────────────┴──────────────────────────┐   │
│  │                    Services Layer                     │   │
│  │              Pipeline | Scheduler                     │   │
│  └───────────────────────────┬──────────────────────────┘   │
│                              │                               │
│  ┌───────────────────────────┴──────────────────────────┐   │
│  │                    Agents Layer                       │   │
│  │    CollectorAgent | ReviewerAgent | AnalyzerAgent    │   │
│  └───────────────────────────┬──────────────────────────┘   │
│                              │                               │
│  ┌───────────────────────────┴──────────────────────────┐   │
│  │                  LangChain + OpenAI API               │   │
│  └───────────────────────────────────────────────────────┘   │
│                              │                               │
│  ┌───────────────────────────┴──────────────────────────┐   │
│  │                    Database Layer                     │   │
│  │         SQLAlchemy ORM | SQLite/PostgreSQL           │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 关键文件快速索引

| 功能 | 文件路径 |
|------|----------|
| 应用入口 | `src/api/main.py` |
| 智能体基类 | `src/agents/base.py` |
| 采集智能体 | `src/agents/collector/agent.py` |
| 预审智能体 | `src/agents/reviewer/agent.py` |
| 分析智能体 | `src/agents/analyzer/agent.py` |
| 评分引擎 | `src/agents/reviewer/scorer.py` |
| 数据模型 | `src/db/models.py` |
| CRUD操作 | `src/db/crud.py` |
| 配置管理 | `src/core/config.py` |
| 处理流水线 | `src/services/pipeline.py` |
| 前端API | `frontend/src/services/api.ts` |
| 类型定义 | `frontend/src/types/index.ts` |
| 学习中心页面 | `frontend/src/pages/LearningRecords.tsx` |
| 内容库页面 | `frontend/src/pages/Contents.tsx` |

---

## 环境变量 (.env)

```bash
# LLM 配置
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/metis.db

# 预审
PASSING_SCORE=60

# API 服务
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 启动命令

```bash
# 后端
venv\Scripts\activate
python -m src.api.main

# 前端
cd frontend
npm run dev

# Docker
docker-compose up -d
```

---

*最后更新: 2026-03-18*

**最近更新内容**:
- 添加后端搜索功能（内容库、学习中心）
- 重构设置页面（可视化LLM配置、移除冗余模块）
- 添加学习中心分页跳转功能
- 清理数据一致性修复相关代码
