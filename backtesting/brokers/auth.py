import asyncio
import aiohttp
import base64
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode
import logging


class SchwabAuth:
    """Handles Schwab API authentication."""
    
    def __init__(self, client_id: str, client_secret: str, 
                 redirect_uri: str = "https://localhost"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # Schwab API endpoints
        self.auth_url = "https://api.schwabapi.com/v1/oauth/authorize"
        self.token_url = "https://api.schwabapi.com/v1/oauth/token"
        
        self.logger = logging.getLogger(__name__)
        
    def get_authorization_url(self) -> str:
        """Get the authorization URL for OAuth flow."""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'readonly'  # Adjust scope as needed
        }
        return f"{self.auth_url}?{urlencode(params)}"
        
    async def exchange_code_for_tokens(self, authorization_code: str) -> bool:
        """Exchange authorization code for access tokens."""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get('access_token')
                        self.refresh_token = token_data.get('refresh_token')
                        
                        # Calculate expiration time
                        expires_in = token_data.get('expires_in', 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                        
                        self.logger.info("Successfully obtained access tokens")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Token exchange failed: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Token exchange error: {e}")
            return False
            
    async def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            self.logger.error("No refresh token available")
            return False
            
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get('access_token')
                        
                        # Update refresh token if provided
                        new_refresh_token = token_data.get('refresh_token')
                        if new_refresh_token:
                            self.refresh_token = new_refresh_token
                            
                        # Calculate expiration time
                        expires_in = token_data.get('expires_in', 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                        
                        self.logger.info("Successfully refreshed access token")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Token refresh failed: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Token refresh error: {e}")
            return False
            
    async def ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token."""
        if not self.access_token:
            self.logger.error("No access token available")
            return False
            
        # Check if token is close to expiration (refresh 5 minutes early)
        if self.token_expires_at and datetime.now() >= (self.token_expires_at - timedelta(minutes=5)):
            self.logger.info("Access token near expiration, refreshing...")
            return await self.refresh_access_token()
            
        return True
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get headers for authenticated requests."""
        if not self.access_token:
            raise ValueError("No access token available")
            
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
    def save_tokens(self, filepath: str) -> None:
        """Save tokens to file (implement encryption in production)."""
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(token_data, f)
            
    def load_tokens(self, filepath: str) -> bool:
        """Load tokens from file."""
        try:
            with open(filepath, 'r') as f:
                token_data = json.load(f)
                
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            
            expires_at_str = token_data.get('expires_at')
            if expires_at_str:
                self.token_expires_at = datetime.fromisoformat(expires_at_str)
                
            return True
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to load tokens: {e}")
            return False