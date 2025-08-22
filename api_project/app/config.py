import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
project_root = Path(__file__).resolve().parent.parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path=dotenv_path)

class Settings:
    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "aurora_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    
    # API
    API_VERSION = "v1"
    API_TITLE = "Análise Financeira Integrada API"
    API_DESCRIPTION = "API para servir dados do Data Warehouse financeiro"
    
    # CORS
    ALLOW_ORIGINS = ["*"]
    ALLOW_CREDENTIALS = True
    ALLOW_METHODS = ["*"]
    ALLOW_HEADERS = ["*"]

settings = Settings()