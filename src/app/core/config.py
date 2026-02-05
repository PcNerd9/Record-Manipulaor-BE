from pydantic import SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
import os



class AppSettings(BaseSettings):
    APP_NAME: str = "Record Manipulator"
    APP_DESCRIPTON: str = "This is a Record Manipulator api"
    APP_VERSION: str = "1.0.0"
    API_BASE: str = "/api/v1"
    PORT: int = 8000
    
    
    
class CryptSettings(BaseSettings):
    SECRET_KEY: SecretStr = SecretStr('secret-key')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRY_TIME: int = 30
    
    
class LoggerSettings(BaseSettings):
    CONSOLE_LOG_LEVEL: str = "INFO"
    CONSOLE_LOG_FORMAT_JSON: bool = False
    
    # Include request ID, Path, Method, client host and status code in the console log
    INCLUDE_REQUEST_ID: bool = False
    INCLUDE_PATH: bool = False
    INCLUDE_METHOD: bool = False
    INLCLUDE_CLIENT_HOST: bool = False
    INCLUDE_STATUS_CODE: bool = False
    
class DatabaseSettings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_PREFIX: str = "postgresql+asyncpg://"
    DB_URL: str | None = None
    
    @computed_field
    @property
    def DB_URI(self) -> str:
        if self.DB_URL:
            return self.DB_URL
        credentials = f"{self.DB_USER}:{self.DB_PASSWORD}"
        location = f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        return f"{self.DB_PREFIX}{credentials}@{location}"
    
class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_POST: int = 6379
    REDIS_URL: str | None = None
    
    @computed_field
    @property
    def REDIS_URI(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_POST}"
    
    
class DefaultRateLimitSettings(BaseSettings):
    DEFAULT_RATE_LIMIT_LIMIT: int = 10
    DEFAULT_RATE_LIMIT_PERIOD: int = 3600
    
    
class EnvironmentOption(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"
    
class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = EnvironmentOption.LOCAL
    
class CORSSettings(BaseSettings):
    CORS_ORIGINS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    
    @field_validator("CORS_ORIGINS", "CORS_METHODS", "CORS_HEADERS", mode="before")
    @classmethod
    def split_str(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [item.strip() for item in v.split(",")]
        
        return v
    
class EmailSettings(BaseSettings):
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 465
    SMTP_HOST: str ="smtp.gmail.com"
    SMTP_USER: str = "johdoe@gmail.com"
    SMTP_PASSWORD: SecretStr = SecretStr("my-app-password")
    EMAILS_FROM_EMAIL: str ="johndoe@gmail.com"
    EMAILS_FROM_NAME: str ="John Doe"

class Settings(
    AppSettings,
    DatabaseSettings,
    CryptSettings,
    RedisSettings,
    LoggerSettings,
    DefaultRateLimitSettings,
    EnvironmentSettings,
    CORSSettings,
    EmailSettings
):
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "..",
            ".env"
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    

settings = Settings()

    
    