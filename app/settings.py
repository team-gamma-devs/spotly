from pydantic_settings import BaseSettings
import os


class BaseSettingsClass(BaseSettings):
    resend_api_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


class DevelopmentSettings(BaseSettingsClass):
    debug: bool = True


class ProductionSettings(BaseSettingsClass):
    debug: bool = False


# Select class depends of the env.
env = os.getenv("ENV", "development")
settings = DevelopmentSettings() if env == "development" else ProductionSettings()
