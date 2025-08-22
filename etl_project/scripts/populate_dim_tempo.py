# etl_project/scripts/populate_dim_tempo.py

import pandas as pd
from datetime import date, timedelta
from utils.db_connection import get_db_connection

def populate_dim_tempo():
    """
    Cria a tabela dim_tempo se ela não existir, e então a popula com dados.
    """
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # --- NOVA ETAPA: Garante que a tabela exista antes de qualquer coisa ---
        print("Verificando e criando a tabela 'dim_tempo' se necessário...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_tempo (
            sk_tempo SERIAL PRIMARY KEY,
            data DATE NOT NULL UNIQUE,
            ano INT NOT NULL,
            mes INT NOT NULL,
            dia INT NOT NULL,
            trimestre INT NOT NULL,
            nome_mes VARCHAR(20) NOT NULL,
            dia_semana VARCHAR(20) NOT NULL
        );
        """)
        conn.commit() # Salva a criação da tabela
        print("Tabela 'dim_tempo' pronta.")
        
        # --- O restante do código continua como antes ---
        start_date = date(2022, 1, 1)
        end_date = date(2025, 12, 31)
        
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append({
                'data': current_date, 'ano': current_date.year, 'mes': current_date.month,
                'dia': current_date.day, 'trimestre': (current_date.month - 1) // 3 + 1,
                'nome_mes': current_date.strftime('%B'), 'dia_semana': current_date.strftime('%A')
            })
            current_date += timedelta(days=1)
        
        df_tempo = pd.DataFrame(dates)

        # Agora o TRUNCATE vai funcionar, pois garantimos que a tabela existe
        cursor.execute("TRUNCATE TABLE dim_tempo RESTART IDENTITY CASCADE;")
        print("Tabela dim_tempo limpa para nova inserção.")

        for index, row in df_tempo.iterrows():
            cursor.execute(
                """
                INSERT INTO dim_tempo (data, ano, mes, dia, trimestre, nome_mes, dia_semana)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (row['data'], row['ano'], row['mes'], row['dia'], row['trimestre'], row['nome_mes'], row['dia_semana'])
            )
        
        conn.commit()
        print(f"{len(df_tempo)} registros inseridos com sucesso na dim_tempo.")

    except Exception as e:
        print(f"Erro ao popular dim_tempo: {e}")
        conn.rollback()
    finally:
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        if conn and not conn.closed:
            conn.close()
            print("Conexão com o PostgreSQL fechada.")

if __name__ == '__main__':
    populate_dim_tempo()