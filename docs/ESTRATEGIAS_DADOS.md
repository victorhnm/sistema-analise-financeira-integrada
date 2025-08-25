# Estrategias de Dados
## Backfill, Incrementais e Reclassificacoes

### Versao: 1.0
### Data: 2024-12-XX

## 1. Visao Geral

Este documento descreve as estrategias implementadas para lidar com:
- **Backfill:** Carregamento historico de dados
- **Incrementais:** Atualizacoes diarias/semanais
- **Reclassificacoes:** Correcoes e restatements

## 2. Estrategia de Backfill

### 2.1 Definicao e Escopo
**Backfill** refere-se ao processo de carregamento inicial ou preenchimento de lacunas historicas nos dados financeiros.

**Cenarios Tipicos:**
- Setup inicial de nova empresa no sistema
- Recuperacao apos falhas prolongadas de ETL  
- Extensao do historico para analises de longo prazo
- Mudancas na estrutura de dados que requerem reprocessamento

### 2.2 Implementacao Tecnica

#### Script Principal: `etl/backfill_historical.py`

```python
# Exemplo de execucao
python etl/backfill_historical.py \
    --symbol AAPL \
    --start_date 2018-01-01 \
    --end_date 2023-12-31 \
    --batch_size 4 \
    --delay_seconds 1
```

**Parametros:**
- `symbol`: Ticker da empresa
- `start_date`: Data inicial para backfill  
- `end_date`: Data final (default: hoje)
- `batch_size`: Trimestres por batch (default: 4)
- `delay_seconds`: Pausa entre requests para evitar rate limiting

#### Processo Step-by-Step:

1. **Identificacao de Gaps**
   ```sql
   -- Query para identificar trimestres faltantes
   SELECT DISTINCT 
       fiscal_year,
       fiscal_quarter
   FROM generate_series('2018-01-01'::date, '2023-12-31'::date, '3 months') AS quarters
   LEFT JOIN raw.financials_raw USING (fiscal_year, fiscal_quarter)
   WHERE raw.financials_raw.fiscal_year IS NULL;
   ```

2. **Extracao por Batches**
   - Processa 4 trimestres (1 ano) por vez
   - Implementa exponential backoff para retry
   - Logs detalhados para cada batch processado

3. **Validacao e Load**
   - Verifica integridade dos dados extraidos
   - Carrega em raw.financials_raw
   - Triggera dbt para reprocessar marts

#### Monitoramento e Logs:
```
[INFO] Iniciando backfill para AAPL: 2018-2023
[INFO] Identificados 24 trimestres para processar  
[INFO] Batch 1/6: Processando 2018Q1-2019Q4
[WARN] Rate limit detectado, aguardando 30s...
[INFO] Batch 1/6 concluido: 4 trimestres carregados
[INFO] Backfill completo: 24/24 trimestres processados
```

### 2.3 Tratamento de Edge Cases

#### Empresas com Historico Limitado:
- IPOs recentes: Buscar apenas desde data de listagem
- Empresas privadas: Dados limitados disponiveis
- M&A: Considerar historico da empresa adquirida

#### Dados Indisponiveis:
```python
# Exemplo de handling para dados missing
if response.status_code == 404:
    logger.warning(f"Dados nao disponiveis para {symbol} {period}")
    # Registra gap mas nao interrompe processo
    continue
```

## 3. Estrategia Incremental

### 3.1 Definicao e Frequencia
**Atualizacoes incrementais** capturam apenas dados novos ou alterados desde a ultima execucao.

**Scheduling:**
- **Diario:** Verificacao de novos filings SEC
- **Semanal:** Reprocessamento completo de metricas TTM
- **Mensal:** Validacao e reconciliacao completa

### 3.2 Implementacao Tecnica

#### Water Mark Strategy:
```python
# Ultimo timestamp processado
last_processed = get_last_watermark('sec_extractions')

# Query apenas para dados mais recentes
new_filings = sec_api.get_filings_since(last_processed)

# Atualiza watermark apos sucesso
update_watermark('sec_extractions', current_timestamp)
```

#### dbt Incremental Models:
```sql
-- marts/fact_financials_ttm.sql
{{ config(
    materialized='incremental',
    unique_key='ttm_id',
    on_schema_change='fail'
) }}

SELECT * FROM {{ ref('int_ttm_calculations') }}

{% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

### 3.3 Deteccao de Mudancas

#### CDC (Change Data Capture):
- **Trigger-based:** Captura changes em raw.financials_raw
- **Log-based:** Monitora WAL do PostgreSQL para mudancas
- **Query-based:** Compara checksums entre execucoes

#### Exemplo de CDC Trigger:
```sql
CREATE TRIGGER financials_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON raw.financials_raw
    FOR EACH ROW EXECUTE FUNCTION audit_changes();
```

## 4. Tratamento de Reclassificacoes

### 4.1 Definicao e Impacto
**Reclassificacoes** ocorrem quando empresas:
- Corrigem erros em filings anteriores
- Mudam criterios contabeis (GAAP/IFRS)
- Ajustam devido a M&A ou spin-offs
- Respondem a auditorias da SEC

### 4.2 Deteccao Automatica

#### Compare & Alert:
```python
def detect_restatements(company_id, fiscal_period):
    """
    Compara valores atuais com historicos para
    detectar possíveis reclassificacoes
    """
    current_values = get_current_financials(company_id, fiscal_period)
    historical_values = get_historical_financials(company_id, fiscal_period)
    
    variance_threshold = 0.05  # 5% 
    
    for metric in ['revenue', 'net_income', 'total_assets']:
        variance = abs(current_values[metric] - historical_values[metric]) / historical_values[metric]
        
        if variance > variance_threshold:
            alert_restatement(company_id, fiscal_period, metric, variance)
```

#### Flags de Qualidade:
```sql
-- Adicionar flags em fact tables
ALTER TABLE marts.fact_financials_quarterly 
ADD COLUMN is_restated BOOLEAN DEFAULT FALSE,
ADD COLUMN restatement_date TIMESTAMP,
ADD COLUMN restatement_reason TEXT;
```

### 4.3 Processo de Correcao

#### Workflow de Reclassificacao:
1. **Deteccao:** Sistema identifica discrepancia
2. **Validacao:** Analista confirma se é restatement legitimo
3. **Backup:** Preserva valores originais para auditoria
4. **Correcao:** Atualiza registros com novos valores
5. **Reprocessamento:** Recalcula metricas derivadas (TTM, ratios)
6. **Notificacao:** Alerta usuarios sobre mudancas

#### Versionamento de Dados:
```sql
-- Tabela de versionamento para auditoria
CREATE TABLE raw.financials_versions (
    version_id SERIAL PRIMARY KEY,
    company_id INTEGER,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    data_snapshot JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    reason TEXT
);
```

## 5. Performance e Otimizacao

### 5.1 Paralelizacao

#### Concurrent Processing:
```python
import concurrent.futures

def process_companies_parallel(company_list, max_workers=5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_company = {
            executor.submit(process_company_incremental, company): company 
            for company in company_list
        }
        
        for future in concurrent.futures.as_completed(future_to_company):
            company = future_to_company[future]
            try:
                result = future.result()
                logger.info(f"Completed {company}: {result}")
            except Exception as exc:
                logger.error(f"Company {company} failed: {exc}")
```

### 5.2 Caching Strategy

#### Redis para Metadata:
```python
# Cache dos ultimos timestamps processados
redis_client.set(f"watermark:{company_id}", last_processed_timestamp)

# Cache de exchange rates para conversao de moedas  
redis_client.setex(f"fx_rate:EUR:USD:{date}", 3600, exchange_rate)
```

### 5.3 Particionamento de Dados

#### Particionamento Temporal:
```sql
-- Particionar fact tables por ano
CREATE TABLE marts.fact_financials_quarterly_2024 
PARTITION OF marts.fact_financials_quarterly
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

## 6. Monitoramento e Alertas

### 6.1 Metricas de Saude

#### Dashboard de ETL:
- **Data Freshness:** Tempo desde ultima atualizacao
- **Gap Detection:** Trimestres faltantes por empresa
- **Error Rate:** Percentual de falhas nas extrações
- **Processing Time:** Duracao de cada batch/incremental

#### Exemplo de Query para Monitoring:
```sql
-- Empresas com dados desatualizados (> 90 dias)
SELECT 
    c.company_name,
    MAX(f.period_end_date) as last_data,
    CURRENT_DATE - MAX(f.period_end_date) as days_stale
FROM marts.fact_financials_quarterly f
JOIN core.dim_company c USING (company_id)
WHERE c.is_active = true
GROUP BY c.company_id, c.company_name
HAVING CURRENT_DATE - MAX(f.period_end_date) > INTERVAL '90 days'
ORDER BY days_stale DESC;
```

### 6.2 Alertas Automaticos

#### Slack Integration:
```python
def send_data_quality_alert(issue_type, details):
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    payload = {
        "text": f"[DATA QUALITY] {issue_type}",
        "attachments": [{
            "color": "warning",
            "fields": [
                {"title": "Issue", "value": issue_type, "short": True},
                {"title": "Details", "value": details, "short": False}
            ]
        }]
    }
    
    requests.post(slack_webhook, json=payload)
```

## 7. Disaster Recovery

### 7.1 Backup Strategy

#### Automated Backups:
- **Daily:** Incremental backup das tabelas marts
- **Weekly:** Full backup completo
- **Monthly:** Archive para cold storage (S3 Glacier)

#### Recovery Procedures:
```bash
# Restore de backup especifico
pg_restore --clean --no-acl --no-owner \
    --host=$SUPABASE_HOST \
    --dbname=$SUPABASE_DB \
    backup_marts_2024_01_15.dump
```

### 7.2 Rollback Procedures

#### Data Rollback:
```python
def rollback_to_checkpoint(checkpoint_date):
    """
    Rollback dos dados para um checkpoint especifico
    """
    # 1. Backup estado atual
    create_emergency_backup()
    
    # 2. Restaurar tabelas para checkpoint
    restore_from_checkpoint(checkpoint_date)
    
    # 3. Reprocessar incrementais desde checkpoint
    reprocess_since(checkpoint_date)
    
    # 4. Validar integridade
    run_data_quality_checks()
```

## 8. Troubleshooting Common Issues

### 8.1 Rate Limiting

**Sintoma:** HTTP 429 responses from SEC API  
**Solucao:** Implementar exponential backoff com jitter
```python
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff: 2^attempt + random jitter  
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)
```

### 8.2 Data Inconsistencies

**Sintoma:** Ratios calculados fora de ranges esperados  
**Solucao:** Implementar data quality rules
```sql
-- Rule: Current ratio nao pode ser negativo
INSERT INTO data_quality_failures 
SELECT company_id, 'current_ratio_negative', current_ratio
FROM marts.fact_financials_ttm 
WHERE current_ratio < 0;
```

### 8.3 Memory Issues

**Sintoma:** Out of memory errors durante backfill  
**Solucao:** Reduzir batch size e implementar chunking
```python
def process_in_chunks(data_list, chunk_size=100):
    for i in range(0, len(data_list), chunk_size):
        chunk = data_list[i:i + chunk_size]
        process_chunk(chunk)
        # Force garbage collection
        gc.collect()
```

## 9. Roadmap e Melhorias Futuras

### 9.1 Near-term (3 meses)
- [ ] Implementar CDC com Debezium
- [ ] Setup alertas proativos via PagerDuty
- [ ] Otimizar queries com materialized views
- [ ] Implementar data lineage tracking

### 9.2 Medium-term (6 meses)  
- [ ] Stream processing com Apache Kafka
- [ ] Machine learning para deteccao de anomalias
- [ ] Auto-scaling baseado em volume de dados
- [ ] Multi-region disaster recovery

### 9.3 Long-term (12+ meses)
- [ ] Real-time data pipeline
- [ ] Advanced data governance com Apache Atlas
- [ ] Zero-downtime deployments
- [ ] Federated queries across multiple sources

---

**Nota:** Este documento deve ser revisado trimestralmente para garantir que as estrategias permanecem alinhadas com o crescimento do volume de dados e requisitos de performance.