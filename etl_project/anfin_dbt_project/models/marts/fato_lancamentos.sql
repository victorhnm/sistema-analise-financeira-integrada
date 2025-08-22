-- anfin_dbt_project/models/marts/fato_lancamentos.sql

with 

-- União de todas as fontes de lançamentos contábeis
lancamentos_consolidados as (
    -- Lançamentos do ERP
    select 
        data,
        conta,
        centro_custo_id,
        null as id_produto,  -- ERP não tem produtos específicos
        null as id_fornecedor,  -- ERP não tem fornecedores específicos
        valor,
        detalhes as descricao,
        'ERP' as origem_dados
    from {{ source('anfin_staging', 'stg_erp_lancamentos') }}

    union all

    -- Lançamentos do Banco Transacional
    select 
        data,
        conta_destino as conta,
        centro_custo,
        id_produto,
        id_fornecedor,
        valor,
        descricao,
        'Banco Transacional' as origem_dados
    from {{ source('anfin_staging', 'stg_banco_transacional') }}
),

-- Referências das dimensões
dim_tempo as (
    select sk_tempo, data from {{ ref('dim_tempo') }}
),

dim_contas as (
    select sk_conta, id_conta_origem from {{ ref('dim_contas') }}
),

dim_centros_custo as (
    select sk_centro_custo, id_cc_origem from {{ ref('dim_centros_custo') }}
),

dim_produtos as (
    select sk_produto, id_produto_origem from {{ ref('dim_produtos') }}
),

dim_fornecedores as (
    select sk_fornecedor, id_fornecedor_origem from {{ ref('dim_fornecedores') }}
)

-- Query principal com todos os JOINs das dimensões
select
    -- Chaves Surrogadas (SKs) obrigatórias
    dt.sk_tempo,
    dc.sk_conta,
    dcc.sk_centro_custo,
    
    -- Chaves Surrogadas (SKs) opcionais - podem ser NULL
    dp.sk_produto,
    df.sk_fornecedor,
    
    -- Métricas (fatos)
    lc.valor,
    
    -- Atributos descritivos
    lc.descricao,
    lc.origem_dados,
    
    -- Data para facilitar filtros (denormalizada)
    dt.data

from lancamentos_consolidados lc

-- JOINs obrigatórios (dimensões que sempre existem)
inner join dim_tempo dt on lc.data = dt.data
inner join dim_contas dc on lc.conta = dc.id_conta_origem
inner join dim_centros_custo dcc on lc.centro_custo_id = dcc.id_cc_origem

-- JOINs opcionais (dimensões que podem não existir)
left join dim_produtos dp on lc.id_produto = dp.id_produto_origem
left join dim_fornecedores df on lc.id_fornecedor = df.id_fornecedor_origem

-- Filtros de qualidade
where 
    lc.data is not null
    and lc.conta is not null
    and lc.centro_custo_id is not null
    and lc.valor is not null