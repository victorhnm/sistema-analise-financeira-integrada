-- anfin_dbt_project/models/marts/fato_caixa.sql

with 

-- Dados da conciliação bancária (fonte principal)
movimentacoes_bancarias as (
    select 
        data,
        tipo,
        valor,
        historico,
        -- Aplicar regras de negócio para classificação automática
        case 
            when lower(historico) like '%pagamento%fornecedor%' then '5.1.1.01'  -- Despesas com fornecedores
            when lower(historico) like '%salario%' or lower(historico) like '%folha%' then '5.1.1.01'  -- Salários
            when lower(historico) like '%aluguel%' then '5.2.1.01'  -- Aluguel
            when lower(historico) like '%receita%vendas%' or lower(historico) like '%cliente%' then '4.1.1.01'  -- Receitas
            when lower(historico) like '%software%' or lower(historico) like '%licenca%' then '5.3.1.04'  -- Software
            when tipo = 'ENTRADA' then '4.1.1.01'  -- Receitas padrão
            else '5.3.1.09'  -- Serviços de terceiros (despesas diversas)
        end as conta_classificada,
        
        -- Aplicar regras para centro de custo baseado no histórico
        case
            when lower(historico) like '%vendas%' or lower(historico) like '%cliente%' then 'VENDAS'
            when lower(historico) like '%rh%' or lower(historico) like '%salario%' or lower(historico) like '%folha%' then 'RH'
            when lower(historico) like '%marketing%' or lower(historico) like '%publicidade%' then 'MARKETING'
            when lower(historico) like '%ti%' or lower(historico) like '%software%' then 'TI'
            else 'CC_RH'  -- Centro de custo padrão administrativo
        end as centro_custo_classificado
        
    from {{ source('anfin_staging', 'stg_conciliacao_bancaria') }}
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
)

-- Query principal da tabela fato
select
    -- Chaves Surrogadas (SKs) obrigatórias
    dt.sk_tempo,
    dc.sk_conta,
    dcc.sk_centro_custo,
    
    -- Métricas de caixa (sempre uma entrada OU uma saída, nunca ambas)
    case 
        when mb.tipo = 'ENTRADA' then abs(mb.valor) 
        else 0 
    end as valor_entrada,
    
    case 
        when mb.tipo = 'SAIDA' then abs(mb.valor) 
        else 0 
    end as valor_saida,
    
    -- Saldo líquido da movimentação (positivo para entrada, negativo para saída)
    case 
        when mb.tipo = 'ENTRADA' then abs(mb.valor)
        when mb.tipo = 'SAIDA' then -abs(mb.valor)
        else 0
    end as saldo,
    
    -- Tipo da movimentação para análises
    mb.tipo as tipo_movimentacao,
    
    -- Atributos descritivos
    mb.historico as descricao,
    'Conciliação Bancária' as origem_dados,
    
    -- Data denormalizada para facilitar filtros
    dt.data

from movimentacoes_bancarias mb

-- JOINs obrigatórios com as dimensões
inner join dim_tempo dt on mb.data = dt.data
inner join dim_contas dc on mb.conta_classificada = dc.id_conta_origem
inner join dim_centros_custo dcc on mb.centro_custo_classificado = dcc.id_cc_origem

-- Filtros de qualidade dos dados
where 
    mb.data is not null
    and mb.valor is not null
    and mb.valor != 0  -- Excluir movimentações zeradas
    and mb.tipo in ('ENTRADA', 'SAIDA')  -- Garantir tipos válidos