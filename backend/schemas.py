# ========== Data Models (New) ==========

class HumanMessageRequest(BaseModel):
    """Request to send manual message"""
    conversation_id: int
    content: str
    agent_name: str = "Human Support"

class UpdateHandoffRequest(BaseModel):
    """Request to update handoff status"""
    status: str  # pending/processing/completed
    agent_name: Optional[str] = None
