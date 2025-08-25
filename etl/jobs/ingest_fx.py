# etl/jobs/ingest_fx.py
# Job para ingerir taxas de câmbio de ECB/FRED
# Processamento incremental diário

import asyncio
import logging
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, date, timedelta

from ..common.db import DatabaseManager, upsert_dataframe, get_max_load_timestamp
from ..common.config import load_database_config, load_etl_config, load_fx_config, setup_logging
from ..sources.fx_client import FxClient, normalize_fx_rates

# =============================================================================
# JOB PRINCIPAL
# =============================================================================

class FxIngestJob:
    """Job de ingestão de taxas de câmbio"""
    
    def __init__(self):
        self.db_config = load_database_config()
        self.etl_config = load_etl_config()
        self.fx_config = load_fx_config()
        self.db_manager = DatabaseManager(self.db_config)
        
        self.logger = setup_logging(self.etl_config.log_level)
        self.logger.name = f"{__name__}.FxIngestJob"
    
    async def run(
        self,
        full_refresh: bool = False,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Executar job de ingestão de FX
        
        Args:
            full_refresh: Se True, reprocessar todos os dados
            days_back: Dias históricos a processar (para full refresh)
            
        Returns:
            Dict com estatísticas de execução
        """
        start_time = datetime.now(timezone.utc)
        stats = {
            'start_time': start_time,
            'fx_source': self.fx_config.source,
            'rates_ingested': 0,
            'raw_records_saved': 0,
            'staging_records_saved': 0,
            'errors': 0,
            'error_details': [],
            'processing_mode': 'full_refresh' if full_refresh else 'incremental'
        }
        
        try:
            self.logger.info(f"Starting FX ingestion job (source: {self.fx_config.source}, "
                           f"mode: {stats['processing_mode']})")
            
            # Testar conectividade
            if not self.db_manager.test_connection():
                raise Exception("Database connection failed")
            
            # Determinar período de processamento
            processing_days = await self._determine_processing_period(full_refresh, days_back)
            
            if processing_days <= 0:
                self.logger.info("No FX data to process")
                return stats
            
            self.logger.info(f"Processing FX data for last {processing_days} days")
            
            # Obter dados FX
            async with FxClient(self.fx_config) as fx_client:
                fx_response = await fx_client.get_rates(days_back=processing_days)
            
            if not fx_response.success:
                raise Exception(f"FX API error: {fx_response.error}")
            
            if not fx_response.rates:
                self.logger.warning("No FX rates returned from API")
                return stats
            
            # Salvar dados brutos
            raw_records = await self._save_raw_fx_data(fx_response)
            stats['raw_records_saved'] = raw_records
            
            # Normalizar e expandir taxas (incluir inversas)
            normalized_rates = normalize_fx_rates(fx_response.rates)
            self.logger.info(f"Normalized {len(fx_response.rates)} rates to {len(normalized_rates)} (with inverses)")
            
            # Salvar em staging
            staging_records = await self._save_staging_fx_data(normalized_rates)
            stats['staging_records_saved'] = staging_records
            stats['rates_ingested'] = len(normalized_rates)
            
            # Estatísticas finais
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            stats.update({
                'end_time': end_time,
                'duration_seconds': duration,
                'success': True,
                'processing_days': processing_days
            })
            
            self.logger.info(f"FX ingestion completed: {stats['rates_ingested']} rates "
                           f"from {stats['processing_days']} days in {duration:.1f}s")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"FX ingestion job failed: {e}")
            stats.update({
                'success': False,
                'error': str(e),
                'end_time': datetime.now(timezone.utc)
            })
            return stats
    
    async def _determine_processing_period(
        self,
        full_refresh: bool,
        default_days: int
    ) -> int:
        """Determinar quantos dias processar baseado no modo"""
        
        if full_refresh:
            return default_days
        
        if not self.etl_config.enable_incremental:
            return default_days
        
        try:
            # Buscar última data processada
            last_load = get_max_load_timestamp('fx_rates_raw', 'raw', self.db_manager)
            
            if last_load is None:
                self.logger.info("No previous FX data found, processing full period")
                return default_days
            
            # Calcular dias desde última atualização
            days_since_last = (datetime.now(timezone.utc) - last_load).days
            
            # Processar pelo menos 1 dia, máximo default_days
            processing_days = max(1, min(days_since_last + 2, default_days))  # +2 para overlap
            
            self.logger.info(f"Incremental mode: last update {days_since_last} days ago, "
                           f"processing {processing_days} days")
            
            return processing_days
            
        except Exception as e:
            self.logger.warning(f"Error determining incremental period: {e}")
            return default_days
    
    async def _save_raw_fx_data(self, fx_response) -> int:
        """Salvar dados brutos na tabela raw.fx_rates_raw"""
        
        # Preparar estrutura de dados para raw
        raw_data = {
            'source': fx_response.source,
            'extract_date': fx_response.extract_date.isoformat(),
            'rates_count': len(fx_response.rates),
            'rates': []
        }
        
        # Converter rates para dict serializável
        for rate in fx_response.rates:
            raw_data['rates'].append({
                'rate_date': rate.rate_date.isoformat(),
                'currency_from': rate.currency_from,
                'currency_to': rate.currency_to,
                'rate': rate.rate,
                'source': rate.source
            })
        
        # Preparar registro
        record = {
            'source': fx_response.source,
            'raw_data': raw_data,
            'extract_date': fx_response.extract_date,
            'load_ts': datetime.now(timezone.utc)
        }
        
        df = pd.DataFrame([record])
        
        # Upsert
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: upsert_dataframe(
                df=df,
                table_name='fx_rates_raw',
                schema='raw',
                unique_columns=['source', 'extract_date'],
                db_manager=self.db_manager,
                chunk_size=1
            )
        )
        
        self.logger.debug(f"Saved raw FX data: {len(fx_response.rates)} rates")
        return 1
    
    async def _save_staging_fx_data(self, rates: List) -> int:
        """Salvar taxas normalizadas em staging.fx_rates"""
        
        if not rates:
            return 0
        
        # Converter para DataFrame
        rates_data = []
        for rate in rates:
            rates_data.append({
                'rate_date': rate.rate_date,
                'currency_from': rate.currency_from,
                'currency_to': rate.currency_to,
                'rate': rate.rate,
                'source': rate.source,
                'load_ts': datetime.now(timezone.utc)
            })
        
        df = pd.DataFrame(rates_data)
        
        # Filtrar dados de qualidade
        df = self._apply_fx_quality_filters(df)
        
        if df.empty:
            self.logger.warning("All FX rates filtered out by quality checks")
            return 0
        
        # Upsert em staging
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: upsert_dataframe(
                df=df,
                table_name='fx_rates',
                schema='staging',
                unique_columns=['rate_date', 'currency_from', 'currency_to', 'source'],
                db_manager=self.db_manager,
                chunk_size=self.etl_config.chunk_size
            )
        )
        
        self.logger.info(f"Saved {len(df)} FX rates to staging")
        return len(df)
    
    def _apply_fx_quality_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar filtros de qualidade nas taxas FX"""
        
        initial_count = len(df)
        
        # Filtro 1: Remover rates nulos ou zero
        df = df[(df['rate'].notna()) & (df['rate'] > 0)]
        
        # Filtro 2: Limites de sanidade (0.001 a 1000)
        df = df[(df['rate'] >= 0.001) & (df['rate'] <= 1000)]
        
        # Filtro 3: Datas válidas (não futuras)
        today = date.today()
        df = df[df['rate_date'] <= today]
        
        # Filtro 4: Datas não muito antigas
        cutoff_date = today - timedelta(days=3650)  # 10 anos
        df = df[df['rate_date'] >= cutoff_date]
        
        # Filtro 5: Currencies válidas
        valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'CHF', 'AUD', 'SEK', 'NOK', 'DKK']
        df = df[
            df['currency_from'].isin(valid_currencies) & 
            df['currency_to'].isin(valid_currencies)
        ]
        
        # Filtro 6: Remover conversões iguais (USD->USD com rate != 1.0)
        same_currency = df['currency_from'] == df['currency_to']
        invalid_same = same_currency & (abs(df['rate'] - 1.0) > 0.0001)
        df = df[~invalid_same]
        
        filtered_count = len(df)
        filtered_out = initial_count - filtered_count
        
        if filtered_out > 0:
            self.logger.info(f"Quality filters: kept {filtered_count}/{initial_count} rates "
                           f"({filtered_out} filtered out)")
        
        return df

# =============================================================================
# UTILITÁRIOS ESPECÍFICOS
# =============================================================================

async def validate_fx_data_quality(db_manager: DatabaseManager) -> Dict[str, Any]:
    """Validar qualidade dos dados FX em staging"""
    
    from ..common.db import fetch_dataframe
    
    validation_results = {
        'total_rates': 0,
        'unique_currencies': [],
        'date_range': {},
        'sources': {},
        'quality_issues': []
    }
    
    try:
        # Estatísticas básicas
        basic_stats_query = """
        SELECT 
            COUNT(*) as total_rates,
            COUNT(DISTINCT currency_from || '-' || currency_to) as unique_pairs,
            MIN(rate_date) as min_date,
            MAX(rate_date) as max_date,
            COUNT(DISTINCT source) as sources_count
        FROM staging.fx_rates
        """
        
        stats_df = fetch_dataframe(basic_stats_query, db_manager)
        
        if not stats_df.empty:
            row = stats_df.iloc[0]
            validation_results.update({
                'total_rates': int(row['total_rates']),
                'unique_currency_pairs': int(row['unique_pairs']),
                'date_range': {
                    'min_date': row['min_date'],
                    'max_date': row['max_date']
                },
                'sources_count': int(row['sources_count'])
            })
        
        # Moedas disponíveis
        currencies_query = """
        SELECT DISTINCT currency_from as currency FROM staging.fx_rates
        UNION
        SELECT DISTINCT currency_to as currency FROM staging.fx_rates
        ORDER BY currency
        """
        
        currencies_df = fetch_dataframe(currencies_query, db_manager)
        validation_results['unique_currencies'] = currencies_df['currency'].tolist()
        
        # Distribuição por fonte
        sources_query = """
        SELECT source, COUNT(*) as count
        FROM staging.fx_rates
        GROUP BY source
        ORDER BY count DESC
        """
        
        sources_df = fetch_dataframe(sources_query, db_manager)
        validation_results['sources'] = dict(zip(sources_df['source'], sources_df['count']))
        
        # Verificar problemas de qualidade
        quality_checks = [
            ("Extreme rates (>100 or <0.01)", "SELECT COUNT(*) as count FROM staging.fx_rates WHERE rate > 100 OR rate < 0.01"),
            ("Future dates", f"SELECT COUNT(*) as count FROM staging.fx_rates WHERE rate_date > '{date.today()}'"),
            ("Missing recent data", f"SELECT COUNT(*) as count FROM staging.fx_rates WHERE rate_date >= '{date.today() - timedelta(days=7)}'")
        ]
        
        for check_name, query in quality_checks:
            try:
                check_df = fetch_dataframe(query, db_manager)
                count = int(check_df.iloc[0]['count'])
                
                if check_name == "Missing recent data" and count == 0:
                    validation_results['quality_issues'].append(f"{check_name}: No recent data found")
                elif check_name != "Missing recent data" and count > 0:
                    validation_results['quality_issues'].append(f"{check_name}: {count} records")
                    
            except Exception as e:
                validation_results['quality_issues'].append(f"Error running check '{check_name}': {e}")
        
    except Exception as e:
        validation_results['error'] = str(e)
    
    return validation_results

# =============================================================================
# CLI E EXECUÇÃO
# =============================================================================

async def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest FX rates from ECB/FRED')
    parser.add_argument('--full-refresh', action='store_true', help='Full refresh (ignore incremental)')
    parser.add_argument('--days-back', type=int, default=30, help='Days to fetch (full refresh mode)')
    parser.add_argument('--validate', action='store_true', help='Validate data quality after ingestion')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging("INFO")
    logger = logging.getLogger(__name__)
    
    try:
        job = FxIngestJob()
        stats = await job.run(
            full_refresh=args.full_refresh,
            days_back=args.days_back
        )
        
        if stats['success']:
            logger.info(f"Job completed successfully: {stats}")
            
            # Log estatísticas detalhadas
            logger.info(f"Processing Summary:")
            logger.info(f"  - Source: {stats['fx_source']}")
            logger.info(f"  - Rates Ingested: {stats['rates_ingested']}")
            logger.info(f"  - Processing Days: {stats.get('processing_days', 'N/A')}")
            logger.info(f"  - Duration: {stats['duration_seconds']:.1f}s")
            
            # Validação de qualidade se solicitada
            if args.validate:
                logger.info("Running data quality validation...")
                db_manager = DatabaseManager()
                validation = await validate_fx_data_quality(db_manager)
                
                logger.info(f"Validation Results:")
                logger.info(f"  - Total Rates: {validation['total_rates']}")
                logger.info(f"  - Currencies: {validation['unique_currencies']}")
                logger.info(f"  - Sources: {validation['sources']}")
                
                if validation['quality_issues']:
                    logger.warning(f"Quality Issues: {validation['quality_issues']}")
                else:
                    logger.info("  - No quality issues found")
            
        else:
            logger.error(f"Job failed: {stats}")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))