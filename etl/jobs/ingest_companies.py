"""
Job para ingestão de dados de empresas da SEC
"""
import asyncio
import asyncpg
import logging
import json
from common.config import config
from sources.sec_client import SECClient
from parsers.sec_xbrl_parser import SECXBRLParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ingest_companies():
    """Executa ingestão de empresas"""
    logger.info("Iniciando ingestão de empresas...")
    
    # Conectar ao banco
    conn = await asyncpg.connect(
        host=config.database.host,
        port=config.database.port,
        user=config.database.user,
        password=config.database.password,
        database=config.database.database
    )
    
    try:
        # Buscar empresas no banco
        companies = await conn.fetch("""
            SELECT company_id, cik, ticker, company_name
            FROM core.dim_company 
            WHERE is_active = true
            ORDER BY ticker
        """)
        
        sec_client = SECClient()
        parser = SECXBRLParser()
        
        for company in companies:
            cik = company['cik']
            ticker = company['ticker']
            
            logger.info(f"Processando {ticker} (CIK: {cik})")
            
            # Buscar dados da SEC
            company_data = await sec_client.get_company_facts(cik)
            
            if company_data:
                # Salvar dados brutos
                await conn.execute("""
                    INSERT INTO raw.sec_company_facts (cik, company_name, ticker, raw_data)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (cik, file_date) DO UPDATE SET
                        raw_data = EXCLUDED.raw_data,
                        ingested_at = CURRENT_TIMESTAMP
                """, cik, company['company_name'], ticker, json.dumps(company_data))
                
                # Parse fatos financeiros
                facts = parser.parse_company_facts(company_data)
                logger.info(f"Extraídos {len(facts)} fatos para {ticker}")
                
                # Inserir fatos no banco
                if facts:
                    fact_values = []
                    for fact in facts:
                        # Skip facts without required fields
                        if not fact.get('period_end') or not fact.get('fiscal_year'):
                            continue
                            
                        fact_values.append((
                            company['company_id'],  # company_id
                            fact.get('concept', ''),  # concept
                            fact.get('canonical_metric', ''),  # canonical_metric  
                            fact.get('statement', ''),  # statement
                            fact.get('period_start'),  # period_start
                            fact.get('period_end'),  # period_end
                            fact.get('fiscal_year'),  # fiscal_year
                            fact.get('fiscal_period', ''),  # fiscal_period
                            fact.get('form', ''),  # form
                            fact.get('value'),  # value_native
                            fact.get('value'),  # value_converted (same as native for now)
                            fact.get('currency', 'USD'),  # currency_from
                            fact.get('unit', ''),  # unit
                            False  # is_restated
                        ))
                    
                    # Batch insert dos fatos
                    await conn.executemany("""
                        INSERT INTO core.fact_statement_line (
                            company_id, concept, canonical_metric, statement,
                            period_start, period_end, fiscal_year, fiscal_period,
                            form, value_native, value_converted, currency_from,
                            unit, is_restated
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        ON CONFLICT DO NOTHING
                    """, fact_values)
                    
                    logger.info(f"Inseridos {len(fact_values)} fatos para {ticker}")
                
            # Rate limiting
            await asyncio.sleep(0.5)
            
    finally:
        await conn.close()
    
    logger.info("Ingestão concluída!")

if __name__ == "__main__":
    asyncio.run(ingest_companies())
