from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://admin:adminpass@localhost/swifty_logs"
    app_name: str = "swifty"

settings = Settings()

