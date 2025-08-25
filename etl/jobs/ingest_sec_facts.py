# etl/jobs/ingest_sec_facts.py
# Job para ingerir company facts XBRL da SEC
# Processamento incremental por CIK, período e statement

import asyncio
import logging
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, date, timedelta

from ..common.db import DatabaseManager, upsert_dataframe, get_max_load_timestamp
from ..common.config import load_database_config, load_etl_config, setup_logging
from ..sources.sec_client import SecClient
from ..parsers.sec_xbrl_parser import SecXbrlParser, parsed_facts_to_dataframe

# =============================================================================
# JOB PRINCIPAL
# =============================================================================

class SecFactsIngestJob:
    """Job de ingestão de fatos financeiros da SEC"""
    
    def __init__(self):
        self.db_config = load_database_config()
        self.etl_config = load_etl_config()
        self.db_manager = DatabaseManager(self.db_config)
        self.parser = SecXbrlParser()
        
        self.logger = setup_logging(self.etl_config.log_level)
        self.logger.name = f"{__name__}.SecFactsIngestJob"
    
    async def run(
        self,
        ciks: Optional[List[str]] = None,
        full_refresh: bool = False,
        max_companies: int = 10
    ) -> Dict[str, Any]:
        """
        Executar job de ingestão de fatos financeiros
        
        Args:
            ciks: Lista específica de CIKs. Se None, busca da staging.companies
            full_refresh: Se True, reprocessar todos os dados
            max_companies: Máximo de empresas a processar
            
        Returns:
            Dict com estatísticas de execução
        """
        start_time = datetime.now(timezone.utc)
        stats = {
            'start_time': start_time,
            'companies_processed': 0,
            'facts_ingested': 0,
            'facts_parsed': 0,
            'errors': 0,
            'error_details': [],
            'processing_mode': 'full_refresh' if full_refresh else 'incremental'
        }
        
        try:
            self.logger.info(f"Starting SEC facts ingestion job (mode: {stats['processing_mode']})")
            
            # Testar conectividade
            if not self.db_manager.test_connection():
                raise Exception("Database connection failed")
            
            # Obter lista de empresas alvo
            target_ciks = await self._get_target_ciks(ciks, max_companies)
            self.logger.info(f"Target CIKs: {len(target_ciks)}")
            
            if not target_ciks:
                self.logger.warning("No CIKs to process")
                return stats
            
            # Determinar estratégia incremental
            incremental_cutoff = None
            if not full_refresh and self.etl_config.enable_incremental:
                incremental_cutoff = await self._get_incremental_cutoff()
                if incremental_cutoff:
                    self.logger.info(f"Incremental mode: processing data after {incremental_cutoff}")
            
            # Processar CIKs em paralelo (com limite)
            max_concurrent = min(self.etl_config.max_workers, 3)  # Rate limiting
            semaphore = asyncio.Semaphore(max_concurrent)
            
            tasks = []
            for cik in target_ciks:
                task = self._process_single_company(cik, incremental_cutoff, semaphore)
                tasks.append(task)
            
            # Executar e coletar resultados
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Agregar estatísticas
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Task exception: {result}")
                    stats['errors'] += 1
                    stats['error_details'].append(str(result))
                elif isinstance(result, dict):
                    stats['companies_processed'] += result.get('companies_processed', 0)
                    stats['facts_ingested'] += result.get('facts_ingested', 0)
                    stats['facts_parsed'] += result.get('facts_parsed', 0)
                    stats['errors'] += result.get('errors', 0)
                    stats['error_details'].extend(result.get('error_details', []))
            
            # Estatísticas finais
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            stats.update({
                'end_time': end_time,
                'duration_seconds': duration,
                'success': True,
                'throughput_facts_per_second': stats['facts_ingested'] / duration if duration > 0 else 0
            })
            
            self.logger.info(f"SEC facts ingestion completed: {stats['companies_processed']} companies, "
                           f"{stats['facts_ingested']} facts in {duration:.1f}s "
                           f"({stats['throughput_facts_per_second']:.1f} facts/sec)")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"SEC facts ingestion job failed: {e}")
            stats.update({
                'success': False,
                'error': str(e),
                'end_time': datetime.now(timezone.utc)
            })
            return stats
    
    async def _get_target_ciks(
        self,
        provided_ciks: Optional[List[str]],
        max_companies: int
    ) -> List[str]:
        """Obter lista de CIKs alvo para processamento"""
        
        if provided_ciks:
            # CIKs específicos fornecidos
            ciks = [cik.zfill(10) for cik in provided_ciks]
            self.logger.info(f"Using provided CIKs: {ciks}")
            return ciks[:max_companies]
        
        # Buscar CIKs da tabela staging.companies
        query = """
        SELECT cik 
        FROM staging.companies 
        WHERE is_active = true 
        ORDER BY 
            CASE 
                WHEN ticker IN ('AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA') THEN 1
                ELSE 2 
            END,
            company_name
        LIMIT %s
        """
        
        try:
            from ..common.db import fetch_dataframe
            df = fetch_dataframe(query, self.db_manager, params=(max_companies,))
            
            if df.empty:
                self.logger.warning("No companies found in staging.companies")
                return []
            
            ciks = df['cik'].tolist()
            self.logger.info(f"Retrieved {len(ciks)} CIKs from staging.companies")
            return ciks
            
        except Exception as e:
            self.logger.error(f"Error retrieving CIKs from database: {e}")
            return []
    
    async def _get_incremental_cutoff(self) -> Optional[datetime]:
        """Determinar cutoff para processamento incremental"""
        
        try:
            # Buscar último timestamp de load da tabela raw
            last_load = get_max_load_timestamp('sec_company_facts', 'raw', self.db_manager)
            
            if last_load:
                # Processar dados das últimas 7 dias para garantir completude
                cutoff = last_load - timedelta(days=7)
                return cutoff
            else:
                self.logger.info("No previous data found, running full refresh")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error determining incremental cutoff: {e}")
            return None
    
    async def _process_single_company(
        self,
        cik: str,
        incremental_cutoff: Optional[datetime],
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Processar uma empresa individual"""
        
        company_stats = {
            'companies_processed': 0,
            'facts_ingested': 0,
            'facts_parsed': 0,
            'errors': 0,
            'error_details': []
        }
        
        async with semaphore:
            try:
                self.logger.info(f"Processing company facts for CIK {cik}")
                
                # Verificar se precisa processar (modo incremental)
                if incremental_cutoff:
                    should_process = await self._should_process_company(cik, incremental_cutoff)
                    if not should_process:
                        self.logger.debug(f"Skipping CIK {cik} - no updates needed")
                        return company_stats
                
                # Obter company facts da SEC
                async with SecClient() as sec_client:
                    raw_facts = await sec_client.get_company_facts(cik)
                
                if not raw_facts:
                    self.logger.warning(f"No company facts found for CIK {cik}")
                    return company_stats
                
                # Salvar dados brutos
                await self._save_raw_facts(cik, raw_facts)
                
                # Parse dos dados
                parse_result = self.parser.parse_company_facts(raw_facts)
                
                if parse_result.parsing_errors:
                    self.logger.warning(f"Parsing errors for CIK {cik}: {len(parse_result.parsing_errors)} errors")
                
                # Converter para DataFrame e salvar
                if parse_result.facts:
                    facts_df = parsed_facts_to_dataframe(parse_result.facts)
                    await self._save_parsed_facts(facts_df)
                    
                    company_stats['facts_parsed'] = len(parse_result.facts)
                    company_stats['facts_ingested'] = len(facts_df)
                
                company_stats['companies_processed'] = 1
                
                self.logger.info(f"Completed CIK {cik}: {company_stats['facts_parsed']} facts parsed")
                
            except Exception as e:
                error_msg = f"Error processing CIK {cik}: {e}"
                self.logger.error(error_msg)
                company_stats['errors'] = 1
                company_stats['error_details'].append(error_msg)
        
        return company_stats
    
    async def _should_process_company(
        self,
        cik: str,
        incremental_cutoff: datetime
    ) -> bool:
        """Verificar se empresa precisa ser processada (modo incremental)"""
        
        try:
            query = """
            SELECT load_ts 
            FROM raw.sec_company_facts 
            WHERE cik = %s 
            ORDER BY load_ts DESC 
            LIMIT 1
            """
            
            from ..common.db import fetch_dataframe
            df = fetch_dataframe(query, self.db_manager, params=(cik,))
            
            if df.empty:
                return True  # Nunca processado
            
            last_processed = df.iloc[0]['load_ts']
            return last_processed < incremental_cutoff
            
        except Exception:
            return True  # Em caso de erro, processar
    
    async def _save_raw_facts(self, cik: str, raw_facts: Dict[str, Any]) -> None:
        """Salvar dados brutos na tabela raw.sec_company_facts"""
        
        # Determinar filing date (aproximação baseada nos facts)
        filing_date = None
        try:
            # Tentar extrair data mais recente dos facts
            facts_data = raw_facts.get('facts', {})
            latest_date = None
            
            for taxonomy in facts_data.values():
                for concept_data in taxonomy.values():
                    units = concept_data.get('units', {})
                    for unit_facts in units.values():
                        if isinstance(unit_facts, list):
                            for fact in unit_facts:
                                filed_str = fact.get('filed')
                                if filed_str:
                                    try:
                                        fact_date = datetime.strptime(filed_str, '%Y-%m-%d').date()
                                        if latest_date is None or fact_date > latest_date:
                                            latest_date = fact_date
                                    except ValueError:
                                        continue
            
            filing_date = latest_date
            
        except Exception as e:
            self.logger.debug(f"Error extracting filing date for CIK {cik}: {e}")
        
        # Preparar registro
        record = {
            'cik': cik.zfill(10),
            'raw_data': raw_facts,
            'filing_date': filing_date,
            'load_ts': datetime.now(timezone.utc),
            'source_url': f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
        }
        
        df = pd.DataFrame([record])
        
        # Upsert
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: upsert_dataframe(
                df=df,
                table_name='sec_company_facts',
                schema='raw',
                unique_columns=['cik', 'filing_date'],
                db_manager=self.db_manager,
                chunk_size=1
            )
        )
        
        self.logger.debug(f"Saved raw facts for CIK {cik}")
    
    async def _save_parsed_facts(self, facts_df: pd.DataFrame) -> None:
        """Salvar fatos parseados na tabela staging.financial_facts"""
        
        if facts_df.empty:
            return
        
        # Adicionar load_ts
        facts_df['load_ts'] = datetime.now(timezone.utc)
        
        # Mapear colunas para schema staging
        staging_df = facts_df.rename(columns={
            'company_name': 'entity_name',  # Se necessário
        })
        
        # Selecionar apenas colunas que existem no schema
        expected_columns = [
            'cik', 'concept', 'taxonomy', 'unit', 'period_start', 'period_end',
            'fiscal_year', 'fiscal_period', 'form', 'value', 'is_restated', 'load_ts'
        ]
        
        available_columns = [col for col in expected_columns if col in staging_df.columns]
        staging_df = staging_df[available_columns]
        
        # Upsert em chunks
        chunk_size = self.etl_config.chunk_size
        
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: upsert_dataframe(
                df=staging_df,
                table_name='financial_facts',
                schema='staging',
                unique_columns=['cik', 'concept', 'period_end', 'form', 'unit'],
                db_manager=self.db_manager,
                chunk_size=chunk_size
            )
        )
        
        self.logger.debug(f"Saved {len(staging_df)} parsed facts to staging")

# =============================================================================
# CLI E EXECUÇÃO
# =============================================================================

async def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest SEC company facts')
    parser.add_argument('--ciks', nargs='+', help='Specific CIKs to process')
    parser.add_argument('--full-refresh', action='store_true', help='Full refresh (ignore incremental)')
    parser.add_argument('--max-companies', type=int, default=10, help='Maximum companies to process')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging("INFO")
    logger = logging.getLogger(__name__)
    
    try:
        job = SecFactsIngestJob()
        stats = await job.run(
            ciks=args.ciks,
            full_refresh=args.full_refresh,
            max_companies=args.max_companies
        )
        
        if stats['success']:
            logger.info(f"Job completed successfully: {stats}")
            
            # Log estatísticas detalhadas
            logger.info(f"Processing Summary:")
            logger.info(f"  - Companies: {stats['companies_processed']}")
            logger.info(f"  - Facts Ingested: {stats['facts_ingested']}")
            logger.info(f"  - Facts Parsed: {stats['facts_parsed']}")
            logger.info(f"  - Duration: {stats['duration_seconds']:.1f}s")
            logger.info(f"  - Throughput: {stats['throughput_facts_per_second']:.1f} facts/sec")
            
            if stats['errors'] > 0:
                logger.warning(f"Completed with {stats['errors']} errors")
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