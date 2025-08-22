-- anfin_dbt_project/models/marts/dim_produtos.sql

with source_data as (
    select distinct
        id_produto as id_produto_origem
    from {{ source('anfin_staging', 'stg_banco_transacional') }}
    where id_produto is not null
)

select
    -- Cria chave surrogate única para cada produto
    {{ dbt_utils.generate_surrogate_key(['id_produto_origem']) }} as sk_produto,
    
    id_produto_origem,
    
    -- Em um projeto real, esta informação viria de um sistema de cadastro de produtos.
    -- Como não temos, estamos aplicando a regra de negócio aqui.
    case
        when id_produto_origem = 'PROD-A' then 'Produto Alpha'
        when id_produto_origem = 'PROD-B' then 'Produto Beta'
        when id_produto_origem = 'PROD-C' then 'Produto Gamma'
        else 'Produto Desconhecido'
    end as nome_produto,

    case
        when id_produto_origem = 'PROD-A' then 'Eletrônicos'
        when id_produto_origem = 'PROD-B' then 'Escritório'
        when id_produto_origem = 'PROD-C' then 'Serviços'
        else 'N/A'
    end as categoria,
    
    -- Adiciona subcategoria para análises mais detalhadas
    case
        when id_produto_origem = 'PROD-A' then 'Smartphones'
        when id_produto_origem = 'PROD-B' then 'Móveis'
        when id_produto_origem = 'PROD-C' then 'Consultoria'
        else 'N/A'
    end as subcategoria

from source_data