from datetime import timedelta

from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    postgres_dsn: PostgresDsn = "postgresql+asyncpg://user:pass@127.0.0.1:5432/db"
    redis_dsn: RedisDsn = "redis://127.0.0.1:6379"
    log_level: str = "INFO"
    postgres_echo: bool = False

    authjwt_secret_key: str = "secret"
    authjwt_access_token_expires: timedelta = 600  # 10 минут
    authjwt_refresh_token_expires: timedelta = 604800  # 7 дней
    authjwt_denylist_enabled: bool = True

    session_secret_key: str = "secret"

    google_client_id: str = ""
    google_client_secret: str = ""
    vk_client_id: str = ""
    vk_client_secret: str = ""

    yandex_client_id: str = ""
    yandex_client_secret: str = ""

    frontend_redirect_url: str = "/"

    enable_tracer: bool = False
    jaeger_agent_host: str = "127.0.0.1"
    jaeger_agent_port: int = 6831

    enable_rate_limiter: bool = False
    rate_limiter_times: int = 2
    rate_limiter_seconds: int = 5


settings = Settings()
