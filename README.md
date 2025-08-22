# 🏦 Sistema de Análise Financeira Integrada

Projeto completo de **Data Engineering** e **Analytics** para análise financeira empresarial usando stack profissional moderna.

## 🎯 Visão Geral

Sistema end-to-end de análise financeira que integra:
- **ETL/ELT** com Python e dbt
- **Data Warehouse** modelado em PostgreSQL
- **API REST** profissional com FastAPI
- **Visualizações** em Power BI
- **Deploy** containerizado com Docker

## 📊 Arquitetura

```
Fontes de Dados → Staging → Transformação (dbt) → Data Warehouse → API → Power BI
     ↓              ↓            ↓                    ↓           ↓       ↓
   CSV/JSON     PostgreSQL    Modelos dbt        Dimensões    FastAPI  Dashboards
   Excel/API      (Staging)    SQL + Jinja2      & Fatos    REST API   Análises
```

## 🚀 Stack Tecnológica

### Backend & Data
- **Python 3.13** - Linguagem principal
- **PostgreSQL 15** - Data Warehouse
- **dbt** - Transformações SQL
- **FastAPI** - API REST
- **Docker** - Containerização
- **Pydantic** - Validação de dados

### Análise & BI
- **Power BI** - Visualizações e dashboards
- **SQL** - Queries analíticas
- **JSON/REST** - Integração de dados

## 📁 Estrutura do Projeto

```
projeto-analise-financeira/
├── 📊 etl_project/                     # Pipeline ETL/ELT
│   ├── scripts/                       # Scripts de ingestão
│   ├── anfin_dbt_project/             # Projeto dbt
│   │   ├── models/marts/              # Modelos finais (dimensões/fatos)
│   │   └── models/staging.yml         # Fontes de dados
│   └── sources_data/                  # Dados de exemplo
├── 🔗 api_project/                    # API FastAPI
│   ├── app/                          # Código da aplicação
│   │   ├── routers/                  # Endpoints organizados
│   │   ├── models.py                 # Schemas Pydantic
│   │   ├── database.py               # Conexões DB
│   │   └── config.py                 # Configurações
│   ├── main.py                       # App principal
│   ├── requirements.txt              # Dependências Python
│   └── Dockerfile                    # Container da API
├── 📈 Guias de Conexão/              # Documentação
│   ├── POWER_BI_CONNECTION.md        # Power BI setup
│   └── DEPLOY_GUIDE.md               # Deploy e CI/CD
├── docker-compose.yml                # Infraestrutura
└── README.md                         # Este arquivo
```

## 🏃‍♂️ Como Executar

### 1️⃣ Pré-requisitos
```bash
# Docker Desktop instalado
# Python 3.13
# Power BI Desktop (opcional)
```

### 2️⃣ Configurar Ambiente
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/projeto-analise-financeira.git
cd projeto-analise-financeira

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações
```

### 3️⃣ Executar Infraestrutura
```bash
# Subir PostgreSQL
docker-compose up -d

# Aguardar inicialização (30s)
```

### 4️⃣ Popular Data Warehouse
```bash
cd etl_project/scripts
python seed_staging_data.py

# Executar transformações dbt (opcional - já executado)
```

### 5️⃣ Executar API
```bash
cd api_project
pip install -r requirements.txt
python main.py
```

### 6️⃣ Acessar Aplicação
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 Data Warehouse - Modelo Dimensional

### 🎯 Dimensões
- **dim_contas** - Plano de contas contábil
- **dim_centros_custo** - Centros de custo organizacionais  
- **dim_tempo** - Calendário para análises temporais
- **dim_fornecedores** - Cadastro de fornecedores
- **dim_produtos** - Catálogo de produtos/serviços

### 📈 Fatos
- **fato_lancamentos** - Lançamentos contábeis detalhados
- **fato_caixa** - Movimentação de caixa/bancos

### 🔑 Relacionamentos
```sql
fato_lancamentos → dim_contas (sk_conta)
fato_lancamentos → dim_centros_custo (sk_centro_custo) 
fato_lancamentos → dim_tempo (sk_tempo)

fato_caixa → dim_contas (sk_conta)
fato_caixa → dim_centros_custo (sk_centro_custo)
fato_caixa → dim_tempo (sk_tempo)
```

## 🔗 API Endpoints

### Dimensões (`/v1/dimensoes/`)
```http
GET /v1/dimensoes/contas              # Lista plano de contas
GET /v1/dimensoes/centros-custo       # Lista centros de custo  
GET /v1/dimensoes/tempo               # Lista calendário
GET /v1/dimensoes/fornecedores        # Lista fornecedores
GET /v1/dimensoes/produtos            # Lista produtos
GET /v1/dimensoes/contas/{id}         # Detalhes de uma conta
```

### Fatos e Análises (`/v1/fatos/`)
```http
GET /v1/fatos/lancamentos             # Lançamentos contábeis
GET /v1/fatos/caixa                   # Movimentação de caixa
GET /v1/fatos/resumo-financeiro       # Resumo por período
GET /v1/fatos/analise-contas          # Top contas por valor
GET /v1/fatos/kpis                    # KPIs financeiros
```

### Exemplos de Resposta
```json
// GET /v1/fatos/kpis
{
  "total_lancamentos": 2000,
  "receitas_total": 3007687.34,
  "despesas_total": 4109479.77,
  "resultado_liquido": -1101792.43,
  "margem_liquida": -36.63
}
```

## 📊 Power BI - Conectar aos Dados

### Opção 1: Conexão Direta PostgreSQL ⭐ (Recomendado)
1. **Obter Dados** → **PostgreSQL**
2. **Servidor**: `localhost:5432`
3. **Database**: `aurora_db`
4. **Credenciais**: Ver arquivo `.env`

### Opção 2: Conexão via API REST
1. **Obter Dados** → **Web**
2. **URL**: `http://localhost:8000/v1/fatos/kpis`
3. **Expandir JSON** no Power Query

📖 **Guia completo**: [POWER_BI_CONNECTION.md](POWER_BI_CONNECTION.md)

## 🐳 Deploy e Produção

### Docker Compose
```bash
# Build e deploy completo
docker-compose up -d --build

# API + PostgreSQL em containers
```

### CI/CD com GitHub Actions
```yaml
# Pipeline automático de deploy
# Build → Test → Deploy → Monitoramento
```

🚀 **Guia completo**: [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)

## 📈 Dashboards Sugeridos

### 1️⃣ **Visão Executiva**
- KPIs principais (Receita, Despesa, Resultado)
- Evolução mensal/trimestral
- Margem de lucro
- Top 10 contas

### 2️⃣ **Análise Operacional**
- Despesas por centro de custo
- Análise de fornecedores
- Produtos mais rentáveis
- Análise de sazonalidade

### 3️⃣ **Fluxo de Caixa**
- Entradas vs Saídas
- Saldo acumulado
- Projeções
- Análise de liquidez

## 🧪 Testes e Qualidade

```bash
# Testes da API
cd api_project
pytest tests/

# Validações dbt  
cd etl_project/anfin_dbt_project
dbt test

# Health checks
curl http://localhost:8000/health
```

## 📊 Dados de Exemplo

O projeto inclui dados sintéticos para demonstração:
- **2.000 lançamentos** contábeis
- **6 contas** contábeis diferentes
- **5 centros de custo**
- **3 produtos**
- **5 fornecedores**
- **Período**: 2024 completo

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Add: nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

- **Issues**: Use as issues do GitHub
- **Documentação**: Arquivos `.md` na raiz
- **API Docs**: http://localhost:8000/docs

---

**🚀 Desenvolvido com Stack Profissional de Data Engineering**

*Sistema completo para análise financeira empresarial com arquitetura moderna e escalável*