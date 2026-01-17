from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from grader.configs.paths import PATH_ENV


class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr

    model_config = SettingsConfigDict(env_file=PATH_ENV, env_file_encoding="utf-8")


settings = Settings()
