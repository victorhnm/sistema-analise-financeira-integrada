# Plano de Testes Manuais
## Integrated Financial Analysis

### Versao: 1.0
### Data: 2024-12-XX

## 1. Objetivo

Este documento estabelece os procedimentos para validacao manual dos componentes principais do sistema de analise financeira integrada, garantindo que todos os requisitos funcionais e nao-funcionais sejam atendidos antes do deployment em producao.

## 2. Escopo dos Testes

### 2.1 Componentes Cobertos
- [x] ETL Pipeline (raw -> core -> marts)
- [x] API FastAPI endpoints  
- [x] Dashboards Power BI
- [x] Integracao Supabase
- [x] Validacao de dados SEC EDGAR

### 2.2 Criterios de Aceite
- Todos os testes devem passar com sucesso
- Tempo de resposta da API < 2 segundos
- Dashboards carregam em < 10 segundos
- Precisao dos calculos TTM >= 99.9%
- Zero dados duplicados ou inconsistentes

## 3. Pre-Requisitos

### 3.1 Ambiente de Teste
- [x] Banco Supabase configurado
- [x] Python 3.11+ com dependencias instaladas
- [x] Power BI Desktop (versao mais recente)
- [x] Credenciais SEC User-Agent validas
- [x] Conexao de internet estavel

### 3.2 Dados de Teste
- [x] Pelo menos 3 empresas com dados historicos (2+ anos)
- [x] Empresas de setores diferentes
- [x] Dados incluindo: AAPL, MSFT, GOOGL (se disponiveis)

## 4. Casos de Teste

### 4.1 ETL Pipeline

#### Teste 4.1.1: Extracao SEC EDGAR
**Objetivo:** Validar extracao correta dos dados financeiros

**Passos:**
1. Executar: `python etl/sec_extractor.py --symbol AAPL --quarters 4`
2. Verificar logs de execucao
3. Conferir dados em raw.financials_raw

**Criterios de Sucesso:**
- [x] Sem erros HTTP ou timeouts
- [x] Dados extraidos correspondem ao esperado no site SEC
- [x] Formato JSON valido
- [x] Metadados corretos (CIK, fiscal dates, etc.)

**Resultado Esperado:**
```
[INFO] Extraindo dados para AAPL...
[INFO] 4 trimestres processados com sucesso
[INFO] 847 registros inseridos em raw.financials_raw
```

#### Teste 4.1.2: Transformacao dbt Core
**Objetivo:** Validar modelos dbt e business rules

**Passos:**
1. Executar: `cd dbt_project && dbt run --models staging`
2. Executar: `dbt run --models marts`
3. Verificar lineage no dbt docs

**Criterios de Sucesso:**
- [x] Todos os modelos compilam sem erro
- [x] Tests de qualidade passam (not_null, unique, etc.)
- [x] Relacionamentos entre tabelas corretos

**Resultado Esperado:**
```
Completed successfully

Done. PASS=45 WARN=0 ERROR=0 SKIP=0 TOTAL=45
```

#### Teste 4.1.3: Calculos TTM
**Objetivo:** Validar precisao dos calculos Trailing Twelve Months

**Passos:**
1. Executar query de validacao:
```sql
SELECT company_id, as_of_date, 
       revenue_ttm, 
       net_income_ttm,
       roe, 
       debt_to_equity
FROM marts.fact_financials_ttm 
WHERE company_id = 1 -- AAPL
ORDER BY as_of_date DESC 
LIMIT 4;
```

2. Comparar com calculos manuais no Excel/Google Sheets

**Criterios de Sucesso:**
- [x] Diferenca <= 0.01% entre calculado e esperado
- [x] Ratios dentro de ranges logicos (ex: ROE entre -50% e 100%)
- [x] Crescimento YoY calculado corretamente

### 4.2 API FastAPI

#### Teste 4.2.1: Endpoints Basicos
**Objetivo:** Validar funcionamento da API REST

**Passos:**
1. Iniciar servidor: `uvicorn api.main:app --reload`
2. Testar endpoints principais:

```bash
# Health check
curl http://localhost:8000/health

# Lista empresas
curl http://localhost:8000/companies

# Metricas especifica empresa
curl http://localhost:8000/companies/AAPL/metrics

# Comparacao setorial  
curl http://localhost:8000/companies/AAPL/peer-comparison
```

**Criterios de Sucesso:**
- [x] Status HTTP 200 para todos os endpoints
- [x] Response time < 2000ms
- [x] JSON valido e bem formatado
- [x] Campos obrigatorios presentes

#### Teste 4.2.2: Filtros e Paginacao
**Objetivo:** Validar parametros de consulta avancados

**Passos:**
1. Testar filtros:
```bash
# Por setor
curl "http://localhost:8000/companies?sector=Technology"

# Por periodo
curl "http://localhost:8000/companies/AAPL/metrics?from=2023-01-01&to=2023-12-31"

# Paginacao
curl "http://localhost:8000/companies?limit=10&offset=20"
```

**Criterios de Sucesso:**
- [x] Filtros aplicados corretamente
- [x] Paginacao funcional
- [x] Metadata de paginacao presente
- [x] Tratamento correto de filtros invalidos

### 4.3 Power BI Dashboard

#### Teste 4.3.1: Conexao Database
**Objetivo:** Validar conectividade com Supabase

**Passos:**
1. Abrir Power BI Desktop
2. Carregar arquivo `/bi/pbip/definition.pbir`
3. Inserir credenciais Supabase quando solicitado
4. Aguardar carregamento das tabelas

**Criterios de Sucesso:**
- [x] Conexao estabelecida sem erros
- [x] Todas as 5 tabelas carregadas (2 facts + 3 dims)
- [x] Relacionamentos automaticos criados
- [x] Preview dos dados correto

#### Teste 4.3.2: Medidas DAX
**Objetivo:** Validar calculos das medidas principais

**Passos:**
1. Criar tabela basica com:
   - Linhas: dim_company[company_name]  
   - Valores: [Receita TTM], [ROE], [Margem Liquida]
2. Aplicar filtro para empresas conhecidas
3. Comparar valores com fonte original

**Criterios de Sucesso:**
- [x] Medidas calculam sem erro
- [x] Valores coerentes com expectativas
- [x] Formatacao adequada (%, milhoes, etc.)
- [x] Performance de calculo aceitavel

#### Teste 4.3.3: Interatividade
**Objetivo:** Validar filtros cruzados e drill-down

**Passos:**
1. Criar dashboard com multiplos visuais:
   - Grafico de barras: Receita por empresa
   - Scatter plot: ROE vs ROA  
   - Slicer: Setor
   - Card: Total empresas
2. Testar interacoes entre visuais

**Criterios de Sucesso:**
- [x] Cross-filtering funciona entre visuais
- [x] Slicers afetam todos os graficos
- [x] Drill-down/up operacional
- [x] Performance visual fluida

### 4.4 Integracao E2E

#### Teste 4.4.1: Pipeline Completo
**Objetivo:** Validar fluxo end-to-end

**Passos:**
1. Executar ETL completo para nova empresa
2. Verificar API retorna novos dados
3. Atualizar Power BI e confirmar novos dados
4. Validar metricas calculadas

**Criterios de Sucesso:**
- [x] Dados fluem corretamente por todas as camadas
- [x] Latencia total < 30 minutos para 1 empresa
- [x] Consistencia entre API e Power BI
- [x] Logs de auditoria gerados

## 5. Testes de Performance

### 5.1 Volume de Dados
**Objetivo:** Validar comportamento com dataset grande

**Teste:**
- Carregar dados para 50+ empresas
- Executar queries complexas
- Medir tempos de resposta

**Expectativas:**
- API: < 5s para queries complexas
- Power BI: < 30s para refresh completo
- ETL: < 2h para carga incremental diaria

### 5.2 Concorrencia
**Objetivo:** Validar comportamento com multiplos usuarios

**Teste:**
- Simular 10 usuarios simultaneos na API
- Abrir multiplas instancias Power BI
- Monitorar performance database

**Expectativas:**
- Sem degradacao significativa performance
- Conexoes database dentro dos limites
- Error rate < 1%

## 6. Testes de Seguranca

### 6.1 Autenticacao API
**Objetivo:** Validar controles de acesso

**Testes:**
- [x] Endpoints protegidos rejeita sem token
- [x] Token invalido retorna 401
- [x] Token expirado renovado automaticamente
- [x] Rate limiting funcional

### 6.2 Conexoes Database
**Objetivo:** Validar seguranca dos dados

**Testes:**
- [x] Conexoes sempre via SSL/TLS
- [x] Credenciais nao expostas em logs
- [x] RLS (Row Level Security) se aplicavel
- [x] Backup e recovery testados

## 7. Checklist Final

### 7.1 Pre-Deployment
- [ ] Todos os casos de teste executados
- [ ] Performance dentro dos parametros
- [ ] Documentacao atualizada
- [ ] Credenciais de producao configuradas
- [ ] Backup strategy validada
- [ ] Monitoring e alertas configurados

### 7.2 Criterios de Go-Live
- [ ] Zero bugs criticos
- [ ] Bugs menores documentados e aceitos
- [ ] Time treinado nos procedimentos
- [ ] Rollback plan testado
- [ ] Support runbook disponivel

## 8. Registro de Execucao

### Teste Executado em: _______________
### Executado por: ___________________
### Ambiente: _______________________

### Resultados:
```
Total Casos de Teste: XX
Passou: XX
Falhou: XX  
Pulado: XX

Bugs Encontrados: XX
- Criticos: XX
- Altos: XX  
- Medios: XX
- Baixos: XX
```

### Observacoes:
_Campo para anotacoes adicionais do testador_

### Aprovacao:
**Testador:** _________________ **Data:** _________
**Tech Lead:** ________________ **Data:** _________
**Product Owner:** _____________ **Data:** _________

---
**Nota:** Este plano deve ser executado em ambiente que replica producao o mais fielmente possivel. Qualquer desvio dos criterios deve ser documentado e aprovado antes do deployment.