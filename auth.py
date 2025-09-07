"""
Basic authentication scaffolding for the Fantastic Palm Tree API.

This module provides simple API key authentication and can be extended
for more sophisticated authentication methods in the future.
"""

import os
import secrets
from typing import Optional
from functools import wraps

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from env_config import get_config


class APIKeyAuth:
    """Simple API key authentication."""
    
    def __init__(self):
        self.config = get_config()
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
        """Validate API key if authentication is enabled."""
        if not self.config.enable_api_key_auth:
            return True  # Authentication disabled
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not self._validate_api_key(credentials.credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return True
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate the provided API key."""
        expected_key = self.config.api_key
        if not expected_key:
            return False
        
        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(api_key, expected_key)


# Global authentication instance
auth = APIKeyAuth()


def require_auth():
    """Dependency to require authentication."""
    return Depends(auth)


def optional_auth():
    """Dependency for optional authentication."""
    async def _optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
        if credentials:
            return await auth(credentials)
        return False
    
    return Depends(_optional_auth)


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


class SecretManager:
    """Basic secret management utilities."""
    
    @staticmethod
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret from environment variables."""
        return os.getenv(key, default)
    
    @staticmethod
    def require_secret(key: str) -> str:
        """Get a required secret from environment variables."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    @staticmethod
    def mask_secret(secret: str, visible_chars: int = 4) -> str:
        """Mask a secret for logging purposes."""
        if not secret or len(secret) <= visible_chars:
            return "*" * len(secret) if secret else ""
        
        return secret[:visible_chars] + "*" * (len(secret) - visible_chars)


# Example usage patterns
def create_auth_examples():
    """Examples of how to use authentication in routes."""
    
    # This would be used in FastAPI routes like:
    
    # @app.get("/protected")
    # async def protected_route(auth_result = require_auth()):
    #     return {"message": "This is a protected route"}
    
    # @app.get("/optional")
    # async def optional_route(is_authenticated = optional_auth()):
    #     if is_authenticated:
    #         return {"message": "Authenticated user"}
    #     else:
    #         return {"message": "Anonymous user"}
    
    pass


# Security guidelines for users
SECURITY_GUIDELINES = """
Security Guidelines for Production Deployment:

1. API Keys:
   - Generate strong API keys using generate_api_key()
   - Store API keys in environment variables, never in code
   - Rotate API keys regularly
   - Use different keys for different environments

2. Environment Variables:
   - Set ENABLE_API_KEY_AUTH=true in production
   - Set API_KEY to a strong, random value
   - Use SESSION_SECRET for session management
   - Never commit secrets to version control

3. HTTPS:
   - Always use HTTPS in production
   - Configure proper SSL/TLS certificates
   - Use HSTS headers for additional security

4. Monitoring:
   - Monitor failed authentication attempts
   - Set up alerts for suspicious activity
   - Log authentication events (without secrets)

5. Access Control:
   - Implement rate limiting for API endpoints
   - Use IP whitelisting when appropriate
   - Consider implementing role-based access control

Example Production Environment:
```bash
export ENVIRONMENT=production
export ENABLE_API_KEY_AUTH=true
export API_KEY=$(python -c "from auth import generate_api_key; print(generate_api_key())")
export SESSION_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```
"""