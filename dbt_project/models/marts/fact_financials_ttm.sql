-- fact_financials_ttm.sql
-- Marts model: Métricas TTM (Trailing Twelve Months) e ratios
-- Grão: Uma linha por empresa por data de referência (últimos 12 meses)

{{ config(
    materialized='table',
    indexes=[
        {'columns': ['company_id', 'as_of_date'], 'unique': True},
        {'columns': ['ticker', 'as_of_date']},
        {'columns': ['sector', 'as_of_date']}
    ]
) }}

with quarterly_facts as (
    select * from {{ ref('fact_financials_quarterly') }}
),

-- Gerar datas de referência para TTM (fim de cada trimestre)
reporting_dates as (
    select distinct
        company_id,
        ticker,
        company_name,
        sector,
        period_end_date as as_of_date
    from quarterly_facts
    where period_end_date >= current_date - interval '3 years'
),

-- Calcular métricas TTM para cada data de referência
ttm_calculations as (
    select
        rd.company_id,
        rd.ticker,
        rd.company_name,
        rd.sector,
        rd.as_of_date,
        
        -- TTM Income Statement (soma dos últimos 4 trimestres)
        sum(case when qf.period_end_date > rd.as_of_date - interval '12 months' 
                 and qf.period_end_date <= rd.as_of_date
                 then qf.revenue end) as revenue_ttm,
                 
        sum(case when qf.period_end_date > rd.as_of_date - interval '12 months' 
                 and qf.period_end_date <= rd.as_of_date
                 then qf.gross_profit end) as gross_profit_ttm,
                 
        sum(case when qf.period_end_date > rd.as_of_date - interval '12 months' 
                 and qf.period_end_date <= rd.as_of_date
                 then qf.operating_income end) as operating_income_ttm,
                 
        sum(case when qf.period_end_date > rd.as_of_date - interval '12 months' 
                 and qf.period_end_date <= rd.as_of_date
                 then qf.net_income end) as net_income_ttm,
                 
        sum(case when qf.period_end_date > rd.as_of_date - interval '12 months' 
                 and qf.period_end_date <= rd.as_of_date
                 then qf.ebitda end) as ebitda_ttm,
                 
        sum(case when qf.period_end_date > rd.as_of_date - interval '12 months' 
                 and qf.period_end_date <= rd.as_of_date
                 then qf.operating_cash_flow end) as operating_cash_flow_ttm,
                 
        sum(case when qf.period_end_date > rd.as_of_date - interval '12 months' 
                 and qf.period_end_date <= rd.as_of_date
                 then qf.free_cash_flow end) as free_cash_flow_ttm,
        
        -- Balance Sheet (valores mais recentes até a data)
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.total_assets end) as total_assets,
                 
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.shareholders_equity end) as shareholders_equity,
                 
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.total_debt end) as total_debt,
                 
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.current_assets end) as current_assets,
                 
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.current_liabilities end) as current_liabilities,
                 
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.cash_and_equivalents end) as cash_and_equivalents,
                 
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.inventory end) as inventory,
                 
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.accounts_receivable end) as accounts_receivable,
                 
        max(case when qf.period_end_date <= rd.as_of_date
                 then qf.accounts_payable end) as accounts_payable
                 
    from reporting_dates rd
    left join quarterly_facts qf
        on rd.company_id = qf.company_id
    
    group by 1,2,3,4,5
),

-- Calcular métricas YoY (Year over Year)
ttm_with_growth as (
    select
        *,
        
        -- YoY Growth (comparar com TTM de 12 meses antes)
        lag(revenue_ttm, 4) over (partition by company_id order by as_of_date) as revenue_ttm_yoy_lag,
        lag(net_income_ttm, 4) over (partition by company_id order by as_of_date) as net_income_ttm_yoy_lag,
        lag(operating_income_ttm, 4) over (partition by company_id order by as_of_date) as operating_income_ttm_yoy_lag
        
    from ttm_calculations
),

-- Calcular ratios e métricas derivadas finais
final as (
    select
        {{ dbt_utils.generate_surrogate_key(['company_id', 'as_of_date']) }} as ttm_id,
        company_id,
        ticker,
        company_name,
        sector,
        as_of_date,
        
        -- TTM Base Metrics
        revenue_ttm,
        gross_profit_ttm,
        operating_income_ttm,
        net_income_ttm,
        ebitda_ttm,
        operating_cash_flow_ttm,
        free_cash_flow_ttm,
        
        -- Profitability Ratios (como decimais, ex: 0.15 = 15%)
        case when revenue_ttm > 0 
             then gross_profit_ttm / revenue_ttm 
             else null end as gross_margin,
             
        case when revenue_ttm > 0 
             then operating_income_ttm / revenue_ttm 
             else null end as operating_margin,
             
        case when revenue_ttm > 0 
             then net_income_ttm / revenue_ttm 
             else null end as net_margin,
        
        -- Return Ratios
        case when shareholders_equity > 0 
             then net_income_ttm / shareholders_equity 
             else null end as roe,  -- Return on Equity
             
        case when total_assets > 0 
             then net_income_ttm / total_assets 
             else null end as roa,  -- Return on Assets
        
        -- Leverage Ratios
        case when shareholders_equity > 0 
             then total_debt / shareholders_equity 
             else null end as debt_to_equity,
             
        case when current_liabilities > 0 
             then current_assets / current_liabilities 
             else null end as current_ratio,
        
        -- Efficiency Ratios (em dias)
        case when revenue_ttm > 0 
             then (accounts_receivable * 365) / revenue_ttm 
             else null end as days_sales_outstanding,
             
        case when gross_profit_ttm > 0 
             then (inventory * 365) / (revenue_ttm - gross_profit_ttm)
             else null end as days_inventory_outstanding,
             
        case when revenue_ttm > 0 
             then (accounts_payable * 365) / revenue_ttm
             else null end as days_payable_outstanding,
        
        -- Growth YoY (como decimais, ex: 0.10 = 10% growth)
        case when revenue_ttm_yoy_lag > 0 
             then (revenue_ttm / revenue_ttm_yoy_lag) - 1 
             else null end as revenue_growth_yoy,
             
        case when net_income_ttm_yoy_lag > 0 
             then (net_income_ttm / net_income_ttm_yoy_lag) - 1 
             else null end as net_income_growth_yoy,
        
        'USD' as currency,
        current_timestamp as load_ts
        
    from ttm_with_growth
    
    where revenue_ttm is not null  -- Somente períodos com dados válidos
    and as_of_date >= '{{ var("start_date") }}'
)

select * from final