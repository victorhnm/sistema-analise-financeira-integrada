-- anfin_dbt_project/models/marts/dim_tempo.sql

-- Este modelo simplesmente seleciona os dados da tabela Dim_Tempo
-- que já foi populada pelo nosso script Python.
-- Fazemos isso para que o dbt conheça a tabela e possa
-- gerenciar as dependências corretamente.

select * from {{ source('anfin_staging', 'dim_tempo') }}