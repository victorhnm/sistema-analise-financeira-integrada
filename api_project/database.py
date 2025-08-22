# api_project/database.py
import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados PostgreSQL.
    Lê as credenciais do arquivo .env na pasta raiz do projeto.
    """
    project_root = Path(__file__).resolve().parent.parent
    dotenv_path = project_root / '.env'
    load_dotenv(dotenv_path=dotenv_path)

    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host='localhost',
            port='5432'
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar com o PostgreSQL: {e}")
        return None