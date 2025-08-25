"""
Configurações centralizadas do ETL
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    """Configurações do banco de dados"""
    url: str = os.getenv('DATABASE_URL', 'postgresql://victorhnm:@urora12@localhost:5432/aurora_db')
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    user: str = os.getenv('DB_USER', 'victorhnm')
    password: str = os.getenv('DB_PASSWORD', '@urora12')
    database: str = os.getenv('DB_NAME', 'aurora_db')

@dataclass  
class SECConfig:
    """Configurações da SEC EDGAR API"""
    user_agent: str = os.getenv('SEC_USER_AGENT', 'Victor Nascimento victorhnm@gmail.com')
    base_url: str = 'https://data.sec.gov/api/xbrl/companyfacts'

@dataclass
class Config:
    """Configuração principal"""
    def __post_init__(self):
        self.database = DatabaseConfig()
        self.sec = SECConfig()
        
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')

# Instância global
config = Config()
