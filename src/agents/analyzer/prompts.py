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

# 英文内容双语对照总结
SUMMARY_PROMPT_BILINGUAL = """You are a professional knowledge summarization expert. Please provide a deep summary of the following content in BILINGUAL format (English + Chinese).

Title: {title}
Source: {source}
Category: {category}
Content: {content}

Please provide:
1. Core summary (within 150 words, capture the most important information) - provide both English and Chinese versions
2. Key points (up to {max_key_points}, each point should be concise) - provide both English and Chinese versions
3. Learning suggestions (specific suggestions for learners) - provide both English and Chinese versions

IMPORTANT: For each field, first provide the English version, then provide the Chinese translation. Format:
- summary: "English summary. [中文翻译：中文总结]"
- key_points: ["English point 1. [中文：要点1]", "English point 2. [中文：要点2]", ...]
- learning_suggestions: "English suggestions. [中文翻译：中文建议]"

Please strictly return in the following JSON format, do not include other content:
{{
    "summary": "English summary here. [中文翻译：中文总结在这里]",
    "key_points": ["English point 1. [中文：要点1]", "English point 2. [中文：要点2]"],
    "learning_suggestions": "English suggestions. [中文翻译：中文建议]"
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

# 英文内容双语对照知识关联
KNOWLEDGE_LINK_PROMPT_BILINGUAL = """You are a knowledge association expert. Please analyze the connections between the following content and other knowledge in BILINGUAL format.

Title: {title}
Content Summary: {summary}
Key Points: {key_points}

Please identify:
1. Related prerequisite knowledge (concepts to understand before learning)
2. Related extended knowledge (content for deeper learning)
3. Potentially confusing concepts (easy to misunderstand or confuse)

IMPORTANT: Provide all content in bilingual format (English + Chinese):
- concept: "English concept [中文：概念]"
- relation: "English relation type [中文：关系类型]"
- note: "English note. [中文翻译：中文说明]"

Please strictly return in the following JSON format:
{{
    "knowledge_links": [
        {{
            "concept": "English concept [中文：概念]",
            "relation": "prerequisite/extension/comparison [中文：先修/扩展/对比]",
            "note": "English explanation. [中文翻译：中文说明]"
        }}
    ],
    "confusion_notes": [
        {{
            "item": "English item [中文：易混淆内容]",
            "distinction": "English distinction. [中文翻译：区分要点]"
        }}
    ],
    "related_topics": ["English topic 1 [中文：主题1]", "English topic 2 [中文：主题2]"]
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

# 英文内容双语对照完整分析
ANALYSIS_PROMPT_BILINGUAL = """Please provide a complete analysis and summary of the following content in BILINGUAL format.

Title: {title}
Source: {source}
Category: {category}
Content: {content}

IMPORTANT: Provide all content in bilingual format (English + Chinese). For each field:
- First write in English, then add Chinese translation in brackets
- Format: "English content. [中文翻译：中文内容]"

Please provide complete analysis results in the following JSON format:
{{
    "summary": "English summary. [中文翻译：中文总结]",
    "key_points": ["English point 1. [中文：要点1]", "English point 2. [中文：要点2]"],
    "knowledge_links": [
        {{
            "concept": "English concept [中文：概念]",
            "relation": "relation type [中文：关系类型]",
            "note": "English note. [中文翻译：中文说明]"
        }}
    ],
    "confusion_notes": [
        {{
            "item": "English item [中文：易混淆内容]",
            "distinction": "English distinction. [中文翻译：区分要点]"
        }}
    ],
    "learning_suggestions": "English suggestions. [中文翻译：中文建议]",
    "related_topics": ["English topic 1 [中文：主题1]", "English topic 2 [中文：主题2]"]
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

# 英文内容双语对照跨领域分析
CROSS_DOMAIN_PROMPT_BILINGUAL = """You are a cross-domain knowledge analysis expert. The following content involves the intersection of AI and information security.

Title: {title}
Content: {content}

Please pay special attention to:
1. How AI technology is applied to information security
2. How information security affects AI systems
3. Unique challenges and opportunities in the cross-domain field

IMPORTANT: Provide all content in bilingual format (English + Chinese).
Format: "English content. [中文翻译：中文内容]"

Please return analysis results in standard JSON format.
"""


def is_english_content(text: str) -> bool:
    """检测内容是否主要为英文"""
    if not text:
        return False
    
    # 统计英文字符比例
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    total_alpha = sum(1 for c in text if c.isalpha())
    
    if total_alpha == 0:
        return False
    
    # 如果英文字符占比超过 70%，认为是英文内容
    return english_chars / total_alpha > 0.7


def get_summary_prompt(title: str, source: str, category: str, content: str, max_key_points: int = 10) -> str:
    """根据内容语言选择合适的总结 prompt"""
    full_text = f"{title} {content}"
    
    if is_english_content(full_text):
        return SUMMARY_PROMPT_BILINGUAL.format(
            title=title,
            source=source,
            category=category,
            content=content,
            max_key_points=max_key_points,
        )
    else:
        return SUMMARY_PROMPT.format(
            title=title,
            source=source,
            category=category,
            content=content,
            max_key_points=max_key_points,
        )


def get_knowledge_link_prompt(title: str, summary: str, key_points: list) -> str:
    """根据内容语言选择合适的知识关联 prompt"""
    full_text = f"{title} {summary} {' '.join(key_points)}"
    
    if is_english_content(full_text):
        return KNOWLEDGE_LINK_PROMPT_BILINGUAL.format(
            title=title,
            summary=summary,
            key_points=key_points,
        )
    else:
        return KNOWLEDGE_LINK_PROMPT.format(
            title=title,
            summary=summary,
            key_points=key_points,
        )


def get_analysis_prompt(title: str, source: str, category: str, content: str) -> str:
    """根据内容语言选择合适的分析 prompt"""
    full_text = f"{title} {content}"
    
    if is_english_content(full_text):
        return ANALYSIS_PROMPT_BILINGUAL.format(
            title=title,
            source=source,
            category=category,
            content=content,
        )
    else:
        return ANALYSIS_PROMPT.format(
            title=title,
            source=source,
            category=category,
            content=content,
        )
