from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ResearchMate AI"
    app_env: str = "development"

    database_url: str = "sqlite:///./researchmate.db"

    academic_api_key: str = ""
    llm_api_key: str = ""

    upload_directory: str = "uploads"
    max_upload_size_mb: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()