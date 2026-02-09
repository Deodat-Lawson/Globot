# """
# Handoff Module (Module 6)
# Handles the logic for handing off from AI to a human agent
# """
# from services.llm_service import get_llm_service
# from models import Handoff, Conversation, Message
# from sqlalchemy.orm import Session
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# class HandoffManager:
#     """Handoff Manager"""
    
#     def __init__(self):
#         self.llm = get_llm_service()
    
#     def create_handoff(self, db: Session, conversation_id: int, reason: str) -> int:
#         """
#         Create handoff record
        
#         Args:
#             db: Database session
#             conversation_id: Conversation ID
#             reason: Reason for handoff
            
#         Returns:
#             Handoff record ID
#         """
#         handoff = Handoff(
#             conversation_id=conversation_id,
#             trigger_reason=reason,
#             created_at=datetime.now()
#         )
#         db.add(handoff)
        
#         # Update conversation status
#         conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#         if conversation:
#             conversation.status = "handoff"
        
#         db.commit()
        
#         logger.info(f"Created handoff record: Conversation {conversation_id}, Reason: {reason}")
#         return handoff.id
    
#     def generate_summary(self, db: Session, conversation_id: int) -> str:
#         """
#         Generate conversation summary (for human salesperson)
        
#         Args:
#             db: Database session
#             conversation_id: Conversation ID
            
#         Returns:
#             Conversation summary
#         """
#         # 1. Retrieve conversation history
#         messages = db.query(Message).filter(
#             Message.conversation_id == conversation_id
#         ).order_by(Message.created_at).all()
        
#         if not messages:
#             return "No conversation history"
        
#         # 2. Format conversation
#         conversation_text = "\n".join([
#             f"{msg.sender.value}: {msg.content}"
#             for msg in messages
#         ])
        
#         # 3. Use LLM to generate summary
#         prompt = f"""Generate conversation summary for human salesperson:

# {conversation_text}

# Please provide:
# 1. Core customer needs (1 sentence)
# 2. Product models mentioned
# 3. Current progress
# 4. Issues to be resolved
# 5. Suggested next actions

# Summary:"""
        
#         summary = self.llm.generate(prompt, temperature=0.3)
        
#         # 4. Save summary
#         conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#         if conversation:
#             conversation.summary = summary
#             db.commit()
        
#         return summary

# # Global singleton
# _handoff_manager = None

# def get_handoff_manager() -> HandoffManager:
#     """Get handoff manager instance (singleton)"""
#     global _handoff_manager
#     if _handoff_manager is None:
#         _handoff_manager = HandoffManager()
#     return _handoff_manager
