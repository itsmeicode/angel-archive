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
        """
        Public base URL for Supabase Storage objects.

        Supabase public object URLs use:
          https://<ref>.supabase.co/storage/v1/object/public/<bucket>/<path>

        This app historically configured STATIC_ASSETS_URL as:
          https://<ref>.supabase.co/storage/v1
        so we normalize it to include /object/public automatically.
        """
        base = (self.static_assets_url or "").rstrip("/")

        # If user provided ".../storage/v1", upgrade to ".../storage/v1/object/public"
        if base.endswith("/storage/v1") and "/storage/v1/object/public" not in base:
            base = f"{base}/object/public"

        # If user already provided ".../storage/v1/object/public", keep it.
        return f"{base}/{self.bucket_name}".rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
