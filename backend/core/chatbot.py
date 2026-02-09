# """
# Intelligent Dialogue Module (Module 3)
# Intelligent customer service robot based on enhanced RAG
# Supports metadata filtering, hybrid search, reranking
# """
# from services.llm_service import get_llm_service
# from services.knowledge_base import get_knowledge_base
# from services.enhanced_knowledge_base import get_enhanced_knowledge_base
# from typing import Dict, List
# import logging
# import json

# logger = logging.getLogger(__name__)

# class DJIChatbot:
#     """DJI Product Intelligent Customer Service Robot (Enhanced Version)"""
    
#     def __init__(self, use_enhanced_rag: bool = True):
#         self.llm = get_llm_service()
#         # Use enhanced RAG system
#         if use_enhanced_rag:
#             self.kb = get_enhanced_knowledge_base()
#             logger.info("Using enhanced RAG system (metadata filtering + hybrid search + reranking)")
#         else:
#             self.kb = get_knowledge_base()
#             logger.info("Using basic RAG system")
#         self.conversation_memory = {}  # Simple in-memory storage (production should use a database)
#         self.use_enhanced = use_enhanced_rag
    
#     def chat(self, customer_id: int, message: str, language: str = 'en-us') -> Dict:
#         """
#         Process customer message
        
#         Args:
#             customer_id: Customer ID
#             message: Message content
#             language: Language
            
#         Returns:
#             {
#                 "answer": "AI response",
#                 "confidence": 0.0-1.0,
#                 "should_handoff": bool,
#                 "retrieved_docs": [...],
#                 "product_tag": "M30/M400/Dock3"
#             }
#         """
#         # 1. Detect product type
#         product_tag = self._detect_product(message)
#         logger.info(f"Detected product: {product_tag}")
        
#         # 2. RAG retrieval (using enhanced features)
#         if self.use_enhanced:
#             retrieved_docs = self.kb.search(
#                 message, 
#                 product_filter=product_tag,
#                 top_k=5,
#                 use_hybrid=True,  # Hybrid Search (BM25 + Vector)
#                 use_rerank=True,  # Reranking
#                 similarity_threshold=0.3
#             )
#         else:
#             retrieved_docs = self.kb.search(message, product_filter=product_tag, top_k=5)
        
#         # 3. Build context
#         context = self._build_context(retrieved_docs)
        
#         # 4. Get conversation history
#         history = self._get_conversation_history(customer_id)
        
#         # 5. Generate response (using moderate creativity)
#         prompt = self._build_chat_prompt(message, context, history, language)
#         answer = self.llm.generate(prompt, temperature=0.5, max_tokens=300)  # Reducing creativity appropriately
        
#         # 6. Calculate confidence
#         confidence = self._calculate_confidence(retrieved_docs, answer)
        
#         # 7. Determine whether to hand off to human agent
#         should_handoff = self._should_handoff(message, confidence)
        
#         # 8. Save conversation history
#         self._save_to_memory(customer_id, message, answer)
        
#         return {
#             "answer": answer,
#             "confidence": confidence,
#             "should_handoff": should_handoff,
#             "retrieved_docs": [doc.page_content[:200] for doc in retrieved_docs],
#             "product_tag": product_tag
#         }
    
#     def _detect_product(self, message: str) -> str:
#         """Detect products mentioned in the message"""
#         message_lower = message.lower()
        
#         # Product keyword mapping
#         if any(kw in message_lower for kw in ['m30', 'matrice 30', 'matrice30']):
#             return 'M30'
#         elif any(kw in message_lower for kw in ['m400', 'matrice 400', 'matrice400']):
#             return 'M400'
#         elif any(kw in message_lower for kw in ['dock 3', 'dock3', 'm4d', 'airport']):
#             return 'Dock3'
#         elif any(kw in message_lower for kw in ['rtk', 'd-rtk']):
#             return 'RTK'
#         else:
#             return None  # Product not clearly specified
    
#     def _build_context(self, docs: List) -> str:
#         """Build retrieval context"""
#         if not docs:
#             return "No relevant documents found"
        
#         context_parts = []
#         for i, doc in enumerate(docs, 1):
#             metadata = doc.metadata
#             product = metadata.get('product_tag', 'Unknown Product')
#             doc_type = metadata.get('doc_type', 'Document')
#             content = doc.page_content[:500]  # Limit length
            
#             context_parts.append(f"[{product} - {doc_type}]\n{content}")
        
#         return "\n\n---\n\n".join(context_parts)
    
#     def _build_chat_prompt(self, message: str, context: str, history: List, language: str) -> str:
#         """Build chat prompt"""
        
#         # Format historical dialogue
#         history_text = "\n".join([
#             f"{'Customer' if h['role'] == 'user' else 'AI'}: {h['content']}"
#             for h in history[-3:]  # Last 3 rounds of conversation
#         ]) if history else "(This is the first conversation)"
        
#         prompt = f"""# Role Definition
# You are a professional B2B sales consultant for DJI drones, specializing in the sales of the Matrice series industrial-grade drones.

# # Core Responsibilities
# 1. Accurately answer technical questions based on product manuals
# 2. Identify customer needs and recommend appropriate products
# 3. Guide customers towards deeper communication at the right time
# 4. Maintain a professional, friendly, and problem-solving oriented approach

# # Knowledge Base Retrieval Results
# {context}

# # Conversation History
# {history_text}

# # Latest Customer Question
# {message}

# # Response Guidelines

# ## Response Strategy
# - **Direct Answer**: Don't repeat the question, go straight to the point
# - **Cite Sources**: Technical parameters must cite sources (e.g., "According to M30 User Manual")
# - **Requirement Discovery**: If the customer's question is vague, clarify needs by asking questions
# - **Value Communication**: Don't just list parameters, explain the value to the customer

# ## Response Format
# - Tone: Professional but not stiff, warm but not pushy
# - Length: 50-100 words (important information can be longer)
# - Language: {'Chinese' if language == 'zh-cn' else 'English'}
# - Structure: Answer the core question first, then supplement with relevant information

# ## Special Handling
# - If retrieval results are empty: Honestly inform and suggest contacting an expert
# - If regarding price/business: Provide reference and suggest transferring to human agent for quotes
# - If multi-product comparison: Ask for use scenarios first, then recommend

# Now please reply to the customer:"""
        
#         return prompt
    
#     def _calculate_confidence(self, docs: List, answer: str) -> float:
#         """Calculate confidence (simplified version)"""
#         if not docs:
#             return 0.5  # No documents retrieved
#         elif len(docs) >= 2:
#             return 0.85  # Multiple relevant documents retrieved
#         else:
#             return 0.7  # Only 1 document retrieved
    
#     def _should_handoff(self, message: str, confidence: float) -> bool:
#         """Determine whether to hand off to human agent"""
#         # Handoff keywords
#         handoff_keywords = ['handoff', 'human agent', 'contact sales', 'human', 'agent']
#         if any(kw in message.lower() for kw in handoff_keywords):
#             return True
        
#         # Low confidence
#         if confidence < 0.7:
#             return True
        
#         # Strong purchase intention (asking about price, contracts, payment, etc.)
#         buy_keywords = ['price', 'quote', 'how much', 'contract', 'payment', 'buy', 'price', 'buy']
#         if any(kw in message.lower() for kw in buy_keywords):
#             return True
        
#         return False
    
#     def _get_conversation_history(self, customer_id: int) -> List[Dict]:
#         """Get conversation history"""
#         return self.conversation_memory.get(customer_id, [])
    
#     def _save_to_memory(self, customer_id: int, user_msg: str, ai_msg: str):
#         """Save conversation to memory"""
#         if customer_id not in self.conversation_memory:
#             self.conversation_memory[customer_id] = []
        
#         self.conversation_memory[customer_id].append({"role": "user", "content": user_msg})
#         self.conversation_memory[customer_id].append({"role": "assistant", "content": ai_msg})
        
#         # Limit history length (only keep the last 10 rounds)
#         if len(self.conversation_memory[customer_id]) > 20:
#             self.conversation_memory[customer_id] = self.conversation_memory[customer_id][-20:]

# # Global singleton
# _chatbot = None

# def get_chatbot() -> DJIChatbot:
#     """Get chatbot instance (singleton)"""
#     global _chatbot
#     if _chatbot is None:
#         _chatbot = DJIChatbot()
#     return _chatbot
