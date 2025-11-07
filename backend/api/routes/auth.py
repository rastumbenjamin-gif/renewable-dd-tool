"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login with email and password"""
    # TODO: Implement actual authentication
    logger.info("Login attempt", email=request.email)

    return {
        "access_token": "demo-token-123",
        "token_type": "bearer",
        "user": {
            "id": "user-1",
            "email": request.email,
            "name": "Demo User",
        },
    }


@router.post("/google")
async def google_auth(token: str):
    """Authenticate with Google OAuth"""
    # TODO: Implement Google OAuth
    logger.info("Google auth attempt")

    return {
        "access_token": "demo-token-123",
        "token_type": "bearer",
        "user": {
            "id": "user-1",
            "email": "demo@example.com",
            "name": "Demo User",
        },
    }


@router.post("/logout")
async def logout():
    """Logout user"""
    logger.info("User logout")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user():
    """Get current user info"""
    return {
        "id": "user-1",
        "email": "demo@example.com",
        "name": "Demo User",
    }
