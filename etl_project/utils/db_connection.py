# etl_project/utils/db_connection.py

import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path # Importamos a biblioteca Path

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados PostgreSQL.
    As credenciais são lidas do arquivo .env que está na pasta raiz do projeto.
    """
    # Construímos o caminho para a pasta raiz do projeto (um nível acima de 'etl_project')
    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path = project_root / '.env'
    
    # Carregamos as variáveis do .env especificando o caminho
    load_dotenv(dotenv_path=dotenv_path)

    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host='localhost',
            port='5432'
        )
        print("Conexão com o PostgreSQL bem-sucedida!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar com o PostgreSQL: {e}")
        return None