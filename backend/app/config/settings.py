from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""

    static_assets_url: str = ""
    bucket_name: str = "angels"

    redis_url: str = "redis://localhost:6379"

    node_env: str = "development"
    disable_rate_limit: bool = True

    port: int = 8080

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_development(self) -> bool:
        return self.node_env == "development"

    @property
    def storage_base_url(self) -> str:
        return f"{self.static_assets_url}/{self.bucket_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
