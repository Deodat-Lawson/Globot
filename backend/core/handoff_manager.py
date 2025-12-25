"""
人工转接模块 (Module 6)
处理AI到人工客服的转接逻辑
"""
from services.llm_service import get_llm_service
from models import Handoff, Conversation, Message
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HandoffManager:
    """人工转接管理器"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    def create_handoff(self, db: Session, conversation_id: int, reason: str) -> int:
        """
        创建转接记录
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            reason: 转接原因
            
        Returns:
            转接记录ID
        """
        handoff = Handoff(
            conversation_id=conversation_id,
            trigger_reason=reason,
            created_at=datetime.now()
        )
        db.add(handoff)
        
        # 更新会话状态
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.status = "handoff"
        
        db.commit()
        
        logger.info(f"创建转接记录: 会话{conversation_id}, 原因:{reason}")
        return handoff.id
    
    def generate_summary(self, db: Session, conversation_id: int) -> str:
        """
        生成对话摘要（给人工销售看）
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            
        Returns:
            对话摘要
        """
        # 1. 获取对话记录
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        if not messages:
            return "暂无对话记录"
        
        # 2. 格式化对话
        conversation_text = "\n".join([
            f"{msg.sender.value}: {msg.content}"
            for msg in messages
        ])
        
        # 3. 使用LLM生成摘要
        prompt = f"""为人工销售生成对话摘要：

{conversation_text}

请提供：
1. 客户核心需求（1句话）
2. 提及的产品型号
3. 当前进展
4. 待解决问题
5. 建议的下一步行动

摘要："""
        
        summary = self.llm.generate(prompt, temperature=0.3)
        
        # 4. 保存摘要
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.summary = summary
            db.commit()
        
        return summary

# 全局单例
_handoff_manager = None

def get_handoff_manager() -> HandoffManager:
    """获取转接管理器实例（单例）"""
    global _handoff_manager
    if _handoff_manager is None:
        _handoff_manager = HandoffManager()
    return _handoff_manager
