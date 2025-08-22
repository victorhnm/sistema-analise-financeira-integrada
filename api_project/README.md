# 🏦 API de Análise Financeira Integrada

API FastAPI profissional para servir dados do Data Warehouse financeiro via endpoints REST.

## 📁 Estrutura do Projeto

```
api_project/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configurações da aplicação
│   ├── database.py         # Gerenciamento de conexões DB
│   ├── models.py           # Modelos Pydantic para responses
│   └── routers/
│       ├── __init__.py
│       ├── dimensoes.py    # Endpoints para dimensões
│       └── fatos.py        # Endpoints para fatos e análises
├── main.py                 # Aplicação principal
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```

## 🚀 Como Rodar a API

### 1. Ativar o Ambiente Virtual e Instalar Dependências

```bash
# No diretório api_project/
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Certifique-se que existe um arquivo `.env` na raiz do projeto com:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aurora_db
DB_USER=postgres
DB_PASSWORD=123456
```

### 3. Iniciar o Banco PostgreSQL

```bash
# No diretório raiz do projeto
docker-compose up -d
```

### 4. Executar a API

```bash
# No diretório api_project/
python main.py
```

A API estará disponível em: **http://localhost:8000**

## 📖 Documentação da API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔗 Endpoints Principais

### Dimensões (`/v1/dimensoes/`)

- `GET /v1/dimensoes/contas` - Lista plano de contas
- `GET /v1/dimensoes/centros-custo` - Lista centros de custo
- `GET /v1/dimensoes/tempo` - Lista dimensão tempo
- `GET /v1/dimensoes/produtos` - Lista produtos
- `GET /v1/dimensoes/fornecedores` - Lista fornecedores
- `GET /v1/dimensoes/contas/{conta_id}` - Detalhes de uma conta

### Fatos (`/v1/fatos/`)

- `GET /v1/fatos/lancamentos` - Lançamentos contábeis com filtros
- `GET /v1/fatos/caixa` - Movimentação de caixa
- `GET /v1/fatos/resumo-financeiro` - Resumo agregado por período
- `GET /v1/fatos/analise-contas` - Top contas por valor
- `GET /v1/fatos/kpis` - KPIs financeiros principais

## 💡 Exemplos de Uso

### Buscar Contas por Tipo

```bash
curl "http://localhost:8000/v1/dimensoes/contas?tipo_conta=Receita"
```

### Resumo Financeiro Mensal

```bash
curl "http://localhost:8000/v1/fatos/resumo-financeiro?agrupamento=mensal&data_inicio=2024-01-01&data_fim=2024-12-31"
```

### KPIs do Período

```bash
curl "http://localhost:8000/v1/fatos/kpis?data_inicio=2024-01-01&data_fim=2024-12-31"
```

## 🔧 Recursos Implementados

✅ Arquitetura modular com routers separados  
✅ Modelos Pydantic para validação de dados  
✅ Gerenciamento profissional de conexões DB  
✅ Context managers para transações seguras  
✅ Logging estruturado  
✅ CORS configurado  
✅ Health check endpoint  
✅ Documentação automática (Swagger/ReDoc)  
✅ Filtros dinâmicos nos endpoints  
✅ Análises financeiras agregadas  
✅ KPIs calculados automaticamente  

## 🐛 Troubleshooting

### Erro de Conexão com Banco

1. Verifique se o Docker está rodando: `docker ps`
2. Teste a conexão: `docker exec -it anfin-postgres-db psql -U postgres -d aurora_db`
3. Verifique as variáveis no arquivo `.env`

### Erro de Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Erro de Import

Certifique-se de estar executando do diretório `api_project/`:
```bash
cd api_project/
python main.py
```