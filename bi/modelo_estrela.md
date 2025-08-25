# Modelo Estrela Lógico - Power BI
# Integrated Financial Analysis

## Diagrama do Modelo Dimensional

```
                    ┌─────────────────┐
                    │   dim_date      │
                    ├─────────────────┤
                    │ date_key (PK)   │
                    │ year            │
                    │ quarter         │
                    │ month           │
                    │ fiscal_year     │
                    │ fiscal_quarter  │
                    │ is_quarter_end  │
                    │ is_year_end     │
                    └─────────────────┘
                             │
                             │
        ┌─────────────────┐  │  ┌─────────────────────┐
        │  dim_company    │  │  │    dim_currency     │
        ├─────────────────┤  │  ├─────────────────────┤
        │ company_id (PK) │  │  │ currency_code (PK)  │
        │ cik             │  │  │ currency_name       │
        │ ticker          │  │  │ currency_symbol     │
        │ company_name    │  │  │ is_active           │
        │ sector          │  │  └─────────────────────┘
        │ country         │  │              │
        │ currency        │  │              │
        │ is_active       │  │              │
        └─────────────────┘  │              │
                 │           │              │
                 │           │              │
                 ▼           ▼              ▼
        ┌─────────────────────────────────────────────────────┐
        │            fact_financials_quarterly                │
        ├─────────────────────────────────────────────────────┤
        │ financial_id (PK)                                   │
        │ company_id (FK) ──► dim_company                     │
        │ period_end_date (FK) ──► dim_date                   │  
        │ currency (FK) ──► dim_currency                      │
        │ fiscal_year                                         │
        │ fiscal_quarter                                      │
        │                                                     │
        │ -- Income Statement Metrics --                      │
        │ revenue                                            │
        │ gross_profit                                       │
        │ operating_income                                   │
        │ net_income                                         │
        │ ebitda                                             │
        │                                                     │
        │ -- Balance Sheet Metrics --                         │
        │ total_assets                                       │
        │ total_liabilities                                  │
        │ shareholders_equity                                │
        │ cash_and_equivalents                               │
        │ total_debt                                         │
        │                                                     │
        │ -- Cash Flow Metrics --                             │
        │ operating_cash_flow                                │
        │ investing_cash_flow                                │
        │ financing_cash_flow                                │
        │ free_cash_flow                                     │
        └─────────────────────────────────────────────────────┘
                             │
                             │
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │             fact_financials_ttm                     │
        ├─────────────────────────────────────────────────────┤
        │ ttm_id (PK)                                         │
        │ company_id (FK) ──► dim_company                     │
        │ as_of_date (FK) ──► dim_date                        │
        │                                                     │
        │ -- TTM Base Metrics --                              │
        │ revenue_ttm                                        │
        │ net_income_ttm                                     │
        │ operating_income_ttm                               │
        │ ebitda_ttm                                         │
        │ free_cash_flow_ttm                                 │
        │                                                     │
        │ -- Calculated Ratios --                             │
        │ gross_margin                                       │
        │ operating_margin                                   │
        │ net_margin                                         │
        │ roe                                                │
        │ roa                                                │
        │ debt_to_equity                                     │
        │ current_ratio                                      │
        │                                                     │
        │ -- Growth Metrics --                                │
        │ revenue_growth_yoy                                 │
        │ net_income_growth_yoy                              │
        └─────────────────────────────────────────────────────┘


    ┌─────────────────┐
    │   dim_sector    │
    ├─────────────────┤
    │ sector_id (PK)  │
    │ sector_name     │
    │ sector_group    │
    │ sic_range       │
    └─────────────────┘
            │
            │
            ▼
    (Relacionamento via dim_company.sector = dim_sector.sector_name)
```

## Relacionamentos do Modelo

### Relacionamentos Principais

1. **fact_financials_quarterly → dim_company**
   - Tipo: Many-to-One
   - Coluna: company_id
   - Cardinalidade: Muitos registros financeiros para uma empresa

2. **fact_financials_quarterly → dim_date**
   - Tipo: Many-to-One  
   - Coluna: period_end_date
   - Cardinalidade: Muitos registros financeiros para uma data

3. **fact_financials_ttm → dim_company**
   - Tipo: Many-to-One
   - Coluna: company_id
   - Cardinalidade: Muitas métricas TTM para uma empresa

4. **fact_financials_ttm → dim_date**
   - Tipo: Many-to-One
   - Coluna: as_of_date
   - Cardinalidade: Muitas métricas TTM para uma data

5. **dim_company → dim_sector** (implícito)
   - Tipo: Many-to-One
   - Coluna: sector (texto)
   - Relacionamento por compatibilidade de valores

6. **dim_company → dim_currency** (implícito)
   - Tipo: Many-to-One
   - Coluna: currency
   - Relacionamento para moeda de reporte padrão

### Configurações Recomendadas no Power BI

```
Relacionamentos:
- fact_financials_quarterly[company_id] → dim_company[company_id] (1:N, Single, Both)
- fact_financials_quarterly[period_end_date] → dim_date[date_key] (1:N, Single, Both)
- fact_financials_ttm[company_id] → dim_company[company_id] (1:N, Single, Both)  
- fact_financials_ttm[as_of_date] → dim_date[date_key] (1:N, Single, Both)

Hierarquias:
- Empresa: sector → company_name → ticker
- Temporal: year → quarter → period_end_date
- Geográfica: country → company_name
```

## Grãos dos Fatos

### fact_financials_quarterly
**Grão:** Uma linha por empresa por período fiscal por métrica
- **Chave de negócio:** company_id + period_end_date
- **Atualização:** Trimestral (após earnings releases)
- **Retenção:** Histórico completo desde 2010

### fact_financials_ttm  
**Grão:** Uma linha por empresa por data de referência
- **Chave de negócio:** company_id + as_of_date
- **Atualização:** Diária (recalculado automaticamente)
- **Retenção:** Últimos 5 anos de dados TTM

## Considerações de Performance

### Otimizações Recomendadas

1. **Colunas Calculadas vs Medidas**
   - Usar medidas DAX para cálculos agregados
   - Evitar colunas calculadas em fatos grandes
   - Colunas calculadas apenas em dimensões pequenas

2. **Compressão e Tipos de Dados**
   - Usar INTEGER para chaves onde possível
   - DECIMAL(19,4) para valores monetários
   - DATE para datas (não DATETIME)
   - Categorical encoding para dimensões de texto

3. **Particionamento (se disponível)**
   - Particionar fatos por ano fiscal
   - Manter dimensões não-particionadas

4. **Indexes Sugeridos no Banco**
   ```sql
   -- Índices para melhor performance
   CREATE INDEX idx_quarterly_company_date ON marts.fact_financials_quarterly(company_id, period_end_date);
   CREATE INDEX idx_ttm_company_date ON marts.fact_financials_ttm(company_id, as_of_date);
   CREATE INDEX idx_company_ticker ON core.dim_company(ticker);
   CREATE INDEX idx_company_sector ON core.dim_company(sector);
   ```

## Extensibilidade

### Futuras Dimensões
- **dim_analyst:** Cobertura de analistas e consensos
- **dim_exchange:** Bolsas de valores e horários de trading  
- **dim_taxonomy:** Mapeamento detalhado US-GAAP/IFRS
- **dim_geography:** Hierarquia país → estado → cidade

### Futuros Fatos
- **fact_analyst_estimates:** Estimativas e consensos
- **fact_price_movements:** Preços de ações e volumes
- **fact_peer_comparisons:** Benchmarks setoriais
- **fact_esg_scores:** Métricas ESG e sustentabilidade

## Notas de Implementação

### Tratamento de Dados Ausentes
- **Receita nula:** Excluir do dataset (empresa inativa)
- **Ratios infinitos:** Substituir por NULL em DAX
- **Crescimento YoY:** Requer pelo menos 2 anos de dados
- **Dados preliminares:** Sinalizar com flag is_preliminary

### Conversão de Moedas
- Todas as métricas em USD para comparabilidade
- Taxa FX aplicada na data de fim do período
- Preservar valores originais para auditoria
- Alertas para variações cambiais significativas