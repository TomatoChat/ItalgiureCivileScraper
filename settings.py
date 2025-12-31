from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the root directory where .env file should be located
ROOT_DIR = Path(__file__).parent
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    hf_token: str = Field(default="", description="HuggingFace token")
    hf_repo_id: str = Field(default="", description="HuggingFace repository ID")

    @field_validator("hf_token", "hf_repo_id")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip whitespace from string values."""
        if v and isinstance(v, str):
            return v.strip()
        return v

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
