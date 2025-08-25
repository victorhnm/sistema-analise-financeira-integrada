# api/db.py
# Database manager para API FastAPI
# Conexões read-only e queries otimizadas

import logging
import os
from typing import Dict, List, Any, Optional
import asyncio
import asyncpg
from datetime import datetime, date
import json

# =============================================================================
# CONFIGURAÇÃO E CONEXÃO
# =============================================================================

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manager de banco de dados para API (read-only)"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self._pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(f"{__name__}.DatabaseManager")
    
    async def _ensure_pool(self):
        """Garantir que connection pool está inicializado"""
        if self._pool is None or self._pool._closed:
            self._pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=5,
                command_timeout=30,
                server_settings={
                    'application_name': 'integrated_financial_api'
                }
            )
            self.logger.info("Database connection pool created")
    
    async def close(self):
        """Fechar connection pool"""
        if self._pool:
            await self._pool.close()
            self.logger.info("Database connection pool closed")
    
    async def test_connection(self) -> bool:
        """Testar conectividade"""
        try:
            await self._ensure_pool()
            async with self._pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False
    
    async def get_table_count(self, schema: str, table: str) -> int:
        """Obter contagem de registros de uma tabela"""
        try:
            await self._ensure_pool()
            query = f"SELECT COUNT(*) FROM {schema}.{table}"
            async with self._pool.acquire() as conn:
                count = await conn.fetchval(query)
                return count or 0
        except Exception as e:
            self.logger.error(f"Error getting count for {schema}.{table}: {e}")
            return 0

# =============================================================================
# QUERIES DE EMPRESAS
# =============================================================================

    async def get_companies(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        page_size: int = 100,
        order_by: str = "company_name",
        order_dir: str = "asc"
    ) -> Dict[str, Any]:
        """Obter lista de empresas com filtros"""
        
        await self._ensure_pool()
        
        # Construir WHERE clause
        where_conditions = ["1=1"]
        params = []
        param_counter = 1
        
        if 'ticker' in filters:
            where_conditions.append(f"ticker = ${param_counter}")
            params.append(filters['ticker'])
            param_counter += 1
        
        if 'sector' in filters:
            where_conditions.append(f"sector = ${param_counter}")
            params.append(filters['sector'])
            param_counter += 1
        
        if 'country' in filters:
            where_conditions.append(f"country = ${param_counter}")
            params.append(filters['country'])
            param_counter += 1
        
        if 'search' in filters:
            where_conditions.append(f"company_name ILIKE ${param_counter}")
            params.append(filters['search'])
            param_counter += 1
        
        if 'is_active' in filters:
            where_conditions.append(f"is_active = ${param_counter}")
            params.append(filters['is_active'])
            param_counter += 1
        
        where_clause = " AND ".join(where_conditions)
        
        # Query principal
        base_query = f"""
        SELECT 
            company_id,
            cik,
            ticker,
            company_name,
            sector,
            country,
            currency,
            is_active,
            created_ts,
            updated_ts
        FROM core.dim_company
        WHERE {where_clause}
        ORDER BY {order_by} {order_dir.upper()}
        LIMIT ${param_counter} OFFSET ${param_counter + 1}
        """
        
        # Query de contagem
        count_query = f"""
        SELECT COUNT(*) 
        FROM core.dim_company
        WHERE {where_clause}
        """
        
        try:
            async with self._pool.acquire() as conn:
                # Executar queries em paralelo
                count_task = conn.fetchval(count_query, *params)
                data_task = conn.fetch(
                    base_query, 
                    *params, 
                    page_size, 
                    (page - 1) * page_size
                )
                
                total_count, rows = await asyncio.gather(count_task, data_task)
                
                # Converter resultados
                companies = []
                for row in rows:
                    companies.append({
                        'company_id': row['company_id'],
                        'cik': row['cik'],
                        'ticker': row['ticker'],
                        'company_name': row['company_name'],
                        'sector': row['sector'],
                        'country': row['country'],
                        'currency': row['currency'],
                        'is_active': row['is_active'],
                        'created_ts': row['created_ts'],
                        'updated_ts': row['updated_ts']
                    })
                
                return {
                    'companies': companies,
                    'total_count': total_count
                }
                
        except Exception as e:
            self.logger.error(f"Error in get_companies: {e}")
            raise

# =============================================================================
# QUERIES DE FATOS FINANCEIROS
# =============================================================================

    async def get_financial_facts(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        page_size: int = 100,
        order_by: str = "period_end",
        order_dir: str = "desc"
    ) -> Dict[str, Any]:
        """Obter fatos financeiros com filtros"""
        
        await self._ensure_pool()
        
        # Base query with joins
        base_from = """
        FROM core.fact_statement_line fsl
        JOIN core.dim_company dc ON fsl.company_id = dc.company_id
        """
        
        # Construir WHERE clause
        where_conditions = ["1=1"]
        params = []
        param_counter = 1
        
        if 'ticker' in filters:
            where_conditions.append(f"dc.ticker = ${param_counter}")
            params.append(filters['ticker'])
            param_counter += 1
        
        if 'company_id' in filters:
            where_conditions.append(f"fsl.company_id = ${param_counter}")
            params.append(filters['company_id'])
            param_counter += 1
        
        if 'period_start' in filters:
            where_conditions.append(f"fsl.period_end >= ${param_counter}")
            params.append(filters['period_start'])
            param_counter += 1
        
        if 'period_end' in filters:
            where_conditions.append(f"fsl.period_end <= ${param_counter}")
            params.append(filters['period_end'])
            param_counter += 1
        
        if 'fiscal_year' in filters:
            where_conditions.append(f"fsl.fiscal_year = ${param_counter}")
            params.append(filters['fiscal_year'])
            param_counter += 1
        
        if 'fiscal_period' in filters:
            where_conditions.append(f"fsl.fiscal_period = ${param_counter}")
            params.append(filters['fiscal_period'])
            param_counter += 1
        
        if 'statement' in filters:
            where_conditions.append(f"fsl.statement = ${param_counter}")
            params.append(filters['statement'])
            param_counter += 1
        
        if 'canonical_metric' in filters:
            where_conditions.append(f"fsl.canonical_metric = ${param_counter}")
            params.append(filters['canonical_metric'])
            param_counter += 1
        
        if 'form' in filters:
            where_conditions.append(f"fsl.form = ${param_counter}")
            params.append(filters['form'])
            param_counter += 1
        
        if 'exclude_restated' in filters and filters['exclude_restated']:
            where_conditions.append("fsl.is_restated = false")
        
        if 'min_value' in filters:
            where_conditions.append(f"ABS(fsl.value_converted) >= ${param_counter}")
            params.append(filters['min_value'])
            param_counter += 1
        
        if 'max_value' in filters:
            where_conditions.append(f"ABS(fsl.value_converted) <= ${param_counter}")
            params.append(filters['max_value'])
            param_counter += 1
        
        # Adicionar filtro para dados válidos
        where_conditions.append("fsl.value_converted IS NOT NULL")
        where_conditions.append("fsl.canonical_metric IS NOT NULL")
        
        where_clause = " AND ".join(where_conditions)
        
        # Query principal
        main_query = f"""
        SELECT 
            fsl.company_id,
            dc.ticker,
            dc.company_name,
            fsl.concept,
            fsl.canonical_metric,
            fsl.statement,
            fsl.period_start,
            fsl.period_end,
            fsl.fiscal_year,
            fsl.fiscal_period,
            fsl.form,
            fsl.value_native,
            fsl.value_converted as value_usd,
            fsl.currency_from as currency_native,
            fsl.unit,
            fsl.is_restated
        {base_from}
        WHERE {where_clause}
        ORDER BY fsl.{order_by} {order_dir.upper()}, dc.ticker
        LIMIT ${param_counter} OFFSET ${param_counter + 1}
        """
        
        # Query de contagem
        count_query = f"""
        SELECT COUNT(*) 
        {base_from}
        WHERE {where_clause}
        """
        
        # Query de agregações
        agg_query = f"""
        SELECT 
            COUNT(*) as total_facts,
            COUNT(DISTINCT fsl.company_id) as unique_companies,
            COUNT(DISTINCT fsl.canonical_metric) as unique_metrics,
            MIN(fsl.period_end) as earliest_period,
            MAX(fsl.period_end) as latest_period,
            SUM(CASE WHEN fsl.value_converted > 0 THEN 1 ELSE 0 END) as positive_values,
            SUM(CASE WHEN fsl.is_restated THEN 1 ELSE 0 END) as restated_facts
        {base_from}
        WHERE {where_clause}
        """
        
        try:
            async with self._pool.acquire() as conn:
                # Executar queries
                count_task = conn.fetchval(count_query, *params)
                data_task = conn.fetch(
                    main_query, 
                    *params, 
                    page_size, 
                    (page - 1) * page_size
                )
                agg_task = conn.fetchrow(agg_query, *params)
                
                total_count, rows, agg_row = await asyncio.gather(
                    count_task, data_task, agg_task
                )
                
                # Converter resultados
                facts = []
                for row in rows:
                    facts.append({
                        'company_id': row['company_id'],
                        'ticker': row['ticker'],
                        'company_name': row['company_name'],
                        'concept': row['concept'],
                        'canonical_metric': row['canonical_metric'],
                        'statement_type': row['statement'],
                        'period_start': row['period_start'],
                        'period_end': row['period_end'],
                        'fiscal_year': row['fiscal_year'],
                        'fiscal_period': row['fiscal_period'],
                        'form': row['form'],
                        'value_native': float(row['value_native']) if row['value_native'] else None,
                        'value_usd': float(row['value_usd']) if row['value_usd'] else None,
                        'currency_native': row['currency_native'],
                        'unit': row['unit'],
                        'is_restated': row['is_restated']
                    })
                
                # Agregações
                aggregations = dict(agg_row) if agg_row else {}
                
                return {
                    'facts': facts,
                    'total_count': total_count,
                    'aggregations': aggregations
                }
                
        except Exception as e:
            self.logger.error(f"Error in get_financial_facts: {e}")
            raise

# =============================================================================
# QUERIES TTM
# =============================================================================

    async def get_ttm_metrics(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        page_size: int = 100,
        order_by: str = "revenue_ttm",
        order_dir: str = "desc"
    ) -> Dict[str, Any]:
        """Obter métricas TTM com filtros"""
        
        await self._ensure_pool()
        
        # Base query
        base_from = """
        FROM marts.fact_financials_ttm ttm
        JOIN core.dim_company dc ON ttm.company_id = dc.company_id
        """
        
        # Construir WHERE clause
        where_conditions = ["1=1"]
        params = []
        param_counter = 1
        
        if 'ticker' in filters:
            where_conditions.append(f"ttm.ticker = ${param_counter}")
            params.append(filters['ticker'])
            param_counter += 1
        
        if 'company_id' in filters:
            where_conditions.append(f"ttm.company_id = ${param_counter}")
            params.append(filters['company_id'])
            param_counter += 1
        
        if 'sector' in filters:
            where_conditions.append(f"ttm.sector = ${param_counter}")
            params.append(filters['sector'])
            param_counter += 1
        
        if 'as_of_date' in filters:
            where_conditions.append(f"ttm.as_of_date = ${param_counter}")
            params.append(filters['as_of_date'])
            param_counter += 1
        
        if 'latest_only' in filters and filters['latest_only']:
            where_conditions.append("""
                ttm.as_of_date = (
                    SELECT MAX(as_of_date) 
                    FROM marts.fact_financials_ttm ttm2 
                    WHERE ttm2.company_id = ttm.company_id
                )
            """)
        
        if 'min_revenue_ttm' in filters:
            where_conditions.append(f"ttm.revenue_ttm >= ${param_counter}")
            params.append(filters['min_revenue_ttm'])
            param_counter += 1
        
        # Filtrar apenas dados com receita válida
        where_conditions.append("ttm.revenue_ttm IS NOT NULL AND ttm.revenue_ttm > 0")
        
        where_clause = " AND ".join(where_conditions)
        
        # Query principal
        main_query = f"""
        SELECT 
            ttm.company_id,
            ttm.ticker,
            ttm.company_name,
            ttm.sector,
            ttm.as_of_date,
            ttm.revenue_ttm,
            ttm.net_income_ttm,
            ttm.operating_income_ttm,
            ttm.ebitda_ttm,
            ttm.free_cash_flow_ttm,
            ttm.gross_margin,
            ttm.operating_margin,
            ttm.net_margin,
            ttm.roe,
            ttm.roa,
            ttm.debt_to_equity,
            ttm.current_ratio,
            ttm.revenue_growth_yoy,
            ttm.net_income_growth_yoy,
            ttm.days_sales_outstanding,
            ttm.days_inventory_outstanding,
            ttm.days_payable_outstanding
        {base_from}
        WHERE {where_clause}
        ORDER BY ttm.{order_by} {order_dir.upper()} NULLS LAST, ttm.ticker
        LIMIT ${param_counter} OFFSET ${param_counter + 1}
        """
        
        # Query de contagem
        count_query = f"""
        SELECT COUNT(*) 
        {base_from}
        WHERE {where_clause}
        """
        
        # Query de estatísticas
        stats_query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT ttm.company_id) as unique_companies,
            AVG(ttm.revenue_ttm) as avg_revenue_ttm,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ttm.revenue_ttm) as median_revenue_ttm,
            AVG(ttm.roe) as avg_roe,
            AVG(ttm.roa) as avg_roa,
            AVG(ttm.debt_to_equity) as avg_debt_to_equity,
            AVG(ttm.revenue_growth_yoy) as avg_revenue_growth
        {base_from}
        WHERE {where_clause}
        """
        
        try:
            async with self._pool.acquire() as conn:
                # Executar queries
                count_task = conn.fetchval(count_query, *params)
                data_task = conn.fetch(
                    main_query, 
                    *params, 
                    page_size, 
                    (page - 1) * page_size
                )
                stats_task = conn.fetchrow(stats_query, *params)
                
                total_count, rows, stats_row = await asyncio.gather(
                    count_task, data_task, stats_task
                )
                
                # Converter resultados
                metrics = []
                for row in rows:
                    metrics.append({
                        'company_id': row['company_id'],
                        'ticker': row['ticker'],
                        'company_name': row['company_name'],
                        'sector': row['sector'],
                        'as_of_date': row['as_of_date'],
                        'revenue_ttm': float(row['revenue_ttm']) if row['revenue_ttm'] else None,
                        'net_income_ttm': float(row['net_income_ttm']) if row['net_income_ttm'] else None,
                        'operating_income_ttm': float(row['operating_income_ttm']) if row['operating_income_ttm'] else None,
                        'ebitda_ttm': float(row['ebitda_ttm']) if row['ebitda_ttm'] else None,
                        'free_cash_flow_ttm': float(row['free_cash_flow_ttm']) if row['free_cash_flow_ttm'] else None,
                        'gross_margin': float(row['gross_margin']) if row['gross_margin'] else None,
                        'operating_margin': float(row['operating_margin']) if row['operating_margin'] else None,
                        'net_margin': float(row['net_margin']) if row['net_margin'] else None,
                        'roe': float(row['roe']) if row['roe'] else None,
                        'roa': float(row['roa']) if row['roa'] else None,
                        'debt_to_equity': float(row['debt_to_equity']) if row['debt_to_equity'] else None,
                        'current_ratio': float(row['current_ratio']) if row['current_ratio'] else None,
                        'revenue_growth_yoy': float(row['revenue_growth_yoy']) if row['revenue_growth_yoy'] else None,
                        'net_income_growth_yoy': float(row['net_income_growth_yoy']) if row['net_income_growth_yoy'] else None,
                        'days_sales_outstanding': float(row['days_sales_outstanding']) if row['days_sales_outstanding'] else None,
                        'days_inventory_outstanding': float(row['days_inventory_outstanding']) if row['days_inventory_outstanding'] else None,
                        'days_payable_outstanding': float(row['days_payable_outstanding']) if row['days_payable_outstanding'] else None
                    })
                
                # Estatísticas resumo
                summary_stats = {}
                if stats_row:
                    summary_stats = {
                        'total_records': stats_row['total_records'],
                        'unique_companies': stats_row['unique_companies'],
                        'avg_revenue_ttm': float(stats_row['avg_revenue_ttm']) if stats_row['avg_revenue_ttm'] else None,
                        'median_revenue_ttm': float(stats_row['median_revenue_ttm']) if stats_row['median_revenue_ttm'] else None,
                        'avg_roe': float(stats_row['avg_roe']) if stats_row['avg_roe'] else None,
                        'avg_roa': float(stats_row['avg_roa']) if stats_row['avg_roa'] else None,
                        'avg_debt_to_equity': float(stats_row['avg_debt_to_equity']) if stats_row['avg_debt_to_equity'] else None,
                        'avg_revenue_growth': float(stats_row['avg_revenue_growth']) if stats_row['avg_revenue_growth'] else None
                    }
                
                return {
                    'metrics': metrics,
                    'total_count': total_count,
                    'summary_stats': summary_stats
                }
                
        except Exception as e:
            self.logger.error(f"Error in get_ttm_metrics: {e}")
            raise

# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

_database_manager: Optional[DatabaseManager] = None

async def get_database() -> DatabaseManager:
    """Dependency para obter database manager"""
    global _database_manager
    
    if _database_manager is None:
        _database_manager = DatabaseManager()
    
    return _database_manager

async def close_database():
    """Fechar conexões do banco"""
    global _database_manager
    
    if _database_manager:
        await _database_manager.close()
        _database_manager = None