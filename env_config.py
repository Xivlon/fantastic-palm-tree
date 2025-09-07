"""
Environment-driven configuration for the Fantastic Palm Tree framework.

This module provides configuration management that respects environment variables
and supports different deployment environments (development, testing, production).
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum


class Environment(str, Enum):
    """Supported deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ServerConfig:
    """Server configuration with environment variable support."""
    
    # Environment
    environment: Environment = field(
        default_factory=lambda: Environment(os.getenv("ENVIRONMENT", "development"))
    )
    
    # Server settings
    host: str = field(default_factory=lambda: os.getenv("HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    
    # API settings
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(",")
    )
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("API_KEY"))
    
    # Database/Storage
    data_directory: str = field(
        default_factory=lambda: os.getenv("DATA_DIRECTORY", "./data")
    )
    cache_directory: str = field(
        default_factory=lambda: os.getenv("CACHE_DIRECTORY", "./cache")
    )
    
    # External services
    alpha_vantage_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ALPHA_VANTAGE_API_KEY")
    )
    schwab_client_id: Optional[str] = field(
        default_factory=lambda: os.getenv("SCHWAB_CLIENT_ID")
    )
    schwab_client_secret: Optional[str] = field(
        default_factory=lambda: os.getenv("SCHWAB_CLIENT_SECRET")
    )
    
    # Logging
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    log_format: str = field(
        default_factory=lambda: os.getenv("LOG_FORMAT", "json")
    )
    
    # Performance
    max_concurrent_backtests: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONCURRENT_BACKTESTS", "5"))
    )
    worker_threads: int = field(
        default_factory=lambda: int(os.getenv("WORKER_THREADS", "4"))
    )
    
    # Security
    enable_api_key_auth: bool = field(
        default_factory=lambda: os.getenv("ENABLE_API_KEY_AUTH", "false").lower() == "true"
    )
    session_secret: Optional[str] = field(
        default_factory=lambda: os.getenv("SESSION_SECRET")
    )
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()
        self._setup_directories()
    
    def _validate(self):
        """Validate configuration values."""
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}")
        
        if self.max_concurrent_backtests < 1:
            raise ValueError(f"Invalid max_concurrent_backtests: {self.max_concurrent_backtests}")
        
        if self.worker_threads < 1:
            raise ValueError(f"Invalid worker_threads: {self.worker_threads}")
        
        if self.environment == Environment.PRODUCTION:
            if self.debug:
                raise ValueError("Debug mode should not be enabled in production")
            
            if self.enable_api_key_auth and not self.api_key:
                raise ValueError("API key required when authentication is enabled")
    
    def _setup_directories(self):
        """Create required directories if they don't exist."""
        os.makedirs(self.data_directory, exist_ok=True)
        os.makedirs(self.cache_directory, exist_ok=True)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration for FastAPI."""
        if self.is_development:
            return {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            }
        else:
            return {
                "allow_origins": self.cors_origins,
                "allow_credentials": True,
                "allow_methods": ["GET", "POST"],
                "allow_headers": ["*"],
            }
    
    def get_env_summary(self) -> Dict[str, Any]:
        """Get a summary of configuration for health checks."""
        return {
            "environment": self.environment.value,
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "api_key_auth_enabled": self.enable_api_key_auth,
            "external_services": {
                "alpha_vantage": bool(self.alpha_vantage_api_key),
                "schwab": bool(self.schwab_client_id and self.schwab_client_secret),
            },
            "directories": {
                "data": self.data_directory,
                "cache": self.cache_directory,
            },
            "performance": {
                "max_concurrent_backtests": self.max_concurrent_backtests,
                "worker_threads": self.worker_threads,
            }
        }


# Global configuration instance
config = ServerConfig()


def get_config() -> ServerConfig:
    """Get the global configuration instance."""
    return config


def reload_config() -> ServerConfig:
    """Reload configuration from environment variables."""
    global config
    config = ServerConfig()
    return config