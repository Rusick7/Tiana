from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str
    TOKEN: str

    @property
    def DATABASE_URL_asyncpg(self):
        return f"sqlite+aiosqlite:///./app/Database/data/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()