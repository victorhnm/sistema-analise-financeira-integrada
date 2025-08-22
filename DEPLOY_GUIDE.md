# 🚀 Guia de Deploy e Orquestração

## 📦 Fase 6: Containerização com Docker

### 1. Docker da API

#### Construir Imagem
```bash
cd api_project/
docker build -t anfin-api:latest .
```

#### Testar Localmente
```bash
docker run -p 8000:8000 --env-file ../.env anfin-api:latest
```

### 2. Docker Compose Completo

Atualize o `docker-compose.yml` na raiz:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: anfin-postgres-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 123456
      POSTGRES_DB: aurora_db
    ports:
      - "5432:5432"
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    networks:
      - anfin-network

  api:
    build: ./api_project
    container_name: anfin-api
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: aurora_db
      DB_USER: postgres
      DB_PASSWORD: 123456
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    networks:
      - anfin-network
    restart: unless-stopped

networks:
  anfin-network:
    driver: bridge
```

#### Executar Stack Completa
```bash
docker-compose up -d --build
```

---

## 🔄 Orquestração com Airflow

### 1. Instalação Airflow

```bash
pip install apache-airflow
pip install apache-airflow-providers-postgres
pip install apache-airflow-providers-docker
```

### 2. DAG de ETL Completo

Crie `dags/anfin_etl_dag.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'anfin_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL Análise Financeira',
    schedule_interval='0 6 * * *',  # Diário às 6h
    catchup=False,
    tags=['finance', 'etl', 'dwh']
)

# Task 1: Ingestão de dados
ingest_data = BashOperator(
    task_id='ingest_raw_data',
    bash_command='cd /app/etl_project/scripts && python seed_staging_data.py',
    dag=dag
)

# Task 2: Transformação dbt
dbt_run = BashOperator(
    task_id='dbt_transform',
    bash_command='cd /app/etl_project/anfin_dbt_project && dbt run',
    dag=dag
)

# Task 3: Testes de qualidade
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /app/etl_project/anfin_dbt_project && dbt test',
    dag=dag
)

# Task 4: Reiniciar API
restart_api = BashOperator(
    task_id='restart_api',
    bash_command='docker-compose restart api',
    dag=dag
)

# Definir dependências
ingest_data >> dbt_run >> dbt_test >> restart_api
```

### 3. Inicializar Airflow

```bash
# Inicializar banco do Airflow
airflow db init

# Criar usuário admin
airflow users create --username admin --password admin123 --firstname Admin --lastname User --role Admin --email admin@example.com

# Iniciar scheduler e webserver
airflow scheduler &
airflow webserver --port 8080
```

**Airflow UI:** http://localhost:8080

---

## 🔄 Alternativa: Orquestração com Mage

### 1. Instalação Mage

```bash
pip install mage-ai
```

### 2. Inicializar Projeto Mage

```bash
mage init anfin_mage_project
cd anfin_mage_project
```

### 3. Pipeline ETL no Mage

Crie blocos no Mage:

#### Data Loader: `load_staging_data.py`
```python
import pandas as pd
from mage_ai.data_preparation.decorators import data_loader

@data_loader
def load_data(**kwargs):
    # Lógica de ingestão de dados
    return df
```

#### Transformer: `transform_dbt.py`
```python
from mage_ai.data_preparation.decorators import transformer

@transformer
def transform_data(df, **kwargs):
    # Executar transformações dbt
    return transformed_df
```

#### Data Exporter: `export_to_dwh.py`
```python
from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data(df, **kwargs):
    # Salvar no DWH
    pass
```

### 4. Executar Mage

```bash
mage start anfin_mage_project
```

**Mage UI:** http://localhost:6789

---

## ☁️ Deploy em Produção

### 1. Variáveis de Ambiente Produção

```env
# .env.production
DB_HOST=prod-postgres.company.com
DB_PORT=5432
DB_NAME=anfin_prod
DB_USER=anfin_user
DB_PASSWORD=super_secure_password

API_ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 2. Docker Compose Produção

```yaml
version: '3.8'

services:
  api:
    image: anfin-api:latest
    environment:
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
    ports:
      - "80:8000"
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

### 3. CI/CD com GitHub Actions

`.github/workflows/deploy.yml`:

```yaml
name: Deploy API

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker Image
        run: |
          cd api_project
          docker build -t ${{ secrets.REGISTRY }}/anfin-api:${{ github.sha }} .
      
      - name: Push to Registry
        run: docker push ${{ secrets.REGISTRY }}/anfin-api:${{ github.sha }}
      
      - name: Deploy to Production
        run: |
          ssh ${{ secrets.PROD_SERVER }} "docker pull ${{ secrets.REGISTRY }}/anfin-api:${{ github.sha }} && docker-compose up -d"
```

---

## 📊 Monitoramento

### 1. Métricas da API

Adicione endpoints de métricas:

```python
@app.get("/metrics")
async def get_metrics():
    return {
        "uptime": get_uptime(),
        "requests_total": get_request_count(),
        "database_connections": get_db_pool_status(),
        "memory_usage": get_memory_usage()
    }
```

### 2. Logs Estruturados

Configure logging para produção:

```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "request_processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    return response
```

---

## ✅ Checklist de Deploy

- [ ] Docker images construídas e testadas
- [ ] Variáveis de ambiente configuradas
- [ ] Backup do banco configurado
- [ ] SSL/HTTPS configurado
- [ ] Monitoramento implementado
- [ ] Pipeline CI/CD funcionando
- [ ] Logs centralizados
- [ ] Testes automatizados passando
- [ ] Documentação atualizada
- [ ] Plano de rollback definido

---

## 🎯 Resultado Final

Com este setup você terá:

✅ **API containerizada** rodando em produção  
✅ **Pipeline ETL automatizado** (Airflow ou Mage)  
✅ **Deploy automatizado** com CI/CD  
✅ **Monitoramento** e alertas  
✅ **Escalabilidade** horizontal  
✅ **Backup e recovery** configurado  
✅ **Segurança** implementada  

**Seu projeto estará pronto para produção! 🚀**