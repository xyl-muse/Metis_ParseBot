# Metis_ParseBot - 智能知识采集与分析系统

## 项目概述

Metis_ParseBot 是一个多智能体协作系统，专注于自动采集、筛选和总结人工智能、信息安全及其交叉领域的前沿知识，帮助用户高效掌握新知识。

### 核心功能
- **自动采集**: 从多个数据源采集学术论文和工程新闻
- **智能筛选**: AI驱动的价值评分机制，过滤低质量内容
- **深度分析**: 总结核心内容，关联相关知识，辨析易混淆点
- **持久存储**: 结构化存储学习记录，便于回顾

## 系统架构

### 三智能体架构

系统采用三智能体协作模式：

1. **采集智能体 (Collector Agent)**
   - 负责从多个数据源采集内容并进行初步分类
   - 数据源包括 arXiv 学术论文、HackerNews、Reddit 等
   - 分类标签：`academic_ai`、`academic_security`、`academic_cross`、`news_ai`、`news_security`、`news_cross`

2. **预审智能体 (Reviewer Agent)**
   - 评估内容价值，过滤低质量内容
   - 五维度评分系统（总分100）：
     - 新颖性 (0-25)
     - 实用性 (0-25)
     - 权威性 (0-20)
     - 时效性 (0-15)
     - 完整性 (0-15)
   - 及格线：60分

3. **分析智能体 (Analyzer Agent)**
   - 对通过预审的内容进行深度分析和总结
   - 生成内容总结、关键点提取、知识关联分析
   - 识别易混淆概念并提供辨析提醒

### 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | React 18 + TypeScript + TailwindCSS + Vite |
| **后端API** | FastAPI (Python 3.10+) |
| **智能体框架** | LangChain |
| **LLM接口** | OpenAI API (环境变量配置) |
| **数据库** | SQLite (开发) / PostgreSQL (生产) |
| **任务调度** | APScheduler |
| **容器化** | Docker + Docker Compose |

## 项目结构

```
Metis_ParseBot/
├── src/                    # 后端源码
│   ├── agents/             # 三智能体
│   │   ├── collector/      # 采集智能体
│   │   │   ├── agent.py    # 采集逻辑
│   │   │   ├── sources/    # 数据源适配器
│   │   │   │   ├── arxiv.py
│   │   │   │   ├── news.py
│   │   │   │   └── base.py
│   │   │   └── prompts.py  # 提示词模板
│   │   ├── reviewer/       # 预审智能体
│   │   │   ├── agent.py    # 预审逻辑
│   │   │   ├── scorer.py   # 评分引擎
│   │   │   └── prompts.py
│   │   └── analyzer/       # 分析智能体
│   │       ├── agent.py    # 分析逻辑
│   │       ├── summarizer.py # 总结生成
│   │       ├── knowledge.py # 知识关联
│   │       └── prompts.py
│   ├── core/               # 核心配置
│   │   ├── config.py       # 配置管理
│   │   ├── logging.py      # 日志配置
│   │   └── exceptions.py   # 异常定义
│   ├── api/                # API接口
│   │   ├── main.py         # FastAPI应用
│   │   ├── routes/
│   │   │   ├── collect.py
│   │   │   ├── review.py
│   │   │   └── analyze.py
│   │   └── schemas.py      # 数据模型
│   ├── db/                 # 数据库
│   │   ├── models.py       # ORM模型
│   │   ├── crud.py         # 数据操作
│   │   └── migrations/     # 数据库迁移
│   ├── services/           # 业务服务
│   │   ├── pipeline.py     # 处理流水线
│   │   └── scheduler.py    # 任务调度
│   └── utils/              # 工具函数
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   ├── hooks/          # 自定义Hooks
│   │   ├── services/       # API调用
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── tests/                  # 测试
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docker/                 # Docker配置
├── data/                   # 数据目录
├── Dockerfile              # 后端镜像
├── Dockerfile.frontend     # 前端镜像
├── docker-compose.yml      # 服务编排
├── requirements.txt        # Python依赖
├── pyproject.toml          # 项目配置
└── .env.example            # 环境变量模板
```

## 核心模块详解

### 1. 采集智能体 (CollectorAgent)

位于 `src/agents/collector/agent.py`，主要功能包括：

- 初始化多种数据源（arXiv、HackerNews、Reddit等）
- 执行采集任务，支持限制每源采集数量
- 内容去重检查
- 使用LLM进行内容分类
- 将采集内容存入数据库

### 2. 预审智能体 (ReviewerAgent)

位于 `src/agents/reviewer/agent.py`，主要功能包括：

- 使用评分引擎对内容进行五维度评分
- 判断内容是否通过预审（基于及格线）
- 生成拒绝原因说明
- 更新内容状态为"reviewed"或"rejected"

### 3. 分析智能体 (AnalyzerAgent)

位于 `src/agents/analyzer/agent.py`，主要功能包括：

- 生成内容总结和关键点提取
- 进行知识关联分析
- 识别易混淆概念
- 创建学习记录

### 4. API服务 (FastAPI)

位于 `src/api/main.py`，提供以下端点：

- 根路由和健康检查
- 内容管理（CRUD操作）
- 采集、预审、分析功能接口
- 系统设置和学习记录接口
- 完整流水线执行接口

## 配置管理

### 环境变量配置

位于 `src/core/config.py`，包含以下配置项：

- **应用配置**: app_name, app_version, debug, log_level
- **LLM API配置**: openai_api_key, openai_api_base, model_name, temperature
- **数据库配置**: database_url, database_echo
- **采集配置**: collect_interval_hours, max_items_per_run, arxiv_categories
- **预审配置**: passing_score, score_weights
- **API服务配置**: api_host, api_port, cors_origins

### 默认配置

```python
# LLM API 配置
openai_api_key: Optional[str] = None
openai_api_base: str = "https://api.openai.com/v1"
model_name: str = "gpt-4"

# 数据库配置
database_url: str = "sqlite+aiosqlite:///./data/metis.db"

# 采集配置
collect_interval_hours: int = 6
max_items_per_run: int = 50

# 预审配置
passing_score: int = 60
score_weights: dict[str, float] = {
    "novelty": 0.25,        # 新颖性
    "utility": 0.25,        # 实用性
    "authority": 0.20,      # 权威性
    "timeliness": 0.15,     # 时效性
    "completeness": 0.15,   # 完整性
}
```

## 前端界面

### 页面结构

- **Dashboard**: 系统概览和快捷操作
- **Contents**: 内容列表和筛选
- **ContentDetail**: 单个内容详情
- **LearningRecords**: 学习记录管理
- **Settings**: 系统设置

### 技术特点

- React 18 + TypeScript
- TailwindCSS 样式框架
- React Router DOM 路由管理
- Axios API 请求
- Recharts 数据可视化

## 部署与运行

### 本地开发

```bash
# 后端
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
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
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 启动所有服务
docker-compose up -d

# 访问
# 前端: http://localhost
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 运行测试

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## 数据库模型

系统包含以下主要模型：

1. **Content**: 采集内容模型
2. **Review**: 预审结果模型
3. **Analysis**: 分析结果模型
4. **LearningRecord**: 学习记录模型

## 开发规范

- **代码风格**: 遵循 PEP 8 (Python) 和 ESLint (TypeScript)
- **提交规范**: Conventional Commits
- **分支策略**: Git Flow
- **文档**: 所有模块需包含docstring

## 项目状态

根据工作日志显示，项目已经全部开发完成，包括：
- 基础架构搭建
- 三智能体核心开发
- 数据库与API开发
- 前端界面开发
- 集成测试与优化
- 部署与交付

## 代码统计

| 模块 | 文件数 | 代码行数(估算) |
|------|--------|----------------|
| 后端核心 | 38 | ~2,650 |
| 前端组件/页面 | 12 | ~2,000 |
| 前端配置 | 6 | ~300 |
| 测试代码 | 6 | ~600 |
| Docker配置 | 4 | ~100 |
| **总计** | **66** | **~5,650** |