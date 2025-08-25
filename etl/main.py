"""
CLI Principal do ETL Pipeline
"""
import click
import asyncio
import logging
import sys
import os

# Add current directory and parent to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import config
from sources.sec_client import SECClient
from jobs.ingest_companies import ingest_companies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Integrated Financial Analysis ETL Pipeline"""
    pass

@cli.command()
def health():
    """Verifica saúde do sistema"""
    async def check():
        # Testar SEC
        sec_client = SECClient()
        sec_ok = await sec_client.test_connection()
        print(f"SEC API: {'OK' if sec_ok else 'FALHA'}")
        
        # Testar banco
        try:
            import asyncpg
            conn = await asyncpg.connect(
                host=config.database.host,
                port=config.database.port,
                user=config.database.user,
                password=config.database.password,
                database=config.database.database
            )
            await conn.execute("SELECT 1")
            await conn.close()
            print("Database: OK")
        except Exception as e:
            print(f"Database: FALHA - {e}")
    
    asyncio.run(check())

@cli.command()
def companies():
    """Ingere dados de empresas"""
    print("Iniciando ingestão de empresas...")
    asyncio.run(ingest_companies())
    print("Ingestão concluída!")

@cli.command()
def all():
    """Executa pipeline completo"""
    print("Executando pipeline completo...")
    asyncio.run(ingest_companies())
    print("Pipeline concluído!")

if __name__ == '__main__':
    cli()
