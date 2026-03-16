# Metis_ParseBot - 智能知识采集与分析系统

## 项目概述

Metis_ParseBot 是一个多智能体协作系统，专注于自动采集、筛选和总结人工智能、信息安全及其交叉领域的前沿知识，帮助用户高效掌握新知识。

## 核心功能

- **自动采集**: 从多个数据源采集学术论文和工程新闻
- **智能筛选**: AI驱动的价值评分机制，过滤低质量内容
- **深度分析**: 总结核心内容，关联相关知识，辨析易混淆点
- **持久存储**: 结构化存储学习记录，便于回顾

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Metis_ParseBot                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  采集智能体   │───▶│  预审智能体   │───▶│ 总结分析智能体│          │
│  │  Collector   │    │   Reviewer   │    │   Analyzer   │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                    │                  │
│         ▼                   ▼                    ▼                  │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐            │
│  │  数据源     │      │  评分引擎   │      │  知识图谱   │            │
│  │ - arXiv    │      │  排序队列   │      │  关联分析   │            │
│  │ - News     │      │  过滤器     │      │  输出生成   │            │
│  └────────────┘      └────────────┘      └────────────┘            │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                         基础设施层                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │  数据库     │  │  LLM API   │  │   API层    │  │   前端     │    │
│  │ PostgreSQL │  │ OpenAI等   │  │  FastAPI   │  │   React    │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 三智能体协作流程

```
采集智能体 (Collector)
    │
    │ 采集内容 + 分类标签
    ▼
预审智能体 (Reviewer)
    │
    │ 价值评分 → 过滤 → 排序
    ▼
总结分析智能体 (Analyzer)
    │
    │ 总结 + 知识关联 + 辨析提醒
    ▼
    数据库存储
```

---

## 技术选型

| 层级 | 技术栈 | 说明 |
|------|--------|------|
| **前端** | React 18 + TypeScript + TailwindCSS | 现代化响应式UI |
| **后端API** | FastAPI (Python) | 高性能异步API框架 |
| **智能体框架** | LangChain / LangGraph | 多智能体编排与管理 |
| **LLM接口** | OpenAI API / Claude API | 通过环境变量配置 |
| **数据库** | SQLite (开发) / PostgreSQL (生产) | 结构化数据存储 |
| **任务调度** | APScheduler | 定时采集任务 |
| **向量存储** | ChromaDB / FAISS | 语义搜索与知识关联 |

---

## 项目结构

```
Metis_ParseBot/
├── src/
│   ├── agents/                 # 智能体模块
│   │   ├── __init__.py
│   │   ├── base.py            # 智能体基类
│   │   ├── collector/         # 采集智能体
│   │   │   ├── __init__.py
│   │   │   ├── agent.py       # 采集逻辑
│   │   │   ├── sources/       # 数据源适配器
│   │   │   │   ├── arxiv.py
│   │   │   │   ├── news.py
│   │   │   │   └── base.py
│   │   │   └── prompts.py     # 提示词模板
│   │   ├── reviewer/          # 预审智能体
│   │   │   ├── __init__.py
│   │   │   ├── agent.py       # 预审逻辑
│   │   │   ├── scorer.py      # 评分引擎
│   │   │   └── prompts.py
│   │   └── analyzer/          # 总结分析智能体
│   │       ├── __init__.py
│   │       ├── agent.py       # 分析逻辑
│   │       ├── summarizer.py  # 总结生成
│   │       ├── knowledge.py   # 知识关联
│   │       └── prompts.py
│   ├── core/                  # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py          # 配置管理
│   │   ├── logging.py         # 日志配置
│   │   └── exceptions.py      # 异常定义
│   ├── api/                   # API接口
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI应用
│   │   ├── routes/
│   │   │   ├── collect.py
│   │   │   ├── review.py
│   │   │   └── analyze.py
│   │   └── schemas.py         # 数据模型
│   ├── db/                    # 数据库
│   │   ├── __init__.py
│   │   ├── models.py          # ORM模型
│   │   ├── crud.py            # 数据操作
│   │   └── migrations/        # 数据库迁移
│   ├── services/              # 业务服务
│   │   ├── __init__.py
│   │   ├── pipeline.py        # 处理流水线
│   │   └── scheduler.py       # 任务调度
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── frontend/                  # 前端项目
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── pages/             # 页面
│   │   ├── hooks/             # 自定义Hooks
│   │   ├── services/          # API调用
│   │   └── utils/             # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── tests/                     # 测试
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/                      # 文档
│   └── api/
├── .env.example               # 环境变量模板
├── requirements.txt           # Python依赖
├── pyproject.toml             # 项目配置
└── README.md
```

---

## 智能体详细设计

### 1. 采集智能体 (Collector Agent)

**职责**: 从多个数据源采集内容并进行初步分类

**数据源**:
- 学术论文: arXiv, Semantic Scholar, Google Scholar
- 工程新闻: Hacker News, Reddit r/MachineLearning, 安全资讯站

**分类标签**:
- `academic_ai` - AI学术论文
- `academic_security` - 信息安全学术论文
- `academic_cross` - 交叉领域学术论文
- `news_ai` - AI工程新闻
- `news_security` - 信息安全新闻
- `news_cross` - 交叉领域新闻

### 2. 预审智能体 (Reviewer Agent)

**职责**: 评估内容价值，过滤低质量内容

**评分维度** (总分100):
- 新颖性 (0-25): 内容的创新程度
- 实用性 (0-25): 对学习者的实际价值
- 权威性 (0-20): 来源可靠性
- 时效性 (0-15): 内容的时效价值
- 完整性 (0-15): 信息完整程度

**及格线**: 60分

### 3. 总结分析智能体 (Analyzer Agent)

**职责**: 深度分析并输出学习内容

**输出结构**:
```json
{
  "title": "内容标题",
  "summary": "核心总结",
  "key_points": ["要点1", "要点2", "..."],
  "knowledge_links": [
    {
      "concept": "关联概念",
      "relation": "关系说明",
      "note": "辨析提醒"
    }
  ],
  "confusion_notes": [
    {
      "item": "易混淆内容",
      "distinction": "区分要点"
    }
  ],
  "learning_suggestions": "学习建议"
}
```

---

## 环境配置

创建 `.env` 文件:

```env
# LLM API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4

# 数据库配置
DATABASE_URL=sqlite:///./metis.db

# 采集配置
COLLECT_INTERVAL_HOURS=6
MAX_ITEMS_PER_RUN=50

# 评分配置
PASSING_SCORE=60
```

---

## 快速开始

```bash
# 克隆项目
git clone <repository_url>
cd Metis_ParseBot

# 安装后端依赖
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入API密钥

# 初始化数据库
python -m src.db.migrations

# 启动后端服务
uvicorn src.api.main:app --reload

# 安装前端依赖并启动
cd frontend
npm install
npm run dev
```

---

## 开发规范

- **代码风格**: 遵循 PEP 8 (Python) 和 ESLint (TypeScript)
- **提交规范**: Conventional Commits
- **分支策略**: Git Flow
- **文档**: 所有模块需包含docstring

---

## License

MIT License
