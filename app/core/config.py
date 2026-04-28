from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class Settings(BaseSettings):
    app_name: str = Field(
        default="Figma Scraper API",
        validation_alias="APP_NAME",
    )
    api_v1_prefix: str = Field(
        default="/api/v1",
        validation_alias="API_V1_PREFIX",
    )
    environment: str = Field(
        default="development",
        validation_alias="ENV",
    )

    figma_max_retry_wait_seconds: int = Field(
        default=10,
        validation_alias="FIGMA_API_MAX_RETRY_WAIT_SECONDS",
    )

    figma_api_url: str = Field(
        default="https://api.figma.com/v1",
        validation_alias="FIGMA_API_URL",
    )

    figma_access_token: str = Field(
        default="",
        validation_alias="FIGMA_ACCESS_TOKEN",
        repr=False,
    )

    @model_validator(mode="after")
    def validate_figma_token(self) -> "Settings":
        token = (self.figma_access_token or "").strip()
        if not token:
            raise ValueError(
                "FIGMA_ACCESS_TOKEN environment variable is required"
            )
        # Catch the most common dev mistake: forgetting to replace the placeholder
        invalid_placeholders = {
            "your_figma_personal_access_token_here",
            "figd_replace_with_your_real_token",
        }
        if token.lower() in invalid_placeholders or token.lower().startswith("your_"):
            raise ValueError(
                "FIGMA_ACCESS_TOKEN looks like the placeholder from .env.example. "
                "Edit .env and paste your real Figma Personal Access Token "
                "(it must start with 'figd_')."
            )
        if not token.startswith("figd_"):
            # Soft warning: print but allow (in case Figma changes prefix)
            import sys
            print(
                f"[config] WARNING: FIGMA_ACCESS_TOKEN does not start with 'figd_' "
                f"(len={len(token)}). Make sure you copied the full token.",
                file=sys.stderr,
            )
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
