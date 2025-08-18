"""Configuration management for the mail sorter application.

This module provides Pydantic-based configuration loading from environment
variables and .env files with proper validation and type conversion.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailConfig(BaseSettings):
    """Email server configuration settings."""
    
    imap_host: str = Field(..., env="IMAP_HOST")
    imap_port: int = Field(993, env="IMAP_PORT")
    imap_user: str = Field(..., env="IMAP_USER")
    imap_password: str = Field(..., env="IMAP_PASSWORD")
    imap_use_ssl: bool = Field(True, env="IMAP_USE_SSL")
    imap_folder: str = Field("INBOX", env="IMAP_FOLDER")
    imap_batch_size: int = Field(50, env="IMAP_BATCH_SIZE", ge=1, le=1000)

    @field_validator("imap_host")
    @classmethod
    def validate_imap_host(cls, v: str) -> str:
        """Validate IMAP host is not empty."""
        if not v.strip():
            raise ValueError("IMAP host cannot be empty")
        return v.strip()

    @field_validator("imap_user")
    @classmethod
    def validate_imap_user(cls, v: str) -> str:
        """Validate IMAP user is not empty."""
        if not v.strip():
            raise ValueError("IMAP user cannot be empty")
        return v.strip()
    
    @field_validator("imap_password")
    @classmethod
    def validate_imap_password(cls, v: str) -> str:
        """Validate IMAP password is not empty."""
        if not v.strip():
            raise ValueError("IMAP password cannot be empty")
        return v.strip()

class DatabaseConfig(BaseSettings):
    """Database configuration settings.
    
    Supports multiple database backends with type-specific configuration.
    Compatible with the repository factory pattern for dependency injection.
    """
    
    database_type: Literal["sqlite", "dynamodb"] = Field("sqlite", env="DATABASE_TYPE")
    
    # SQLite settings
    sqlite_db_path: Path = Field(
        Path("./mailbot/data/checkpoints.db"), 
        env="SQLITE_DB_PATH"
    )
    
    # DynamoDB settings
    aws_region: str = Field("us-east-1", env="AWS_REGION")
    aws_access_key_id: str | None = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(None, env="AWS_SECRET_ACCESS_KEY")
    dynamodb_table_name: str = Field("mail_checkpoints", env="DYNAMODB_TABLE_NAME")

    @property
    def database_path(self) -> Path:
        """Get the appropriate database path based on database type.
        
        Returns:
            Path to database file for SQLite, placeholder for DynamoDB
            
        Raises:
            ValueError: If database type is unsupported
        """
        if self.database_type == "sqlite":
            return self.sqlite_db_path
        elif self.database_type == "dynamodb":
            # For DynamoDB, return a placeholder path (not used)
            return Path("dynamodb://placeholder")
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")

    @field_validator("sqlite_db_path")
    @classmethod
    def validate_sqlite_path(cls, v: Path) -> Path:
        """Ensure SQLite database directory exists."""
        if isinstance(v, str):
            v = Path(v)
        v.parent.mkdir(parents=True, exist_ok=True)
        return v


class AppConfig(BaseSettings):
    """Application-wide configuration settings."""
    
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Path = Field(Path("./logs/mailbot.log"), env="LOG_FILE")
    debug: bool = Field(False, env="DEBUG")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v_upper

    @field_validator("log_file")
    @classmethod
    def validate_log_file(cls, v: Path) -> Path:
        """Ensure log directory exists."""
        if isinstance(v, str):
            v = Path(v)
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

# TODO: update while training model
class MLConfig(BaseSettings):
    """Machine learning model configuration settings."""
    
    model_path: Path = Field(
        Path("./mailbot/data/models/classifier.joblib"), 
        env="MODEL_PATH"
    )
    retrain_threshold: int = Field(100, env="RETRAIN_THRESHOLD", ge=1)
    confidence_threshold: float = Field(
        0.8, 
        env="CONFIDENCE_THRESHOLD", 
        ge=0.0, 
        le=1.0
    )

    @field_validator("model_path")
    @classmethod
    def validate_model_path(cls, v: Path) -> Path:
        """Ensure model directory exists."""
        if isinstance(v, str):
            v = Path(v)
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

# TODO: update while configuration app logic
class ProcessingConfig(BaseSettings):
    """Email processing configuration settings."""
    
    auto_delete_spam: bool = Field(False, env="AUTO_DELETE_SPAM")
    spam_folder: str = Field("Spam", env="SPAM_FOLDER")
    important_folder: str = Field("Important", env="IMPORTANT_FOLDER")
    processed_folder: str = Field("Processed", env="PROCESSED_FOLDER")


class Settings(BaseSettings):
    """Main application settings combining all configuration sections."""
    
    email: EmailConfig = EmailConfig()
    database: DatabaseConfig = DatabaseConfig()
    app: AppConfig = AppConfig()
    ml: MLConfig = MLConfig()
    processing: ProcessingConfig = ProcessingConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance, creating it if necessary.
    
    Returns:
        Settings: The application settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment and .env file.
    
    Returns:
        Settings: The refreshed application settings instance.
    """
    global _settings
    _settings = Settings()
    return _settings


def get_env_path() -> Path:
    """Get the path to the .env file.
    
    Returns:
        Path: Path to the .env file in the project root.
    """
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    return project_root / ".env"


def is_env_file_present() -> bool:
    """Check if .env file exists in the project root.
    
    Returns:
        bool: True if .env file exists, False otherwise.
    """
    return get_env_path().exists()
