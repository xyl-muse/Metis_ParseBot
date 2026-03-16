"""采集智能体提示词模板"""

CLASSIFICATION_PROMPT = """你是一个专业的内容分类助手。请分析以下内容，判断它属于哪个类别。

内容标题: {title}
内容摘要: {summary}
来源: {source}

可选类别:
1. academic_ai - 人工智能学术论文
2. academic_security - 信息安全学术论文  
3. academic_cross - AI与安全交叉领域学术论文
4. news_ai - AI工程新闻/技术动态
5. news_security - 信息安全新闻/技术动态
6. news_cross - AI与安全交叉领域新闻

请严格按照以下JSON格式返回结果，不要包含其他内容:
{{
    "category": "选定的类别",
    "confidence": 0.0到1.0之间的置信度,
    "reason": "简要说明分类理由"
}}
"""

EXTRACTION_PROMPT = """请从以下内容中提取关键信息。

内容:
{content}

请提取并严格按照以下JSON格式返回:
{{
    "main_topics": ["主要话题1", "主要话题2"],
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "relevance_to_ai": 0.0到1.0之间的AI相关度,
    "relevance_to_security": 0.0到1.0之间的安全相关度
}}
"""

SUMMARY_GENERATION_PROMPT = """请为以下内容生成简洁的摘要（100字以内）。

标题: {title}
内容: {content}

摘要:
"""
