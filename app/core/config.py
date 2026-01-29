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

    # 👇 Default satisfies Pylance
    figma_access_token: str = Field(
        default="",
        validation_alias="FIGMA_ACCESS_TOKEN",
        repr=False,
    )

    @model_validator(mode="after")
    def validate_figma_token(self) -> "Settings":
        if not self.figma_access_token:
            raise ValueError(
                "FIGMA_ACCESS_TOKEN environment variable is required"
            )
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
