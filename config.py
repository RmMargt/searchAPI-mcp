"""
Configuration management module with Pydantic validation.
Following FAST MCP best practices for externalized configuration.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIConfig(BaseSettings):
    """SearchAPI configuration with validation."""

    # API Configuration
    api_key: str = Field(
        ...,
        description="SearchAPI.io API key",
        validation_alias="SEARCHAPI_API_KEY"
    )
    api_url: str = Field(
        default="https://www.searchapi.io/api/v1/search",
        description="SearchAPI base URL"
    )

    # HTTP Client Configuration
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts"
    )
    retry_backoff: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Retry backoff multiplier"
    )

    # Cache Configuration
    enable_cache: bool = Field(
        default=True,
        description="Enable response caching"
    )
    cache_ttl: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Cache TTL in seconds (1 hour default)"
    )
    cache_max_size: int = Field(
        default=1000,
        ge=10,
        le=10000,
        description="Maximum number of cached items"
    )

    # Connection Pool Configuration
    pool_connections: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of connection pool instances"
    )
    pool_maxsize: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of connections in pool"
    )

    # Monitoring Configuration
    enable_metrics: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty or placeholder."""
        if not v or v in ["your_api_key_here", "YOUR_API_KEY"]:
            raise ValueError(
                "Invalid API key. Please set SEARCHAPI_API_KEY environment variable."
            )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # Allow extra fields for testing
    )


class ServerConfig(BaseModel):
    """Server runtime configuration."""

    name: str = Field(
        default="searchapi",
        description="MCP server name"
    )
    transport: str = Field(
        default="stdio",
        description="MCP transport type (stdio, sse, etc.)"
    )
    version: str = Field(
        default="1.0.0",
        description="Server version"
    )


def load_config() -> APIConfig:
    """
    Load and validate configuration from environment.

    Returns:
        APIConfig: Validated configuration object

    Raises:
        ValueError: If configuration is invalid
    """
    try:
        return APIConfig()
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}")


def get_transport() -> str:
    """Get MCP transport type from environment."""
    return os.environ.get("MCP_TRANSPORT", "stdio")
