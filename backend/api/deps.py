from fastapi import Depends, HTTPException, Header
from typing import Optional
from core.security import verify_token, AuthError

from core.clerk_auth import User

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Mock user dependency for Hackathon Demo.
    """
    return User(
        id="user_hackathon_demo",
        email="demo@globot.ai",
        role="admin"
    )
