# etl/common/db.py
# Pool de conexões e operações de banco de dados
# Upserts idempotentes e transações seguras

import logging
from typing import Dict, List, Any, Optional, Union
from contextlib import contextmanager
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
import psycopg2.extras
from datetime import datetime, timezone

from .config import load_database_config, DatabaseConfig

# =============================================================================
# CLASSE PRINCIPAL DE CONEXÃO
# =============================================================================

class DatabaseManager:
    """Gerenciador de conexões e operações de banco de dados"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or load_database_config()
        self.logger = logging.getLogger(f"{__name__}.DatabaseManager")
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        
    @property
    def engine(self) -> Engine:
        """Lazy initialization do engine SQLAlchemy"""
        if self._engine is None:
            self._engine = create_engine(
                self.config.url,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                echo=self.config.echo,
                pool_pre_ping=True,  # Validar conexões antes do uso
                pool_recycle=3600    # Reciclar conexões a cada hora
            )
            self.logger.info("Database engine initialized")
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Factory para criar sessões"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory
    
    @contextmanager
    def get_session(self):
        """Context manager para sessões com auto-rollback em erro"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Testa conectividade com o banco"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                self.logger.info("Database connection test successful")
                return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False

# =============================================================================
# OPERAÇÕES UPSERT GENÉRICAS
# =============================================================================

def upsert_dataframe(
    df: pd.DataFrame,
    table_name: str,
    schema: str,
    unique_columns: List[str],
    db_manager: DatabaseManager,
    update_columns: Optional[List[str]] = None,
    chunk_size: int = 1000
) -> int:
    """
    Upsert de DataFrame com ON CONFLICT DO UPDATE
    
    Args:
        df: DataFrame com os dados
        table_name: Nome da tabela
        schema: Schema da tabela  
        unique_columns: Colunas que formam a chave única
        db_manager: Instance do DatabaseManager
        update_columns: Colunas a serem atualizadas (se None, usa todas exceto unique_columns)
        chunk_size: Tamanho dos chunks para inserção
        
    Returns:
        Número de linhas afetadas
    """
    
    if df.empty:
        logging.getLogger(__name__).warning(f"DataFrame vazio para {schema}.{table_name}")
        return 0
        
    logger = logging.getLogger(__name__)
    total_rows = 0
    
    # Preparar colunas para update
    if update_columns is None:
        update_columns = [col for col in df.columns if col not in unique_columns]
    
    # Adicionar load_ts se não existir
    if 'load_ts' not in df.columns:
        df['load_ts'] = datetime.now(timezone.utc)
    
    try:
        with db_manager.get_session() as session:
            # Processar em chunks para grandes volumes
            for chunk_start in range(0, len(df), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(df))
                chunk_df = df.iloc[chunk_start:chunk_end]
                
                # Converter para lista de dicts
                records = chunk_df.to_dict(orient='records')
                
                # Construir query de upsert
                placeholders = ', '.join([f":{col}" for col in chunk_df.columns])
                conflict_cols = ', '.join(unique_columns)
                
                update_clauses = []
                for col in update_columns:
                    if col != 'load_ts':  # Sempre atualizar load_ts
                        update_clauses.append(f"{col} = EXCLUDED.{col}")
                    else:
                        update_clauses.append(f"{col} = CURRENT_TIMESTAMP")
                
                update_clause = ', '.join(update_clauses)
                
                query = f"""
                INSERT INTO {schema}.{table_name} ({', '.join(chunk_df.columns)})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_cols}) DO UPDATE SET
                {update_clause}
                """
                
                result = session.execute(text(query), records)
                chunk_rows = result.rowcount
                total_rows += chunk_rows
                
                logger.debug(f"Upserted chunk {chunk_start}-{chunk_end}: {chunk_rows} rows")
        
        logger.info(f"Successfully upserted {total_rows} rows to {schema}.{table_name}")
        return total_rows
        
    except Exception as e:
        logger.error(f"Error upserting to {schema}.{table_name}: {e}")
        raise

# =============================================================================
# OPERAÇÕES DE CONSULTA
# =============================================================================

def fetch_dataframe(
    query: str,
    db_manager: DatabaseManager,
    params: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Executa query e retorna DataFrame
    
    Args:
        query: SQL query
        db_manager: Instance do DatabaseManager
        params: Parâmetros da query
        
    Returns:
        DataFrame com os resultados
    """
    logger = logging.getLogger(__name__)
    
    try:
        with db_manager.engine.connect() as conn:
            df = pd.read_sql(query, conn, params=params)
            logger.debug(f"Fetched {len(df)} rows")
            return df
            
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

def get_max_load_timestamp(
    table_name: str,
    schema: str,
    db_manager: DatabaseManager,
    timestamp_column: str = 'load_ts'
) -> Optional[datetime]:
    """
    Obtém o último timestamp de carregamento de uma tabela
    
    Args:
        table_name: Nome da tabela
        schema: Schema da tabela
        db_manager: Instance do DatabaseManager
        timestamp_column: Nome da coluna de timestamp
        
    Returns:
        Último timestamp ou None se tabela vazia
    """
    query = f"""
    SELECT MAX({timestamp_column}) as max_ts 
    FROM {schema}.{table_name}
    """
    
    try:
        df = fetch_dataframe(query, db_manager)
        max_ts = df.iloc[0]['max_ts']
        return max_ts if pd.notna(max_ts) else None
        
    except Exception:
        # Tabela pode não existir ainda
        return None

# =============================================================================
# OPERAÇÕES DE LIMPEZA E MANUTENÇÃO
# =============================================================================

def cleanup_old_data(
    table_name: str,
    schema: str,
    db_manager: DatabaseManager,
    retention_days: int,
    timestamp_column: str = 'load_ts'
) -> int:
    """
    Remove dados antigos baseado em retention policy
    
    Args:
        table_name: Nome da tabela
        schema: Schema da tabela
        db_manager: Instance do DatabaseManager
        retention_days: Dias de retenção
        timestamp_column: Coluna de timestamp para filtro
        
    Returns:
        Número de linhas removidas
    """
    logger = logging.getLogger(__name__)
    
    query = f"""
    DELETE FROM {schema}.{table_name}
    WHERE {timestamp_column} < CURRENT_DATE - INTERVAL '{retention_days} days'
    """
    
    try:
        with db_manager.get_session() as session:
            result = session.execute(text(query))
            rows_deleted = result.rowcount
            
            if rows_deleted > 0:
                logger.info(f"Cleaned up {rows_deleted} old rows from {schema}.{table_name}")
            
            return rows_deleted
            
    except Exception as e:
        logger.error(f"Error cleaning up {schema}.{table_name}: {e}")
        raise

def vacuum_analyze_table(
    table_name: str,
    schema: str,
    db_manager: DatabaseManager
) -> None:
    """
    Executa VACUUM ANALYZE em uma tabela para otimização
    
    Args:
        table_name: Nome da tabela
        schema: Schema da tabela
        db_manager: Instance do DatabaseManager
    """
    logger = logging.getLogger(__name__)
    
    try:
        # VACUUM precisa ser executado fora de transação
        with db_manager.engine.connect() as conn:
            conn.execute(text("COMMIT"))  # Finalizar qualquer transação pendente
            conn.execute(text(f"VACUUM ANALYZE {schema}.{table_name}"))
            
        logger.info(f"VACUUM ANALYZE completed for {schema}.{table_name}")
        
    except Exception as e:
        logger.warning(f"Error running VACUUM ANALYZE on {schema}.{table_name}: {e}")

# =============================================================================
# UTILITÁRIOS
# =============================================================================

def get_table_row_count(
    table_name: str,
    schema: str,
    db_manager: DatabaseManager
) -> int:
    """Retorna número de linhas em uma tabela"""
    query = f"SELECT COUNT(*) as row_count FROM {schema}.{table_name}"
    df = fetch_dataframe(query, db_manager)
    return int(df.iloc[0]['row_count'])

def table_exists(
    table_name: str,
    schema: str,
    db_manager: DatabaseManager
) -> bool:
    """Verifica se tabela existe"""
    query = """
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = :schema 
        AND table_name = :table_name
    ) as table_exists
    """
    
    try:
        df = fetch_dataframe(query, db_manager, {'schema': schema, 'table_name': table_name})
        return bool(df.iloc[0]['table_exists'])
    except Exception:
        return False