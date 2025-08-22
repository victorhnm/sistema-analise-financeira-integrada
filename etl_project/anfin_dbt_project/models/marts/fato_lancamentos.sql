-- anfin_dbt_project/models/marts/fato_lancamentos.sql

with 
    
-- Primeiro, selecionamos a fonte principal de lançamentos, que é o nosso ERP
lancamentos_erp as (
    select * from {{ source('anfin_staging', 'stg_erp_lancamentos') }}
),

-- CORREÇÃO AQUI: Referenciamos nossas dimensões usando a função ref()
-- Isso cria o gráfico de dependências (lineage) no dbt
dim_contas as (
    select * from {{ ref('dim_contas') }}
),

dim_centros_custo as (
    select * from {{ ref('dim_centros_custo') }}
),

dim_tempo as (
    select * from {{ ref('dim_tempo') }}
)

-- A query final que fará a junção de tudo
select
    -- Chaves Surrogadas (SKs) das dimensões
    dt.sk_tempo,
    dc.sk_conta,
    dcc.sk_centro_custo,
    
    -- Métricas (os fatos)
    le.valor,
    
    -- Campos descritivos (para facilitar a análise)
    le.detalhes as descricao,
    'ERP' as origem_dados

from lancamentos_erp as le

-- CORREÇÃO AQUI: Fazemos o JOIN usando a função ref() também
left join dim_tempo as dt on le.data = dt.data
left join dim_contas as dc on le.conta = dc.id_conta_origem
left join dim_centros_custo as dcc on le.centro_custo_id = dcc.id_cc_origem