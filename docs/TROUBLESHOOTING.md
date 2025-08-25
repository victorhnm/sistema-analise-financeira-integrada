# 🔧 Troubleshooting Guide
# Integrated Financial Analysis - Soluções para Problemas Comuns

## 🗂️ Índice

- [🔌 Conectividade de Banco](#-conectividade-de-banco)
- [🔄 Pipeline ETL](#-pipeline-etl)  
- [🏗️ dbt Issues](#️-dbt-issues)
- [🌐 API FastAPI](#-api-fastapi)
- [📊 Power BI](#-power-bi)
- [⚙️ GitHub Actions](#️-github-actions)
- [🛡️ Security & Rate Limiting](#️-security--rate-limiting)
- [📈 Performance](#-performance)

---

## 🔌 Conectividade de Banco

### ❌ "Could not connect to server" / "Connection timeout"

**Sintomas:**
```
psycopg2.OperationalError: could not connect to server: Connection timed out
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
```

**Soluções:**

1. **Verificar URL de conexão:**
```bash
# Verificar formato da DATABASE_URL
echo $DATABASE_URL
# Deve ser: postgresql://postgres:senha@projeto.supabase.co:5432/postgres

# Testar conexão direta
psql "postgresql://postgres:senha@projeto.supabase.co:5432/postgres"
```

2. **Configuração SSL:**
```python
# Em .env, adicionar parâmetros SSL
DATABASE_URL=postgresql://postgres:senha@projeto.supabase.co:5432/postgres?sslmode=require

# Em dbt profiles.yml
sslmode: require
```

3. **Firewall corporativo:**
```bash
# Testar conectividade de rede
telnet projeto.supabase.co 5432
nc -zv projeto.supabase.co 5432

# Se bloqueado, usar proxy ou VPN
```

4. **Pool de conexões esgotado:**
```python
# Reduzir pool_size em config.py
DB_POOL_SIZE=2
DB_MAX_OVERFLOW=5

# Ou definir variável de ambiente
export DB_POOL_SIZE=2
```

### ❌ "Invalid password" / "Authentication failed"

**Soluções:**

1. **Verificar credenciais no Supabase:**
   - Settings → Database → Reset database password
   - Aguardar 2-3 minutos para propagação
   - Atualizar todas as configurações (.env, profiles.yml, secrets)

2. **Caracteres especiais na senha:**
```bash
# URL encode de caracteres especiais
# @ → %40, # → %23, & → %26, + → %2B

# Exemplo:
# senha: P@ssw0rd#123
# encoded: P%40ssw0rd%23123
DATABASE_URL=postgresql://postgres:P%40ssw0rd%23123@projeto.supabase.co:5432/postgres
```

---

## 🔄 Pipeline ETL

### ❌ "SEC rate limit exceeded" / HTTP 429

**Sintomas:**
```
aiohttp.client_exceptions.ClientResponseError: 429, message='Too Many Requests'
SEC EDGAR API rate limit exceeded
```

**Soluções:**

1. **Verificar User-Agent:**
```bash
# User-Agent deve seguir formato exato
echo $SEC_USER_AGENT
# Correto: "CompanyName AdminEmail@domain.com"  
# Incorreto: "Python script" ou vazio

# Definir corretamente
export SEC_USER_AGENT="SuaEmpresa contato@seudominio.com"
```

2. **Reduzir rate limiting:**
```bash
# Em .env, reduzir requests por segundo
SEC_RATE_LIMIT_RPS=3.0  # Default: 5.0

# Executar com menos concorrência
python -m etl.main facts --max-companies 3
```

3. **Implementar backoff manual:**
```python
# Se necessário, adicionar delay manual
import time
time.sleep(5)  # Entre chamadas
```

### ❌ "No company facts found" / Empty datasets

**Sintomas:**
```
WARNING: No company facts found for CIK 0000320193
INFO: 0 facts ingested, 0 companies processed
```

**Soluções:**

1. **Verificar CIKs válidos:**
```python
# Testar CIK específico manualmente
import requests
cik = "0000320193"  # Apple
url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
headers = {"User-Agent": "SuaEmpresa contato@domain.com"}
response = requests.get(url, headers=headers)
print(response.status_code, response.json())
```

2. **Usar company tickers oficiais:**
```bash
# Baixar lista oficial da SEC
curl -H "User-Agent: SuaEmpresa contato@domain.com" \
     https://www.sec.gov/files/company_tickers.json > company_tickers.json

# Verificar CIK da empresa
grep -i "apple" company_tickers.json
```

3. **Período de dados:**
```python
# Algumas empresas podem não ter dados recentes
# Verificar se há dados históricos
start_date = '2020-01-01'  # Expandir janela temporal
```

### ❌ "XBRL parsing failed" / Invalid JSON

**Soluções:**

1. **Verificar estrutura JSON:**
```python
# Debug do parser
import json
with open('debug_company_facts.json', 'w') as f:
    json.dump(raw_data, f, indent=2)

# Verificar se há facts → us-gaap
if 'facts' not in raw_data:
    print("No facts in response")
if 'us-gaap' not in raw_data.get('facts', {}):
    print("No US-GAAP data")
```

2. **Fallback para dados mínimos:**
```python
# Em caso de erro, processar conceitos básicos apenas
MINIMAL_CONCEPTS = ['Revenues', 'NetIncomeLoss', 'Assets', 'StockholdersEquity']
```

---

## 🏗️ dbt Issues

### ❌ "Compilation Error" / Model dependencies

**Sintomas:**
```
Compilation Error in model 'fact_financials_ttm'
Model 'staging.stg_companies' depends on a node named 'raw.sec_submissions'
```

**Soluções:**

1. **Verificar sources.yml:**
```yaml
# dbt_project/models/sources.yml
sources:
  - name: raw
    tables:
      - name: sec_company_facts
      - name: sec_submissions  
      - name: fx_rates_raw
```

2. **Executar em ordem correta:**
```bash
# Limpar e reexecutar
dbt clean
dbt deps
dbt seed --full-refresh
dbt run --full-refresh
```

3. **Debug de dependências:**
```bash
# Ver DAG de dependências  
dbt ls --models +fact_financials_ttm
dbt run --models +stg_companies  # Executar upstream primeiro
```

### ❌ "Incremental model failed" / Schema changes

**Sintomas:**
```
Database Error in model 'fact_financials_ttm'
column "new_column" does not exist
```

**Soluções:**

1. **Full refresh do modelo:**
```bash
dbt run --models fact_financials_ttm --full-refresh
```

2. **Schema evolution strategy:**
```sql
-- Em dbt_project.yml
models:
  marts:
    +on_schema_change: 'append_new_columns'  # ou 'fail'
```

3. **Manual schema update:**
```sql
-- Se necessário, alterar schema manualmente
ALTER TABLE marts.fact_financials_ttm ADD COLUMN new_column DECIMAL;
```

### ❌ "Test failures" / Data quality issues

**Sintomas:**
```
FAIL 1 unique_fact_financials_quarterly_company_id_period_end_date
WARN 5 not_null_stg_companies_ticker
```

**Soluções:**

1. **Investigar falhas:**
```bash
# Ver detalhes do teste que falhou
dbt test --models fact_financials_quarterly --store-failures

# Query para investigar duplicatas
SELECT company_id, period_end_date, COUNT(*)  
FROM marts.fact_financials_quarterly
GROUP BY 1,2 HAVING COUNT(*) > 1;
```

2. **Ajustar tolerância de testes:**
```yaml
# schema.yml  
tests:
  - unique:
      config:
        severity: warn  # Em vez de error
        warn_if: ">= 1"
        error_if: ">= 10"
```

---

## 🌐 API FastAPI

### ❌ "Internal Server Error" / 500 errors

**Sintomas:**
```
{"detail":"Internal server error: column \"company_id\" does not exist"}
```

**Soluções:**

1. **Verificar schema do banco:**
```sql
-- Verificar se tabelas existem
\dt core.*
\dt marts.*

-- Verificar colunas específicas
\d+ core.dim_company
\d+ marts.fact_financials_ttm
```

2. **Debug de queries:**
```python
# Ativar SQL logging
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Ou adicionar prints na db.py
print(f"Executing query: {query}")
print(f"With params: {params}")
```

3. **Conectividade da API:**
```bash
# Testar variáveis de ambiente
export DATABASE_URL="postgresql://..."
python -c "
from api.db import DatabaseManager
import asyncio
db = DatabaseManager()
print(asyncio.run(db.test_connection()))
"
```

### ❌ "422 Validation Error" / Pydantic issues

**Soluções:**

1. **Verificar tipos de dados:**
```python
# Em models.py, ajustar validators
@validator('revenue_ttm', pre=True)
def parse_decimal(cls, v):
    if v is None:
        return None
    return float(v) if isinstance(v, Decimal) else v
```

2. **Debug de serialização:**
```python
# Testar endpoint manualmente
curl -X GET "http://localhost:8000/companies?limit=1" -H "accept: application/json"
```

---

## 📊 Power BI

### ❌ "Connection timeout" / Performance issues

**Soluções:**

1. **Usar Import Mode em vez de DirectQuery:**
   - File → Options → DirectQuery → desmarcar
   - Refresh agendado em vez de tempo real
   - Melhor para datasets > 1M rows

2. **Otimizar queries via API:**
```python
# Usar API endpoints com paginação
GET /ttm?latest_only=true&page_size=100
# Em vez de conectar diretamente às tabelas
```

3. **Filtros no source:**
```sql
-- Criar views otimizadas para Power BI
CREATE VIEW bi.vw_ttm_latest AS
SELECT * FROM marts.fact_financials_ttm 
WHERE as_of_date >= CURRENT_DATE - INTERVAL '2 years';
```

### ❌ "DAX calculation errors" / BLANK() results

**Sintomas:**
```
ROE = BLANK() para todas as empresas
Margem Líquida mostrando valores incorretos
```

**Soluções:**

1. **Verificar relationships:**
   - Model → Manage relationships
   - fact_financials_ttm[company_id] → dim_company[company_id]
   - Cross-filter direction: Both ou Single

2. **Debug DAX measures:**
```dax
-- Criar measure de debug
Debug ROE = 
VAR _NetIncome = SUM('fact_financials_ttm'[net_income_ttm])
VAR _Revenue = SUM('fact_financials_ttm'[revenue_ttm])  
VAR _Equity = CALCULATE(AVERAGE('fact_financials_quarterly'[shareholders_equity]))
RETURN 
"NetIncome: " & _NetIncome & " | Revenue: " & _Revenue & " | Equity: " & _Equity
```

3. **Context e filtros:**
```dax
-- Usar KEEPFILTERS se necessário
Receita TTM = 
CALCULATE(
    SUM('fact_financials_ttm'[revenue_ttm]),
    KEEPFILTERS('dim_date'[date_key] = MAX('dim_date'[date_key]))
)
```

---

## ⚙️ GitHub Actions

### ❌ "Workflow failed" / Missing secrets

**Sintomas:**
```
Error: Environment variable DATABASE_URL is not set
SEC_USER_AGENT is required but not found
```

**Soluções:**

1. **Configurar secrets:**
   - Repository → Settings → Secrets and variables → Actions
   - Adicionar todos os secrets necessários:
     - `DATABASE_URL`
     - `SEC_USER_AGENT`
     - `SUPABASE_HOST`, `SUPABASE_PASSWORD`, etc.

2. **Verificar referências:**
```yaml
# Em workflow YAML, usar secrets corretamente
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}  # ✅
  DATABASE_URL: $DATABASE_URL  # ❌ Incorreto
```

3. **Debug de secrets:**
```yaml
# Temporariamente, para debug (remover depois)
- name: Debug Environment
  run: |
    echo "Database URL length: ${#DATABASE_URL}"
    echo "User agent starts with: ${SEC_USER_AGENT:0:10}..."
```

### ❌ "Pipeline hanging" / Timeout issues

**Soluções:**

1. **Timeout configuration:**
```yaml
jobs:
  ingest-companies:
    timeout-minutes: 30  # Default: 360 min
    steps:
      - name: Run ETL
        timeout-minutes: 15
```

2. **Paralelismo e recursos:**
```yaml
strategy:
  matrix:
    source: [companies, fx, facts]
  max-parallel: 2  # Reduzir se necessário
```

---

## 🛡️ Security & Rate Limiting

### ❌ "API key exposed" / Secrets in logs

**Soluções:**

1. **Sanitização de logs:**
```python
# Nunca logar secrets diretamente
logger.info(f"Using database: {database_url}")  # ❌
logger.info(f"Using database: {database_url[:10]}...")  # ✅

# Mascarar API keys
masked_key = api_key[:4] + "***" + api_key[-4:] if api_key else "None"
```

2. **Environment variables:**
```bash
# Verificar se não há secrets em .env commitado
git log --follow -p .env
git rm --cached .env  # Se foi commitado acidentalmente
```

### ❌ "Rate limit exceeded" / IP blocking

**Soluções:**

1. **Implementar jitter:**
```python
import random
delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
await asyncio.sleep(delay)
```

2. **User-Agent rotation (se permitido):**
```python
user_agents = [
    "CompanyA admin@companya.com",
    "CompanyB admin@companyb.com"
]
# Usar alternadamente se múltiplas entities legítimas
```

---

## 📈 Performance

### ❌ "ETL too slow" / Large datasets

**Soluções:**

1. **Paralelismo:**
```python
# Aumentar workers (cuidado com rate limits)
ETL_MAX_WORKERS=3  # Aumentar gradualmente
MAX_CONCURRENT_REQUESTS=2
```

2. **Chunk processing:**
```python
# Processar em chunks menores
CHUNK_SIZE=500
for chunk in chunks(companies, CHUNK_SIZE):
    await process_chunk(chunk)
```

3. **Incremental loading:**
```python
# Processar apenas dados novos
last_load_ts = get_max_load_timestamp('raw', 'sec_company_facts')
process_since = last_load_ts - timedelta(days=7)  # Overlap de 7 dias
```

### ❌ "Database performance" / Slow queries

**Soluções:**

1. **Adicionar índices:**
```sql
-- Índices específicos para queries lentas
CREATE INDEX CONCURRENTLY idx_ttm_company_date 
ON marts.fact_financials_ttm(company_id, as_of_date);

CREATE INDEX CONCURRENTLY idx_facts_period_metric
ON core.fact_statement_line(period_end, canonical_metric) 
WHERE canonical_metric IS NOT NULL;
```

2. **Query optimization:**
```sql
-- Usar EXPLAIN ANALYZE para identificar gargalos
EXPLAIN ANALYZE 
SELECT * FROM marts.fact_financials_ttm 
WHERE company_id = 'uuid-here' 
ORDER BY as_of_date DESC;
```

3. **Connection pooling:**
```python
# Ajustar pool de conexões
POOL_SIZE=10
MAX_OVERFLOW=20
POOL_TIMEOUT=60
```

---

## 🆘 Emergency Procedures

### 🚨 Pipeline crítico falhando

1. **Rollback rápido:**
```bash
# Voltar para último commit funcional
git revert HEAD~1
git push origin main

# Ou executar manualmente sem GitHub Actions
python -m etl.main companies --max-companies 5
dbt run --models marts.fact_financials_ttm
```

2. **Bypass incremental:**
```bash
# Full refresh emergency
dbt run --full-refresh --models marts
python -m etl.main all --full-refresh --max-companies 20
```

### 📞 Contato e Escalação

- **GitHub Issues**: Para bugs reproduzíveis
- **Documentation**: Este arquivo para troubleshooting
- **Community**: Stack Overflow tags: `dbt`, `supabase`, `fastapi`

---

## 📋 Checklist de Troubleshooting

Antes de reportar um bug, verificar:

- [ ] **Connectividade**: `dbt debug` e `python -m etl.main health`
- [ ] **Credenciais**: Secrets configurados e não expirados
- [ ] **Rate limits**: Não excedeu limites da SEC/ECB/FRED
- [ ] **Dependencies**: `pip install -r requirements.txt` e `dbt deps`
- [ ] **Schema**: Tabelas existem e têm dados
- [ ] **Logs**: Verificar logs específicos do erro
- [ ] **Retry**: Tentar novamente após alguns minutos

---

*Última atualização: 2024-08-23*
*Para reportar novos problemas ou sugerir soluções: [GitHub Issues](https://github.com/seu-usuario/integrated-financial-analysis/issues)*