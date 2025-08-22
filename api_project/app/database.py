import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    @staticmethod
    def get_connection():
        """Cria conexão com o PostgreSQL usando as configurações."""
        try:
            return psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
        except Exception as e:
            logger.error(f"Erro ao conectar no banco: {e}")
            raise

    @staticmethod
    @contextmanager
    def get_db_cursor():
        """Context manager para conexões de banco."""
        conn = None
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            yield cursor
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro na operação do banco: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def execute_query(query: str, params: tuple = None):
        """Executa uma query e retorna os resultados."""
        with DatabaseManager.get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()