# ========== 数据模型（新增） ==========

class HumanMessageRequest(BaseModel):
    """人工发送消息请求"""
    conversation_id: int
    content: str
    agent_name: str = "人工客服"

class UpdateHandoffRequest(BaseModel):
    """更新转人工状态请求"""
    status: str  # pending/processing/completed
    agent_name: Optional[str] = None
