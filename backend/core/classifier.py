# """
# Customer Classification Module (Module 2)
# Automatically classifies customers based on conversation history into: high_value/normal/low_value
# """
# from services.llm_service import get_llm_service
# from models import Customer, CustomerCategory
# import json
# import logging

# logger = logging.getLogger(__name__)

# class CustomerClassifier:
#     """Customer Classifier"""
    
#     def __init__(self):
#         self.llm = get_llm_service()
    
#     def classify(self, conversation_history: list) -> dict:
#         """
#         Classify Customer
        
#         Args:
#             conversation_history: list of messages [{"sender": "customer", "content": "..."}]
            
#         Returns:
#             {
#                 "category": "high_value/normal/low_value",
#                 "priority_score": 1-5,
#                 "reason": "Classification reason"
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
#                 "category": CustomerCategory.NORMAL,
#                 "priority_score": 3,
#                 "reason": "Classification failed, using default"
#             }
    
#     def _build_classification_prompt(self, conversation_history: list) -> str:
#         """Build classification prompt"""
        
#         # Format conversation history
#         conversation_text = "\n".join([
#             f"{'Customer' if msg['sender'] == 'customer' else 'AI'}: {msg['content']}"
#             for msg in conversation_history[-10:]  # Last 10 messages
#         ])
        
#         prompt = f"""You are a professional B2B sales customer classification expert, specializing in DJI drone sales.

# Please determine the customer value level based on the following conversation history:

# Conversation History:
# {conversation_text}

# Classification Criteria:

# 1. **High Value (high_value)**:
#    - Clearly mentions large-scale purchase needs (>5 units or total price > 500,000 RMB)
#    - In-depth technical questions (indicating real project requirements)
#    - Fast decision-making (asking for quotes, lead times, contracts within 3 rounds)
#    - Mentions specific application scenarios (power inspection, mapping, emergency rescue, etc.)
   
# 2. **Normal (normal)**:
#    - Has purchase intent but is hesitant
#    - Requirements are not clear or small purchase volume (1-5 units)
#    - Requires multiple rounds of communication to understand needs
#    - Price-sensitive, repeated price comparisons
   
# 3. **Low Value (low_value)**:
#    - Only consults on price, doesn't care about technical details
#    - Only asks about test flights, free trials, never mentions purchasing
#    - Shallow questions (e.g., "What is the cheapest one?")
#    - Abnormal behavior (could be competitors fishing for info)

# Please output in JSON format:
# ```json
# {{
#     "category": "high_value/normal/low_value",
#     "priority_score": Integer from 1 to 5,
#     "reason": "Explain the classification reason in 1-2 sentences, must cite specific evidence from the conversation"
# }}
# ```

# Output ONLY JSON, no other content."""
        
#         return prompt
    
#     def _parse_classification_result(self, response: str) -> dict:
#         """Parse classification result"""
#         # 尝试提取JSON
#         # Attempt to extract JSON
#         import re
#         json_match = re.search(r'\{[^{}]*"category"[^{}]*\}', response, re.DOTALL)
        
#         if json_match:
#             result = json.loads(json_match.group())
            
#             # Validate and normalize
#             category = result.get('category', 'normal')
#             if category not in ['high_value', 'normal', 'low_value']:
#                 category = 'normal'
            
#             priority_score = int(result.get('priority_score', 3))
#             if not (1 <= priority_score <= 5):
#                 priority_score = 3
            
#             return {
#                 'category': CustomerCategory(category),
#                 'priority_score': priority_score,
#                 'reason': result.get('reason', 'Automatic Classification')
#             }
#         else:
#             raise ValueError("Could not parse JSON")

# # Global singleton
# _classifier = None

# def get_classifier() -> CustomerClassifier:
#     """Get classifier instance (singleton)"""
#     global _classifier
#     if _classifier is None:
#         _classifier = CustomerClassifier()
#     return _classifier
