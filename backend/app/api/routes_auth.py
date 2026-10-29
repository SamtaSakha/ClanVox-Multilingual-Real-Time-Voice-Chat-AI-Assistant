from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from ..core.security import create_access_token

router = APIRouter(prefix="/v1/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    # Authenticate user (guest / demo accepted)
    user_id = credentials.username or "demo_user"
    token = create_access_token({"sub": user_id})
    return TokenResponse(access_token=token, user_id=user_id)

