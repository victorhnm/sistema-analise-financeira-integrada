# Instrucoes para Popular o Supabase

## Status: SCRIPT PRONTO - EXECUCAO MANUAL NECESSARIA

Criei o script SQL completo (`populate_supabase.sql`) com 15.610 bytes que vai:

1. Criar todas as tabelas necessárias
2. Inserir dados das 5 empresas (AAPL, MSFT, AMZN, GOOGL, META)  
3. Popular dados financeiros reais do Q4 2023
4. Calcular métricas TTM e ratios
5. Verificar se tudo foi inserido corretamente

## EXECUTE AGORA:

### Opcao 1: SQL Editor (MAIS FACIL)
1. Acesse: https://supabase.com/dashboard/project/otzqqbcxqfpxzzopcxsk/sql
2. Abra o arquivo `populate_supabase.sql` 
3. Copie TODO o conteudo (Ctrl+A, Ctrl+C)
4. Cole no SQL Editor
5. Clique "Run" 

### Opcao 2: Linha de Comando (se tiver psql)
```bash
PGPASSWORD=996744957Vh@ psql \
  -h db.otzqqbcxqfpxzzopcxsk.supabase.co \
  -p 5432 \
  -U postgres \
  -d postgres \
  -f populate_supabase.sql
```

## Verificacao de Sucesso

Após executar, rode essas queries para confirmar:

```sql
-- 1. Contar registros
SELECT 
    'dim_company' as table_name, count(*) as records FROM core.dim_company
UNION ALL
SELECT 'fact_financials_quarterly', count(*) FROM marts.fact_financials_quarterly  
UNION ALL
SELECT 'fact_financials_ttm', count(*) FROM marts.fact_financials_ttm;

-- 2. Ver dados financeiros
SELECT 
    c.ticker,
    c.company_name,
    ROUND(f.revenue / 1000000000.0, 1) as revenue_billions,
    ROUND(ttm.roe * 100, 1) as roe_percent
FROM marts.fact_financials_quarterly f
JOIN core.dim_company c ON f.company_id = c.company_id
JOIN marts.fact_financials_ttm ttm ON f.company_id = ttm.company_id
ORDER BY f.revenue DESC;
```

**Resultado Esperado:**
- dim_company: 5 records  
- fact_financials_quarterly: 5 records
- fact_financials_ttm: 5 records

E você deve ver dados para AMZN (170B), AAPL (119.6B), GOOGL (86.3B), MSFT (62B), META (40.1B).

## Após Popular os Dados

1. **Teste Power BI**: Conecte usando as credenciais e veja se os dados aparecem
2. **Teste API**: Execute `python api/main.py` para testar endpoints
3. **Execute ETL**: Use scripts para buscar mais dados da SEC

## Dados Inseridos

O script insere dados financeiros reais das Big Tech para Q4 2023:

| Empresa | Receita (B) | Lucro (B) | ROE | 
|---------|-------------|-----------|-----|
| AMZN    | 170.0       | 10.6      | 4.7% |
| AAPL    | 119.6       | 33.9      | 45.0% |
| GOOGL   | 86.3        | 20.7      | 6.4% |
| MSFT    | 62.0        | 22.3      | 10.8% |
| META    | 40.1        | 14.0      | 10.1% |

Todos os ratios financeiros (ROE, ROA, D/E, margens, etc.) são calculados automaticamente.

---

**AGUARDANDO:** Execute o script SQL no Supabase para prosseguirmos!