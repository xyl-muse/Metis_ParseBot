# Metis_ParseBot 全局工作规划

## 项目里程碑

```
Phase 1: 基础架构搭建
    │
    ▼
Phase 2: 三智能体核心开发
    │
    ▼
Phase 3: 数据库与API开发
    │
    ▼
Phase 4: 前端界面开发
    │
    ▼
Phase 5: 集成测试与优化
    │
    ▼
Phase 6: 部署与交付
    │
    ▼
Phase 7: 功能优化与改进
```

---

## Phase 1: 基础架构搭建 [已完成]

### 1.1 项目初始化
- [x] 创建项目目录结构
- [x] 初始化 Python 项目 (pyproject.toml, requirements.txt)
- [x] 配置开发环境 (虚拟环境, 代码格式化工具)
- [x] 设置 Git 仓库及 .gitignore

### 1.2 核心配置模块
- [x] 实现 `src/core/config.py` - 配置管理 (支持环境变量)
- [x] 实现 `src/core/logging.py` - 日志系统
- [x] 实现 `src/core/exceptions.py` - 自定义异常
- [x] 创建 `.env.example` 环境变量模板

### 1.3 数据库基础
- [x] 设计数据库模型 (`src/db/models.py`)
- [x] 实现数据库连接与会话管理
- [x] 创建基础 CRUD 操作

**数据库模型设计**:

```python
# Content - 采集内容
class Content:
    id: UUID
    title: str
    source: str              # 数据来源
    source_url: str          # 原始链接
    category: str            # 分类标签
    raw_content: str         # 原始内容
    collected_at: datetime   # 采集时间
    status: str              # pending/reviewed/analyzed

# Review - 预审记录
class Review:
    id: UUID
    content_id: UUID
    novelty_score: int       # 新颖性
    utility_score: int       # 实用性
    authority_score: int     # 权威性
    timeliness_score: int    # 时效性
    completeness_score: int  # 完整性
    total_score: int         # 总分
    passed: bool             # 是否通过
    reviewed_at: datetime

# Analysis - 分析结果
class Analysis:
    id: UUID
    content_id: UUID
    summary: str             # 核心总结
    key_points: JSON         # 要点列表
    knowledge_links: JSON    # 知识关联
    confusion_notes: JSON    # 易混淆辨析
    learning_suggestions: str
    analyzed_at: datetime
```

---

## Phase 2: 三智能体核心开发 [已完成]

### 2.1 智能体基类
- [x] 实现 `src/agents/base.py` - 智能体基类
- [x] 定义智能体接口规范
- [x] 实现LLM调用封装

### 2.2 采集智能体 (Collector Agent)

#### 2.2.1 数据源适配器
- [x] 实现适配器基类 `sources/base.py`
- [x] 实现 arXiv 适配器 `sources/arxiv.py`
  - 论文标题、摘要、作者、链接
  - 分类: cs.AI, cs.CR, cs.LG 等
- [x] 实现新闻源适配器 `sources/news.py`
  - Hacker News API
  - Reddit API (r/MachineLearning, r/netsec)
  - 安全资讯源

#### 2.2.2 采集逻辑
- [x] 实现内容分类器 (判断是AI/安全/交叉领域)
- [x] 实现去重机制 (基于URL或标题相似度)
- [x] 实现采集调度器 (定时任务)

#### 2.2.3 提示词工程
- [x] 设计分类提示词模板
- [x] 测试与优化分类准确性

### 2.3 预审智能体 (Reviewer Agent)

#### 2.3.1 评分引擎
- [x] 实现 `scorer.py` - 多维度评分逻辑
- [x] 设计评分提示词模板
- [x] 实现评分结果解析

#### 2.3.2 过滤与排序
- [x] 实现及格线过滤机制
- [x] 实现优先级队列排序
- [x] 实现批量预审功能

#### 2.3.3 提示词工程
- [x] 设计价值评估提示词
- [x] 测试评分一致性与准确性

### 2.4 总结分析智能体 (Analyzer Agent)

#### 2.4.1 总结生成
- [x] 实现 `summarizer.py` - 内容总结
- [x] 设计总结输出格式
- [x] 实现关键点提取

#### 2.4.2 知识关联
- [x] 实现 `knowledge.py` - 知识关联分析
- [x] 设计知识关联提示词
- [x] 实现易混淆内容检测

#### 2.4.3 提示词工程
- [x] 设计分析总结提示词
- [x] 设计知识关联提示词
- [x] 测试输出质量

---

## Phase 3: 数据库与API开发 [已完成]

### 3.1 数据库完善
- [x] 实现完整 CRUD 操作 `src/db/crud.py`
- [x] 添加数据查询接口
- [x] 实现数据库迁移脚本

### 3.2 API接口开发

#### 3.2.1 FastAPI 应用
- [x] 实现 `src/api/main.py` - 应用入口
- [x] 配置 CORS 和中间件
- [x] 实现请求/响应模型 `schemas.py`

#### 3.2.2 API路由
- [x] `/api/collect` - 手动触发采集
- [x] `/api/contents` - 获取内容列表
- [x] `/api/contents/{id}` - 获取单个内容
- [x] `/api/reviews` - 获取预审结果
- [x] `/api/analyses` - 获取分析结果
- [x] `/api/status` - 获取系统状态

### 3.3 处理流水线
- [x] 实现 `src/services/pipeline.py`
- [x] 串联三个智能体的处理流程
- [x] 实现错误处理与重试机制

---

## Phase 4: 前端界面开发 [已完成]

### 4.1 项目初始化
- [x] 创建 React + TypeScript 项目
- [x] 配置 TailwindCSS
- [x] 配置路由 (React Router)

### 4.2 核心页面

#### 4.2.1 仪表盘页面
- [x] 系统状态概览
- [x] 最近采集内容统计
- [x] 待处理任务数量

#### 4.2.2 内容列表页面
- [x] 展示采集内容列表
- [x] 分类筛选功能
- [x] 搜索功能

#### 4.2.3 内容详情页面
- [x] 展示原始内容
- [x] 展示预审评分
- [x] 展示分析结果
- [x] 知识关联可视化

#### 4.2.4 设置页面
- [x] API密钥配置
- [x] 采集源管理
- [x] 评分阈值设置

### 4.3 组件开发
- [x] ContentCard - 内容卡片组件
- [x] ScoreDisplay - 评分展示组件
- [x] KnowledgeGraph - 知识关联图组件
- [x] FilterBar - 筛选栏组件

---

## Phase 5: 集成测试与优化 [已完成]

### 5.1 单元测试
- [x] 智能体逻辑测试
- [x] 评分引擎测试
- [x] API接口测试

### 5.2 集成测试
- [x] 端到端流程测试
- [x] 数据库操作测试
- [x] 前后端联调测试

### 5.3 性能优化
- [x] API响应时间优化
- [x] 数据库查询优化
- [x] 前端加载优化

### 5.4 提示词优化
- [x] 根据实际效果优化各智能体提示词
- [x] 提高分类准确性
- [x] 提高评分一致性

---

## Phase 6: 部署与交付 [已完成]

### 6.1 部署准备
- [x] 编写部署文档
- [x] 创建 Docker 镜像
- [x] 配置生产环境变量

### 6.2 最终验证
- [x] 功能完整性检查
- [x] 安全性检查 (API密钥保护)
- [x] 文档完整性检查

---

## Phase 7: 功能优化与改进 [已完成]

### 7.1 前端界面优化
- [x] 修复前端仪表盘统计数据显示为0的问题
- [x] 修复一键运行流水线的错误
- [x] 在内容库中按栏目划分：已采纳(待分析)、已分析、已拒绝
- [x] 将内容库中的知识显示改为列表形式，简化字段展示
- [x] 添加列表/网格视图切换功能
- [x] 创建ContentListItem组件以支持列表视图
- [x] 实现按内容状态的标签页导航

### 7.2 后端功能增强
- [x] 为采集智能体添加时效限制：仅采集近三天的热点内容
- [x] 修改tag格式为'主题+分类'格式，主题为AI/安全/AI&安全，分类为学术/工程
- [x] 增加内容时效性检查功能
- [x] 添加新的内容标签生成机制
- [x] 优化API响应处理逻辑

---

## 未来发展规划

### Phase 8: 高级功能扩展
- [ ] 知识图谱可视化
- [ ] 高级搜索和过滤功能
- [ ] 个性化推荐系统
- [ ] 多语言支持
- [ ] 用户协作功能

### Phase 9: 性能和扩展性优化
- [ ] 引入缓存机制
- [ ] 数据库读写分离
- [ ] 微服务架构优化
- [ ] 实时通知系统

### Phase 10: 移动端适配
- [ ] 响应式设计优化
- [ ] 移动端专用界面
- [ ] PWA功能实现

---

## 开发优先级

```
高优先级 (P0):
├── Phase 1: 基础架构
├── Phase 2.1-2.2: 智能体基类 + 采集智能体
└── Phase 2.3: 预审智能体

中优先级 (P1):
├── Phase 2.4: 总结分析智能体
├── Phase 3: 数据库与API
└── Phase 5.1-5.2: 测试

低优先级 (P2):
├── Phase 4: 前端界面
├── Phase 5.3-5.4: 优化
└── Phase 6: 部署
```

---

## 技术风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| LLM API 调用成本高 | 预算超支 | 实现缓存机制，优化提示词长度 |
| 采集频率限制 | 数据不足 | 多源采集，合理设置间隔 |
| 评分主观性强 | 质量不稳定 | 多轮评分取平均，持续优化提示词 |
| 知识关联准确性低 | 用户体验差 | 引入知识图谱，迭代优化 |

---

## 下一步行动

1. **持续优化**: 根据用户反馈持续改进现有功能
2. **功能扩展**: 实现高级功能如知识图谱可视化
3. **性能调优**: 优化系统性能和用户体验

---

*文档版本: v2.0*
*创建日期: 2026-03-16*
