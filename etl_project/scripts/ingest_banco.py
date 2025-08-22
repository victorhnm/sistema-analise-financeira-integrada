# etl_project/scripts/ingest_banco.py

import pandas as pd
from utils.db_connection import get_db_connection

def ingest_banco_transacional(filepath: str):
    """
    Lê um arquivo JSON simulando uma extração de banco transacional 
    e o insere em uma tabela de staging.
    """
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        df = pd.read_json(filepath)
        print(f"Lidos {len(df)} registros do arquivo JSON do banco transacional.")

        cursor.execute("TRUNCATE TABLE stg_banco_transacional;")
        print("Tabela stg_banco_transacional limpa.")

        for index, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO stg_banco_transacional (id_venda, data_venda, id_produto, quantidade, valor_unitario, cliente_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (row['id_venda'], row['data_venda'], row['id_produto'], row['quantidade'], row['valor_unitario'], row['cliente_id'])
            )
        
        conn.commit()
        print(f"{len(df)} registros inseridos com sucesso na stg_banco_transacional.")

    except Exception as e:
        print(f"Erro ao ingerir dados do banco transacional: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("Conexão com o PostgreSQL fechada.")

if __name__ == '__main__':
    json_file_path = 'sources_data/banco_transacional.json'
    ingest_banco_transacional(json_file_path)