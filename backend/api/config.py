"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Settings
    APP_NAME: str = "Renewable DD Tool"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    SESSION_TIMEOUT_MINUTES: int = 15

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./renewable_dd.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_DB: int = 1

    # Google Cloud (Optional for development)
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Google Drive
    GOOGLE_DRIVE_API_VERSION: str = "v3"
    GOOGLE_DRIVE_ROOT_FOLDER: str = "DD-Projects"

    # Google Cloud KMS (Optional for development)
    GCP_KMS_KEY_RING: Optional[str] = None
    GCP_KMS_CRYPTO_KEY: Optional[str] = None
    GCP_KMS_LOCATION: str = "us-central1"

    # OAuth 2.0 (Optional for development)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    # Security
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    PASSWORD_MIN_LENGTH: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30

    # Data Retention
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    SESSION_DATA_RETENTION_HOURS: int = 24
    TEMP_FILE_RETENTION_MINUTES: int = 5

    # Document Processing
    MAX_DOCUMENT_SIZE_MB: int = 100
    SUPPORTED_FORMATS: str = "pdf,docx,xlsx,doc,xls,txt,csv"
    PROCESSING_QUEUE_NAME: str = "document-processing"
    MAX_CONCURRENT_PROCESSING: int = 10

    # AI/ML Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4000
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Vector Database
    VECTOR_DB_TYPE: str = "pinecone"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "renewable-dd-documents"

    # Monitoring and Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    ENABLE_AUDIT_LOGGING: bool = True
    AUDIT_LOG_PATH: str = "logs/audit.log"

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_ADDRESS: str = "noreply@renewable-dd-tool.com"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Document Classification
    MIN_CLASSIFICATION_CONFIDENCE: float = 0.75
    MIN_EXTRACTION_CONFIDENCE: float = 0.70

    # Renewable Energy Specific
    DEFAULT_CAPACITY_FACTOR_SOLAR: float = 0.25
    DEFAULT_CAPACITY_FACTOR_WIND: float = 0.35
    DEFAULT_CAPACITY_FACTOR_HYDRO: float = 0.45
    MERCHANT_TAIL_DISCOUNT_RATE: float = 0.08

    # CORS and Security
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    @property
    def supported_formats_list(self) -> List[str]:
        """Return supported formats as a list"""
        return [fmt.strip() for fmt in self.SUPPORTED_FORMATS.split(",")]

    @property
    def max_document_size_bytes(self) -> int:
        """Return max document size in bytes"""
        return self.MAX_DOCUMENT_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
