"""
Configurações centralizadas da aplicação usando Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação validadas com Pydantic"""
    
    # =============================================================================
    # API SETTINGS
    # =============================================================================
    APP_NAME: str = "Avaliar API"
    APP_VERSION: str = "0.1.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # =============================================================================
    # PATH SETTINGS
    # =============================================================================
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    REACT_BUILD_DIR: Path = BASE_DIR / "front/build/client"
    PDF_OUTPUT_DIR: Path = BASE_DIR / "static/pdfs"
    TEMP_PDF_DIR: Path = BASE_DIR / "static/pdfs/temp"
    LATEX_SOURCES_DIR: Path = BASE_DIR / "static/latex_sources"
    
    # =============================================================================
    # CACHE & CLEANUP SETTINGS
    # =============================================================================
    TEMP_PDF_TTL_MINUTES: int = 30
    CLEANUP_INTERVAL_MINUTES: int = 10
    MAX_TEMP_PDFS: int = 100
    TEMP_PDF_PREFIX: str = "temp_"
    
    # =============================================================================
    # UPLOAD SETTINGS
    # =============================================================================
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB em bytes
    
    # =============================================================================
    # CORS SETTINGS
    # =============================================================================
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Converte CORS_ORIGINS string em lista"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def cors_methods_list(self) -> list[str]:
        """Converte CORS_ALLOW_METHODS string em lista"""
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",")]
    
    @property
    def cors_headers_list(self) -> list[str]:
        """Converte CORS_ALLOW_HEADERS string em lista"""
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",")]
    
    # =============================================================================
    # LATEX COMPILATION SETTINGS
    # =============================================================================
    LATEX_TIMEOUT_SECONDS: int = 30
    LATEX_COMPILE_RUNS: int = 2
    
    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    DATABASE_URL: str = "postgresql://avaliador:passwd@localhost:5432/avaliar"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_ECHO: bool = False  # Set to True for SQL logging in development

    # =============================================================================
    # MIGRATION SETTINGS
    # =============================================================================
    ALEMBIC_DATABASE_URL: str = DATABASE_URL

    # =============================================================================
    # JWT / AUTH SETTINGS
    # =============================================================================
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_TOKEN_LOCATION: list[str] = ["headers"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOGIN_PIN: str = "123456"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar campos extras do .env


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância singleton das configurações
    
    Returns:
        Settings: Configurações da aplicação
    """
    return Settings()


# Instância global de settings
settings = get_settings()


def init_directories():
    """
    Cria os diretórios necessários para a aplicação
    """
    settings.PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    settings.TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)
    settings.LATEX_SOURCES_DIR.mkdir(parents=True, exist_ok=True)


# Inicializar diretórios ao importar o módulo
init_directories()
