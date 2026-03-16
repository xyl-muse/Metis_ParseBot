"""总结分析智能体提示词模板"""

SUMMARY_PROMPT = """你是一个专业的知识总结专家。请对以下内容进行深度总结。

标题: {title}
来源: {source}
分类: {category}
内容: {content}

请提供:
1. 核心总结（150字以内，抓住最重要的信息）
2. 关键要点（最多{max_key_points}个，每个要点简洁明了）
3. 学习建议（给学习者的具体建议）

请严格按照以下JSON格式返回，不要包含其他内容:
{{
    "summary": "核心总结内容",
    "key_points": ["要点1", "要点2", "要点3"],
    "learning_suggestions": "学习建议"
}}
"""

KNOWLEDGE_LINK_PROMPT = """你是一个知识关联专家。请分析以下内容与其他知识的关联。

标题: {title}
内容摘要: {summary}
关键要点: {key_points}

请识别:
1. 相关的先修知识（学习前需要了解的概念）
2. 相关的扩展知识（可以深入学习的内容）
3. 可能的易混淆概念（容易误解或混淆的地方）

请严格按照以下JSON格式返回，不要包含其他内容:
{{
    "knowledge_links": [
        {{
            "concept": "关联概念名称",
            "relation": "关系类型（先修/扩展/对比）",
            "note": "关联说明或辨析提醒"
        }}
    ],
    "confusion_notes": [
        {{
            "item": "易混淆内容",
            "distinction": "如何区分/辨析要点"
        }}
    ],
    "related_topics": ["相关主题1", "相关主题2"]
}}
"""

ANALYSIS_PROMPT = """请对以下内容进行完整的分析和总结。

标题: {title}
来源: {source}
分类: {category}
内容: {content}

请提供完整的分析结果，严格按照以下JSON格式返回:
{{
    "summary": "核心总结（150字以内）",
    "key_points": ["关键要点1", "关键要点2", "关键要点3"],
    "knowledge_links": [
        {{
            "concept": "关联概念",
            "relation": "关系类型",
            "note": "关联说明"
        }}
    ],
    "confusion_notes": [
        {{
            "item": "易混淆内容",
            "distinction": "区分要点"
        }}
    ],
    "learning_suggestions": "学习建议",
    "related_topics": ["相关主题"]
}}
"""

CROSS_DOMAIN_PROMPT = """你是一个跨领域知识分析专家。以下内容涉及AI和信息安全的交叉领域。

标题: {title}
内容: {content}

请特别关注:
1. AI技术如何应用于信息安全
2. 信息安全如何影响AI系统
3. 交叉领域的独特挑战和机遇

请按照标准JSON格式返回分析结果。
"""
