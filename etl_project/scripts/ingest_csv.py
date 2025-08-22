# etl_project/scripts/ingest_csv.py

import pandas as pd
from utils.db_connection import get_db_connection

def ingest_csv_conciliacao(filepath: str):
    """
    Lê um arquivo CSV de conciliação bancária e o insere em uma tabela de staging.
    """
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        # Lê o arquivo CSV usando Pandas
        df = pd.read_csv(filepath)
        print(f"Lidos {len(df)} registros do arquivo CSV.")

        # Limpa a tabela de staging antes de inserir novos dados
        cursor.execute("TRUNCATE TABLE stg_conciliacao_bancaria;")
        print("Tabela stg_conciliacao_bancaria limpa.")

        # Insere os dados do DataFrame na tabela de staging
        for index, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO stg_conciliacao_bancaria (data, historico, valor, tipo)
                VALUES (%s, %s, %s, %s)
                """,
                (row['data'], row['historico'], row['valor'], row['tipo'])
            )
        
        conn.commit()
        print(f"{len(df)} registros inseridos com sucesso na stg_conciliacao_bancaria.")

    except Exception as e:
        print(f"Erro ao ingerir dados do CSV: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("Conexão com o PostgreSQL fechada.")

if __name__ == '__main__':
    # O caminho para o nosso arquivo de dados simulado
    csv_file_path = 'sources_data/conciliacao_bancaria.csv'
    ingest_csv_conciliacao(csv_file_path)