from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # API Settings
    api_title: str = "3270 Terminal Automation Builder"
    api_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS Settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Directory Settings
    scripts_dir: str = "../scripts"
    logs_dir: str = "../logs"


settings = Settings()
