# """
# 客户分类模块 (Module 2)
# 基于对话历史自动分类客户为：优质/普通/低价值
# """
# from services.llm_service import get_llm_service
# from models import Customer, CustomerCategory
# import json
# import logging

# logger = logging.getLogger(__name__)

# class CustomerClassifier:
#     """客户分类器"""
    
#     def __init__(self):
#         self.llm = get_llm_service()
    
#     def classify(self, conversation_history: list) -> dict:
#         """
#         分类客户
        
#         Args:
#             conversation_history: 对话历史 [{"sender": "customer", "content": "..."}]
            
#         Returns:
#             {
#                 "category": "high_value/normal/low_value",
#                 "priority_score": 1-5,
#                 "reason": "分类理由"
#             }
#         """
#         # 构建提示词
#         prompt = self._build_classification_prompt(conversation_history)
        
#         # 调用LLM
#         response = self.llm.generate(prompt, temperature=0.3)
        
#         # 解析结果
#         try:
#             result = self._parse_classification_result(response)
#             logger.info(f"客户分类完成: {result['category']} (置信度: {result['priority_score']}/5)")
#             return result
#         except Exception as e:
#             logger.error(f"分类结果解析失败: {e}, 原始响应: {response}")
#             # 返回默认分类
#             return {
#                 "category": CustomerCategory.NORMAL,
#                 "priority_score": 3,
#                 "reason": "分类失败，使用默认分类"
#             }
    
#     def _build_classification_prompt(self, conversation_history: list) -> str:
#         """构建分类提示词"""
        
#         # 格式化对话历史
#         conversation_text = "\n".join([
#             f"{'客户' if msg['sender'] == 'customer' else 'AI'}: {msg['content']}"
#             for msg in conversation_history[-10:]  # 最近10条消息
#         ])
        
#         prompt = f"""你是一个专业的B2B销售客户分类专家，专注于大疆无人机销售领域。

# 请基于以下对话记录，判断客户价值等级：

# 对话记录：
# {conversation_text}

# 分类标准：

# 1. **优质客户 (high_value)**：
#    - 明确提及大额采购需求（>5台或总价>50万元）
#    - 询问技术细节深入（说明有真实项目需求）
#    - 决策快（3轮对话内就询问报价、交期、合同）
#    - 提及具体应用场景（电力巡检、测绘、应急救援等）
   
# 2. **普通客户 (normal)**：
#    - 有购买意向但犹豫不决
#    - 需求不明确或采购量较小（1-5台）
#    - 需要多轮沟通才能了解需求
#    - 价格敏感，反复比价
   
# 3. **低价值客户 (low_value)**：
#    - 只咨询价格，不关心技术细节
#    - 只问试飞、免费体验，从不提购买
#    - 提问肤浅（如"最便宜的多少钱"）
#    - 行为异常（可能是竞品套信息）

# 请输出JSON格式：
# ```json
# {{
#     "category": "high_value/normal/low_value",
#     "priority_score": 1到5的整数,
#     "reason": "用1-2句话说明分类理由，必须引用对话中的具体证据"
# }}
# ```

# 仅输出JSON，不要其他内容。"""
        
#         return prompt
    
#     def _parse_classification_result(self, response: str) -> dict:
#         """解析分类结果"""
#         # 尝试提取JSON
#         import re
#         json_match = re.search(r'\{[^{}]*"category"[^{}]*\}', response, re.DOTALL)
        
#         if json_match:
#             result = json.loads(json_match.group())
            
#             # 验证并规范化
#             category = result.get('category', 'normal')
#             if category not in ['high_value', 'normal', 'low_value']:
#                 category = 'normal'
            
#             priority_score = int(result.get('priority_score', 3))
#             if not (1 <= priority_score <= 5):
#                 priority_score = 3
            
#             return {
#                 'category': CustomerCategory(category),
#                 'priority_score': priority_score,
#                 'reason': result.get('reason', '自动分类')
#             }
#         else:
#             raise ValueError("无法解析JSON")

# # 全局单例
# _classifier = None

# def get_classifier() -> CustomerClassifier:
#     """获取分类器实例（单例）"""
#     global _classifier
#     if _classifier is None:
#         _classifier = CustomerClassifier()
#     return _classifier
