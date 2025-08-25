"""
FastAPI Application - Integrated Financial Analysis
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configurações
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://victorhnm:@urora12@localhost:5432/aurora_db')

# Criar aplicação
app = FastAPI(
    title="Integrated Financial Analysis API",
    description="API REST para dados financeiros da SEC EDGAR",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Integrated Financial Analysis API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check"""
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='victorhnm',
            password='@urora12',
            database='aurora_db'
        )
        company_count = await conn.fetchval("SELECT COUNT(*) FROM core.dim_company")
        await conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": f"connected ({company_count} companies)",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/companies")
async def get_companies(limit: int = 10):
    """Lista empresas disponíveis"""
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='victorhnm',
            password='@urora12',
            database='aurora_db'
        )
        rows = await conn.fetch("""
            SELECT cik, ticker, company_name, sector, country, is_active
            FROM core.dim_company 
            WHERE is_active = true
            ORDER BY company_name
            LIMIT $1
        """, limit)
        await conn.close()
        
        companies = []
        for row in rows:
            companies.append({
                "cik": row['cik'],
                "ticker": row['ticker'],
                "name": row['company_name'],
                "sector": row['sector'],
                "country": row['country']
            })
            
        return {"companies": companies, "total": len(companies)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/raw-data/{cik}")
async def get_raw_data(cik: str):
    """Busca dados brutos de uma empresa"""
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='victorhnm',
            password='@urora12',
            database='aurora_db'
        )
        row = await conn.fetchrow("""
            SELECT cik, company_name, ticker, raw_data, ingested_at
            FROM raw.sec_company_facts 
            WHERE cik = $1
            ORDER BY ingested_at DESC
            LIMIT 1
        """, cik)
        await conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"CIK {cik} not found")
        
        raw_data_str = row['raw_data']
        # Se for string, fazer parse do JSON
        if isinstance(raw_data_str, str):
            import json
            raw_data = json.loads(raw_data_str)
        else:
            raw_data = raw_data_str
            
        facts = raw_data.get('facts', {})
        us_gaap = facts.get('us-gaap', {})
        
        return {
            "company_info": {
                "cik": row['cik'],
                "name": row['company_name'],
                "ticker": row['ticker'],
                "last_updated": row['ingested_at'].isoformat()
            },
            "summary": {
                "us_gaap_concepts": len(us_gaap),
                "sample_concepts": list(us_gaap.keys())[:5]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
