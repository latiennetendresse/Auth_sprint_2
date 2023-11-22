from pydantic import AnyUrl, BaseSettings, PostgresDsn, RedisDsn


class TestSettings(BaseSettings):
    postgres_dsn: PostgresDsn
    redis_dsn: RedisDsn
    api_url: AnyUrl
    postgres_echo: bool = False


settings = TestSettings()
