from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class CustomerCategory(str, enum.Enum):
    """客户类别枚举"""
    HIGH_VALUE = "high_value"  # 优质客户
    NORMAL = "normal"          # 普通客户
    LOW_VALUE = "low_value"    # 低价值客户

class ConversationStatus(str, enum.Enum):
    """会话状态枚举"""
    ACTIVE = "active"      # 进行中
    CLOSED = "closed"      # 已关闭
    HANDOFF = "handoff"    # 已转人工

class MessageSender(str, enum.Enum):
    """消息发送者枚举"""
    CUSTOMER = "customer"  # 客户
    AI = "ai"             # AI
    HUMAN = "human"       # 人工客服

# ========== 数据模型 ==========

class Customer(Base):
    """客户表"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    company = Column(String(200))
    phone = Column(String(50))
    language = Column(String(10), default='zh-cn')
    
    # 分类相关
    category = Column(Enum(CustomerCategory), default=CustomerCategory.NORMAL)
    priority_score = Column(Integer, default=3)  # 1-5分
    classification_reason = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    conversations = relationship("Conversation", back_populates="customer")

class Conversation(Base):
    """会话表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    summary = Column(Text)  # 对话摘要
    
    # 统计
    message_count = Column(Integer, default=0)
    avg_confidence = Column(Float)  # 平均置信度
    
    # 时间戳
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime)
    
    # 关系
    customer = relationship("Customer", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    content = Column(Text, nullable=False)
    sender = Column(Enum(MessageSender), nullable=False)
    language = Column(String(10))
    
    # AI相关
    ai_confidence = Column(Float)  # 0.00-1.00
    retrieved_docs = Column(Text)  # RAG检索的文档片段（JSON格式）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")

class HandoffStatus(str, enum.Enum):
    """转人工状态枚举"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 已完成

class Handoff(Base):
    """人工转接记录表"""
    __tablename__ = "handoffs"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    trigger_reason = Column(String(50))  # manual/low_confidence/customer_request
    agent_name = Column(String(100))  # 接管的销售人员
    status = Column(Enum(HandoffStatus), default=HandoffStatus.PENDING)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class KBDocument(Base):
    """知识库文档元数据表"""
    __tablename__ = "kb_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    doc_type = Column(String(50))  # manual/faq/product_spec
    product_tag = Column(String(100))  # M30/M400/Dock3等
    source_file = Column(String(200))
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
