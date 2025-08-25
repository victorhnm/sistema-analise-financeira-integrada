Aja como um arquiteto de dados sênior e analista financeiro sênior com foco em relatórios corporativos (balanço patrimonial, DRE e fluxo de caixa) e em DX para repositórios públicos. Sua missão é gerar um projeto completo “Integrated Financial Analysis” ponta a ponta, 100% grátis, rodando em nuvem (Supabase + GitHub Actions + dbt Core + FastAPI + Power BI). Pense passo a passo (pensamento prolongado): valide premissas, explicite decisões e trade-offs, e gere artefatos prontos para copiar e colar. Evite explicações prolixas: foque em outputs acionáveis. Sempre que você gerar código, entregue dentro de blocos de código com nome de arquivo e caminho, e uma linha explicando o propósito. Ao final de cada seção, inclua um checklist de verificação do que foi entregue.

Restrições e políticas:
• Custos: somente tiers gratuitos (Supabase free, GitHub Actions público, dbt Core, FastAPI simples, Power BI Desktop local; “Publish to web” apenas se possível).
• Fontes de dados: somente públicas e redistribuíveis. Priorize demonstrativos regulatórios (ex.: EDGAR/SEC via XBRL/JSON) e FX de fonte oficial (ECB ou FRED). Incluir user-agent nas chamadas quando requerido e respeitar limites com rate limiting e backoff.
• Privacidade: não expor segredos; usar placeholders e GitHub Secrets.
• Reprodutibilidade: scripts idempotentes, particionados e incrementais; testes de qualidade.
• Portfólio: README top-tier, badges, prints do dashboard, diagrama, documentação de métricas, story-telling de negócio.

Controle de versão e README — OBRIGATÓRIO (ADDITIONAL RULES):
• Commits em Português (obrigatório): Sempre que você criar ou modificar qualquer artefato importante (arquivos em /etl, /dbt_project, /api, /.github/workflows, /bi, /docs, /infra, infra/init.sql, seeds, ou modelos dbt), você deve incluir imediatamente no output um bloco chamado "Commit sugerido" contendo:

Os comandos git exatos a serem rodados (ex.: git checkout -b feat/descricao && git add <arquivos> && git commit -m "tipo(escopo): mensagem em português" && git push -u origin feat/descricao).

Mensagem de commit em português clara e descritiva (seguir padrão sugerido: tipo(escopo): ação breve — exemplos: feat(etl): adicionar parser XBRL SEC ou fix(dbt): corrigir teste unique em dim_company).

Sugestão de título e descrição do Pull Request em português prontos para colar (PR title e descrição).

Sugestão de branch name e, se aplicável, tag semântica.
Importante: O Chatbot não deve executar comandos — apenas gerá-los para que eu copie/cole.
• Atualização do README (obrigatório): Sempre que houver mudança que afete o uso, schema, comandos ou status do projeto (novos scripts, alterações em tables/seeds, novos workflows, alterações no processo CI), o Chatbot deve:

Atualizar o README principal com um resumo em português da mudança na seção Últimas alterações usando data ISO (YYYY-MM-DD).

Adicionar/atualizar uma entrada apropriada em /docs/CHANGELOG.md com detalhes (o quê mudou, por quê, quem comitou, instruções de rollback).

Atualizar badges no README se necessário (status workflows, cobertura de testes se houver).
Resposta à sua pergunta: Sim — atualizar o README constantemente é necessário e boa prática: melhora reprodutibilidade, DX e facilita avaliação do seu trabalho no portfólio.

Formato da entrega (ordem obrigatória):

Visão Geral concisa + Diagrama ASCII de arquitetura.

Estrutura de pastas (árvore) + tabela “o que vai em cada pasta”.

Catálogo de dados e licenças (fontes, endpoints, limites, política de uso).

Esquema do banco (Postgres/Supabase): DDL completo, schemas raw/staging/core/marts.

Projeto dbt: dbt_project.yml, profiles.yml (com placeholders), modelos stg/int/marts, seeds, macros, testes e exposures.

Ingestão Python (ETL): coletores por fonte, parser XBRL/JSON, upsert idempotente, logging, retries, paginação, rate limit.

Orquestração GitHub Actions: workflows YAML (etl_daily, dbt_run_test, quality_gate, api_deploy) com cron e gatilhos.

API FastAPI mínima: /health, /companies, /facts com filtros e paginação.

Power BI: modelo estrela lógico, lista de medidas DAX, recomendações de relacionamento, wireframe de 3 páginas, instruções de conexão.

Documentação: README final, guia de troubleshooting, aviso legal, roadmap, “Como avaliar minhas skills”.

Extensões “nice to have”: Brasil (CVM), Great Expectations, DuckDB local, Parquet export.

Critérios de aceite: checklist objetivo.

Importante para sua forma de resposta:
• Para cada arquivo, comece com a linha “Arquivo: <caminho/nome.ext>” e, logo abaixo, entregue o conteúdo em bloco de código do tipo apropriado.
• Inclua comentários no topo de arquivos críticos explicando decisões-chave.
• Em YAML/SQL/Python/DAX, mantenha nomes consistentes com o esquema proposto.
• Inclua variantes mínimas quando couber (ex.: ECB ou FRED para FX: gere ambos, habilitando por variável de ambiente).
• Ao final, gere um “Plano de Testes Manuais” de 10–15 passos para eu validar tudo localmente.
• Sempre que criar/modificar artefato importante, gere bloco "Commit sugerido" (conforme regras acima) E atualize README/CHANGELOG no mesmo output.

—
SEÇÃO 1 — VISÃO GERAL E DIAGRAMA
Entregue: descrição em até 8 linhas do fluxo ponta a ponta e um diagrama ASCII com: Data Sources → ETL (Python) → Supabase (raw/staging/core/marts) → dbt (stg/int/marts) → API FastAPI → Power BI. Liste também 5 decisões de design e seus trade-offs (curto).

—
SEÇÃO 2 — ESTRUTURA DE PASTAS
Entregue: a árvore abaixo e uma tabela com descrição do conteúdo de cada pasta/arquivo.

Raiz do repositório:
• /etl
• /dbt_project
• /infra
• /api
• /bi
• /docs
• /.github/workflows

Inclua um arquivo “Arquivo: .gitignore” adequado a Python, dbt, Power BI e artefatos temporários.

—
SEÇÃO 3 — CATÁLOGO DE FONTES DE DADOS E LICENÇAS
Entregue: tabela com colunas {Fonte, Finalidade, Endpoints típicos, Autenticação, Limites sugeridos, Licença/uso, Observações}.
• Demonstrativos financeiros: registros regulatórios (ex.: EDGAR/SEC XBRL/JSON – company facts, submissions).
• FX: ECB (eurofxref) e alternativa FRED (séries DEXXX).
• Tickers/empresas: tabela mínima de empresas com CIK/ticker/setor/país.
Inclua instruções de user-agent para chamadas que exijam e limites (ex.: ≤5 req/s + backoff).

—
SEÇÃO 4 — ESQUEMA DO BANCO (SUPABASE/POSTGRES)
Entregue: DDL completo com schemas raw, staging, core, marts.
• raw: arquivos brutos conforme origem (json/xbrl normalizado em colunas genéricas).
• staging: normalização básica, tipagem, dedupe.
• core: entidades canônicas (dim_company, dim_currency, dim_sector, dim_taxonomy_map, fact_statement_line).
• marts: fatos agregados e métricas prontas para BI (fact_financials_quarterly, fact_financials_ttm, views para Power BI).
Inclua índices, PKs, FKs, constraints únicas e materialized views para consumo.
Forneça “Arquivo: /infra/init.sql” com todo DDL.
Forneça “Arquivo: /infra/seed_companies.csv” com 3 empresas (AAPL, MSFT, AMZN) e colunas mínimas: ticker, cik, name, sector, country, currency.

—
SEÇÃO 5 — PROJETO DBT
Entregue:
• Arquivo: /dbt_project/dbt_project.yml
• Arquivo: /dbt_project/profiles_example.yml (usar placeholders e instruções de cópia para ~/.dbt/profiles.yml; conexão via Supabase: host, db, user, pass, port, schema=core default).
• Seeds: /dbt_project/seeds/currency_rates_sample.csv (linhas de exemplo) e /dbt_project/seeds/taxonomy_map.csv (mapa US GAAP/IFRS → canonical_metric).
• Modelos: stg_* (limpeza), int_* (harmonização + FX), marts_* (métricas finais).
• Macros úteis (ex.: generate_surrogate_key, safe_cast_decimal, fx_convert).
• Testes: unique/not_null/relationships; schema.yml com descriptions; exposures para o dashboard do Power BI.
• Estratégia incremental nos modelos de fatos (is_incremental com watermark por período_reportado).
• Documentação dbt (descriptions e refs).
Inclua instruções no topo de dbt_project.yml explicando caminhos e convenções.

—
SEÇÃO 6 — INGESTÃO (PYTHON)
Entregue:
• Estrutura /etl:

/etl/common/config.py (leitura de env, configs, constantes como user-agent)

/etl/common/db.py (pool de conexões, upsert genérico)

/etl/sources/sec_client.py (chamadas a endpoints, paginação, rate limit, retries)

/etl/sources/fx_client.py (ECB e FRED, alternáveis por env)

/etl/parsers/sec_xbrl_parser.py (normalização de company facts → linhas: company_id, period_start, period_end, statement, concept, unit, value, is_restated etc.)

/etl/jobs/ingest_companies.py (seed de empresas para tabela dim_company)

/etl/jobs/ingest_sec_facts.py (coleta incremental por CIK, período, statement)

/etl/jobs/ingest_fx.py (FX diário)

/etl/main.py (CLI: comandos “companies”, “facts”, “fx”, “all”)
• Boas práticas: logging estruturado, idempotência (ON CONFLICT DO UPDATE), chunking, paralelismo moderado (ex.: asyncio + semáforo), validações de schema simples (pydantic), e testes unitários mínimos (pytest) para parsers.
• Arquivo: /etl/requirements.txt com versões estáveis.
• Arquivo: /etl/.env.example com placeholders: DATABASE_URL, SEC_USER_AGENT, SOURCE_FX, RATE_LIMIT_RPS etc.
• “Como rodar localmente”: comandos python -m etl.main …
• Incluir notinhas sobre limites e ética de acesso.

Commit sugerido (exemplo)

# Comandos git (copiar/colar)
git checkout -b feat/ingest/sec-xbrl-parser
git add etl/parsers/sec_xbrl_parser.py etl/jobs/ingest_sec_facts.py etl/requirements.txt
git commit -m "feat(etl): adicionar parser XBRL SEC e job de ingestão incremental"
git push -u origin feat/ingest/sec-xbrl-parser


Título PR (em português): feat: adicionar parser XBRL SEC e ingestão incremental
Descrição PR (em português): Adiciona parser XBRL para normalizar company facts da SEC e job incremental para ingestão por CIK. Inclui validações básicas e exemplos de .env. Testes unitários básicos incluídos.

—
SEÇÃO 7 — ORQUESTRAÇÃO (GITHUB ACTIONS)
Entregue os YAMLs:
• /.github/workflows/etl_daily.yml → cron diário + matrix por fonte (facts, fx), cache de pip, variáveis e secrets.
• /.github/workflows/dbt_run_test.yml → dbt deps → seed → run → test, com artifact upload (logs/target).
• /.github/workflows/quality_gate.yml → pytest para parsers e validações rápidas do schema, badge de status.
• /.github/workflows/api_deploy.yml → build e sanity check da FastAPI (teste de /health).
Inclua badges prontos para o README (status dos 4 workflows).

—
SEÇÃO 8 — API (FASTAPI)
Entregue:
• /api/app.py com endpoints: /health, /companies (filtros: setor, país, ticker; paginação), /facts (filtros: ticker, período, statement, métrica; paginação; ordenação; limites).
• /api/db.py (conexão read-only, variáveis de ambiente)
• /api/requirements.txt
• Dockerfile leve (uso local opcional).
• Exemplo de curl para cada endpoint.
• Observação: paginar e limitar respostas, retornar metadata (page, page_size, total_estimated).

Commit sugerido (exemplo)

git checkout -b feat/api/basic-endpoints
git add api/app.py api/db.py api/requirements.txt
git commit -m "feat(api): adicionar endpoints /health, /companies, /facts com paginação"
git push -u origin feat/api/basic-endpoints


PR title (pt): feat(api): endpoints básicos para leitura de empresas e fatos
PR description (pt): Implementa API read-only com endpoints para health, lista de empresas e consulta de facts com filtros e paginação.

—
SEÇÃO 9 — POWER BI (PBIP em vez de PBIX)
Entregue:
• Modelo estrela lógico documentado (texto + diagrama ASCII): dim_company, dim_date, dim_currency, dim_sector; fatos: fact_financials_quarterly e fact_financials_ttm.
• Lista de medidas DAX (nomes exatos e fórmulas) para: Receita TTM, Crescimento Receita YoY, Margem Bruta, Margem Operacional, ROE, ROA, Debt/Equity, CCC (dias), DuPont (3 fatores).
• Recomendações de relacionamentos e formatos (moeda, %, casas decimais).
• Wireframe de 3 páginas: “Visão Executiva”, “Desempenho e Crescimento”, “Liquidez e Caixa”.
• Projeto PBIP versionável em /bi/pbip/ com subestruturas mínimas (use nomes canônicos):

/bi/pbip/Report/definition.pbir e artefatos do relatório (JSONs correspondentes).

/bi/pbip/Dataset/definition.pbir e metadados do modelo (inclua medidas DAX e conexões).

Instruções para abrir no Power BI Desktop como Projeto (Arquivo → Opções de Prévia → habilitar PBIP, se necessário; depois “Salvar como” PBIP).
• Instruções de conexão:

Opção A (direto): conector Postgres → Supabase (host/port/db/user).

Opção B (export): script Python para exportar CSV/Parquet; no PBIP, configurar tabelas como “Import” apontando para arquivos locais do repositório (/bi/exports/*.parquet).
• Entregue também Arquivo: /bi/medidas_dax.txt com todas as medidas e comentários.

Commit sugerido (exemplo PBIP)

git checkout -b feat/bi/pbip-estrutura-inicial
git add bi/pbip/Report/definition.pbir bi/pbip/Dataset/definition.pbir bi/medidas_dax.txt
git commit -m "feat(bi): adicionar estrutura inicial PBIP (Report e Dataset) e medidas DAX"
git push -u origin feat/bi/pbip-estrutura-inicial


PR title (pt): feat(bi): estrutura PBIP inicial (Report/Dataset) + medidas DAX
PR description (pt): Cria projeto Power BI no formato PBIP versionável, com Report/Dataset e conjunto inicial de medidas DAX. Instruções de abertura e conexão incluídas.

—

SEÇÃO 10 — DOCUMENTAÇÃO (README E AFINS)
Entregue:
• /docs/README.md com: visão, diferenciais, arquitetura, stack, fontes e licenças, como rodar (local e CI), como configurar Secrets, prints de telas, badges dos workflows, “Como avaliar minhas skills” (mapa de competências: engenharia, análise, BI), roadmap (MVP → extensões).
• /docs/TROUBLESHOOTING.md (erros comuns: timeouts, quotas, schema drift).
• /docs/LEGAL_NOTICE.md (uso de dados públicos e redistribuição).
• /LICENSE (MIT).
Inclua no README uma seção “Roteiro de Demonstração” com comandos passo a passo e capturas esperadas.

IMPORTANTE (README update): Sempre que gerar/alterar qualquer dos artefatos acima, o Chatbot deve inserir no README principal (topo) um trecho em português na seção Últimas alterações com data ISO, resumo curto, e link para o PR/branch sugerido. Também adicione/atualize /docs/CHANGELOG.md.

Commit sugerido (exemplo atualização README)

git checkout -b docs/update-readme-after-ingest
git add README.md docs/CHANGELOG.md
git commit -m "docs(readme): atualizar README e CHANGELOG com novo job de ingestão SEC"
git push -u origin docs/update-readme-after-ingest

onde citar PBIX, substituir por PBIP e adicionar instruções de abertura de projeto PBIP)

Commit sugerido (exemplo atualização README para PBIP)

git checkout -b docs/readme-pbip
git add README.md docs/CHANGELOG.md
git commit -m "docs(readme): instruções PBIP e atualização de fluxo de conexão"
git push -u origin docs/readme-pbip

—
SEÇÃO 11 — EXTENSÕES (NICE TO HAVE)
Entregue: instruções e artefatos mínimos para:
• Brasil (CVM): script de coleta inicial e parser; tabela adicional de mapeamento IFRS.
• Qualidade de dados: Great Expectations básica sobre tabelas core.
• DuckDB local + export Parquet.
Cada item com “como ligar/desligar” via variável de ambiente.

—
SEÇÃO 12 — CRITÉRIOS DE ACEITE
Entregue uma lista marcada que eu possa copiar no README, incluindo:
[ ] Pipelines rodam fim a fim com Actions no repositório público.
[ ] Supabase com ≥3 empresas e ≥8 trimestres.
[ ] dbt seeds, run, test, exposures ok.
[ ] Power BI calcula TTM, YoY, DuPont, CCC.
[ ] README com prints e badges verdes.
[ ] Código idempotente, com logs e rate limiting.

—
SEÇÃO 13 — VARIÁVEIS DE AMBIENTE E SEGREDOS
Entregue: tabela com {NOME, Descrição, Exemplo de valor, Onde configurar} incluindo:
DATABASE_URL (Supabase), SEC_USER_AGENT, SOURCE_FX (ECB|FRED), RATE_LIMIT_RPS, LOG_LEVEL, API_PAGE_SIZE_DEFAULT, API_MAX_PAGE_SIZE, DBT_TARGET_SCHEMA etc.
Explique como configurá-las em GitHub Secrets e em .env local.

—
SEÇÃO 14 — PLANOS DE BACKFILL E INCREMENTALIDADE
Entregue: estratégia de backfill por janela deslizante (ex.: últimos 12 trimestres), flags de “is_restated” e tratamento de reclassificações.
Inclua pseudo-SQL de filtros incrementais e como reinicializar uma empresa específica.

—
SEÇÃO 15 — PLANO DE TESTES MANUAIS
Entregue: 10–15 passos para validar tudo localmente (seed → ingest → dbt → api → export CSV → abrir PBIP → checar medidas) com resultados esperados.

—
Padronização de nomenclatura:
• Schemas: raw, staging, core, marts
• Tabelas principais: dim_company, dim_sector, dim_currency, fact_statement_line, fact_financials_quarterly, fact_financials_ttm
• Colunas comuns: company_id, cik, ticker, period_start, period_end, fiscal_period, statement, concept, canonical_metric, unit, value, value_native, value_converted, currency_from, currency_to, fx_rate, load_ts

Diretrizes de qualidade:
• Testes dbt: unique/not_null/relationships em chaves e joins críticos.
• Observabilidade: logs de ingestão contendo contagens por empresa/período, delta de linhas, e tempo de execução.
• Segurança: conexão read-only para API, paginação obrigatória, limites configuráveis.

Se alguma fonte exigir um dado que não possa ser redistribuído, proponha alternativa aberta e ajuste o pipeline.

Fim do Prompt.