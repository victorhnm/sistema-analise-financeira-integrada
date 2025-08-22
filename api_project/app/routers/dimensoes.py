from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import (
    DimContaResponse, DimCentroCustoResponse, DimTempoResponse,
    DimProdutoResponse, DimFornecedorResponse
)
from app.database import DatabaseManager
import logging

router = APIRouter(prefix="/dimensoes", tags=["Dimensões"])
logger = logging.getLogger(__name__)

@router.get("/contas", response_model=List[DimContaResponse])
async def get_contas(
    tipo_conta: Optional[str] = Query(None, description="Filtrar por tipo de conta"),
    grupo_conta: Optional[str] = Query(None, description="Filtrar por grupo de conta")
):
    """Retorna todas as contas do plano de contas."""
    try:
        query = "SELECT sk_conta, id_conta_origem, nome_conta, tipo_conta, grupo_conta FROM dim_contas WHERE 1=1"
        params = []
        
        if tipo_conta:
            query += " AND tipo_conta = %s"
            params.append(tipo_conta)
            
        if grupo_conta:
            query += " AND grupo_conta = %s"
            params.append(grupo_conta)
            
        query += " ORDER BY id_conta_origem"
        
        results = DatabaseManager.execute_query(query, tuple(params) if params else None)
        return [DimContaResponse(**dict(row)) for row in results]
        
    except Exception as e:
        logger.error(f"Erro ao buscar contas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/centros-custo", response_model=List[DimCentroCustoResponse])
async def get_centros_custo():
    """Retorna todos os centros de custo."""
    try:
        query = """
        SELECT sk_centro_custo, id_cc_origem, nome_centro_custo, setor, gerencia 
        FROM dim_centros_custo 
        ORDER BY nome_centro_custo
        """
        results = DatabaseManager.execute_query(query)
        return [DimCentroCustoResponse(**dict(row)) for row in results]
        
    except Exception as e:
        logger.error(f"Erro ao buscar centros de custo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/tempo", response_model=List[DimTempoResponse])
async def get_tempo(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    mes: Optional[int] = Query(None, description="Filtrar por mês (1-12)")
):
    """Retorna dimensão tempo."""
    try:
        query = """
        SELECT sk_tempo, data, ano, mes, trimestre, nome_mes, dia_semana, nome_dia_semana 
        FROM dim_tempo WHERE 1=1
        """
        params = []
        
        if ano:
            query += " AND ano = %s"
            params.append(ano)
            
        if mes:
            query += " AND mes = %s"
            params.append(mes)
            
        query += " ORDER BY data"
        
        results = DatabaseManager.execute_query(query, tuple(params) if params else None)
        return [DimTempoResponse(**dict(row)) for row in results]
        
    except Exception as e:
        logger.error(f"Erro ao buscar dimensão tempo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/produtos", response_model=List[DimProdutoResponse])
async def get_produtos():
    """Retorna todos os produtos."""
    try:
        query = """
        SELECT sk_produto, id_produto_origem, nome_produto, categoria, subcategoria 
        FROM dim_produtos 
        ORDER BY nome_produto
        """
        results = DatabaseManager.execute_query(query)
        return [DimProdutoResponse(**dict(row)) for row in results]
        
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/fornecedores", response_model=List[DimFornecedorResponse])
async def get_fornecedores():
    """Retorna todos os fornecedores."""
    try:
        query = """
        SELECT sk_fornecedor, id_fornecedor_origem, nome_fornecedor, tipo_fornecedor, categoria_fornecedor 
        FROM dim_fornecedores 
        ORDER BY nome_fornecedor
        """
        results = DatabaseManager.execute_query(query)
        return [DimFornecedorResponse(**dict(row)) for row in results]
        
    except Exception as e:
        logger.error(f"Erro ao buscar fornecedores: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/contas/{conta_id}", response_model=DimContaResponse)
async def get_conta_by_id(conta_id: str):
    """Retorna uma conta específica pelo ID."""
    try:
        query = """
        SELECT sk_conta, id_conta_origem, nome_conta, tipo_conta, grupo_conta 
        FROM dim_contas 
        WHERE sk_conta = %s OR id_conta_origem = %s
        """
        results = DatabaseManager.execute_query(query, (conta_id, conta_id))
        
        if not results:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
            
        return DimContaResponse(**dict(results[0]))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar conta {conta_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")