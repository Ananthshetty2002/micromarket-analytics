requirement\backend\app\core\auth.py
```

```python
"""
Authentication stubs for Micromarket Analytics Platform

This file contains placeholder authentication functions.
Replace with actual JWT or OAuth implementation as needed.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from datetime import datetime

# Security scheme for API documentation
security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Simple user model for demo purposes"""

    def __init__(
        self,
        id: str,
        email: str,
        name: str,
        role: str = "viewer"
    ):
        self.id = id
        self.email = email
        self.name = name
        self.role = role  # admin, manager, analyst, viewer

    def dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role
        }


# Demo users for client demo
DEMO_USERS = {
    "demo-token-1": CurrentUser(
        id="550e8400-e29b-41d4-a716-446655440001",
        email="admin@micromarket.com",
        name="Admin User",
        role="admin"
    ),
    "demo-token-2": CurrentUser(
        id="550e8400-e29b-41d4-a716-446655440002",
        email="manager@micromarket.com",
        name="Manager User",
        role="manager"
    ),
    "demo-token-3": CurrentUser(
        id="550e8400-e29b-41d4-a716-446655440003",
        email="analyst@micromarket.com",
        name="Analyst User",
        role="analyst"
    )
}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    Get current authenticated user from JWT token.

    For demo: accepts any of the demo tokens above.
    Replace with actual JWT validation in production.
    """
    if not credentials:
        # Return default demo user for ease of testing
        return DEMO_USERS["demo-token-2"]

    token = credentials.credentials

    # Demo token validation
    if token in DEMO_USERS:
        return DEMO_USERS[token]

    # For development - accept any bearer token as demo user
    if token.startswith("demo-"):
        return DEMO_USERS["demo-token-2"]

    # Production: validate JWT here
    # try:
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    #     user_id = payload.get("sub")
    #     ...

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Verify user is active (not disabled).
    """
    # Add active check if needed
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(allowed_roles: list):
    """
    Dependency factory to require specific roles.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            user: CurrentUser = Depends(require_role(["admin"]))
        ):
            ...
    """
    async def role_checker(
        current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized. Required: {allowed_roles}"
            )
        return current_user
    return role_checker


# Common role requirements
require_admin = require_role(["admin"])
require_manager = require_role(["admin", "manager"])
require_analyst = require_role(["admin", "manager", "analyst"])
