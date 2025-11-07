"""
Authentication and authorization module
Implements role-based access control and session management
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import structlog
from enum import Enum

from api.config import settings
from security.session import SessionManager

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()


class Role(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    REVIEWER = "reviewer"
    READ_ONLY = "read_only"


class Permission(str, Enum):
    """Granular permissions"""
    VIEW_DOCUMENTS = "view_documents"
    UPLOAD_DOCUMENTS = "upload_documents"
    DELETE_DOCUMENTS = "delete_documents"
    MANAGE_PROJECTS = "manage_projects"
    MANAGE_USERS = "manage_users"
    EXPORT_DATA = "export_data"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    ANNOTATE_DOCUMENTS = "annotate_documents"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.VIEW_DOCUMENTS,
        Permission.UPLOAD_DOCUMENTS,
        Permission.DELETE_DOCUMENTS,
        Permission.MANAGE_PROJECTS,
        Permission.MANAGE_USERS,
        Permission.EXPORT_DATA,
        Permission.VIEW_AUDIT_LOGS,
        Permission.ANNOTATE_DOCUMENTS,
    ],
    Role.REVIEWER: [
        Permission.VIEW_DOCUMENTS,
        Permission.UPLOAD_DOCUMENTS,
        Permission.EXPORT_DATA,
        Permission.ANNOTATE_DOCUMENTS,
    ],
    Role.READ_ONLY: [
        Permission.VIEW_DOCUMENTS,
        Permission.EXPORT_DATA,
    ],
}


class AuthService:
    """Authentication service"""

    def __init__(self):
        self.session_manager = SessionManager()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token

        Args:
            data: Data to encode in token
            expires_delta: Optional expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        logger.info("Access token created", user_id=data.get("sub"))
        return encoded_jwt

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate JWT token

        Args:
            token: JWT token

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )

            return payload

        except JWTError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> Dict[str, Any]:
        """
        Get current authenticated user from token

        Args:
            credentials: HTTP Bearer credentials

        Returns:
            User information

        Raises:
            HTTPException: If authentication fails
        """
        token = credentials.credentials
        payload = self.decode_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Check if session is still valid
        session_valid = await self.session_manager.validate_session(user_id, token)
        if not session_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid"
            )

        # Update session activity
        await self.session_manager.update_session_activity(user_id)

        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role"),
            "name": payload.get("name"),
        }

    def has_permission(self, user_role: str, permission: Permission) -> bool:
        """
        Check if user role has a specific permission

        Args:
            user_role: User's role
            permission: Permission to check

        Returns:
            True if user has permission
        """
        try:
            role = Role(user_role)
            return permission in ROLE_PERMISSIONS.get(role, [])
        except ValueError:
            logger.warning(f"Invalid role: {user_role}")
            return False

    def require_permission(self, permission: Permission):
        """
        Dependency for requiring a specific permission

        Args:
            permission: Required permission

        Returns:
            Dependency function
        """
        async def permission_checker(
            current_user: Dict[str, Any] = Depends(self.get_current_user)
        ):
            user_role = current_user.get("role")
            if not self.has_permission(user_role, permission):
                logger.warning(
                    f"Permission denied",
                    user_id=current_user.get("user_id"),
                    permission=permission
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}"
                )
            return current_user

        return permission_checker

    def require_role(self, required_role: Role):
        """
        Dependency for requiring a specific role

        Args:
            required_role: Required role

        Returns:
            Dependency function
        """
        async def role_checker(
            current_user: Dict[str, Any] = Depends(self.get_current_user)
        ):
            user_role = current_user.get("role")
            if user_role != required_role.value:
                logger.warning(
                    f"Role check failed",
                    user_id=current_user.get("user_id"),
                    required_role=required_role.value,
                    user_role=user_role
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required role: {required_role.value}"
                )
            return current_user

        return role_checker


# Global auth service instance
auth_service = AuthService()


# Dependency functions for route protection
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    return await auth_service.get_current_user(credentials)


def require_permission(permission: Permission):
    """Require specific permission"""
    return auth_service.require_permission(permission)


def require_role(role: Role):
    """Require specific role"""
    return auth_service.require_role(role)
