from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
from app.models import (
    FatoLancamentoResponse, FatoCaixaResponse, 
    ResumoFinanceiroResponse, AnaliseContaResponse, DateRangeFilter
)
from app.database import DatabaseManager
import logging

router = APIRouter(prefix="/fatos", tags=["Fatos"])
logger = logging.getLogger(__name__)

@router.get("/lancamentos", response_model=List[FatoLancamentoResponse])
async def get_lancamentos(
    data_inicio: Optional[date] = Query(None, description="Data inicial"),
    data_fim: Optional[date] = Query(None, description="Data final"),
    conta_id: Optional[str] = Query(None, description="ID da conta"),
    centro_custo_id: Optional[str] = Query(None, description="ID do centro de custo"),
    limit: int = Query(100, le=1000, description="Limite de registros")
):
    """Retorna lançamentos contábeis com filtros."""
    try:
        query = """
        SELECT 
            fl.sk_tempo, fl.sk_conta, fl.sk_centro_custo,
            fl.sk_produto, fl.sk_fornecedor,
            fl.valor, fl.descricao, fl.origem_dados
        FROM fato_lancamentos fl
        JOIN dim_tempo dt ON fl.sk_tempo = dt.sk_tempo
        WHERE 1=1
        """
        params = []
        
        if data_inicio:
            query += " AND dt.data >= %s"
            params.append(data_inicio)
            
        if data_fim:
            query += " AND dt.data <= %s"
            params.append(data_fim)
            
        if conta_id:
            query += " AND fl.sk_conta = %s"
            params.append(conta_id)
            
        if centro_custo_id:
            query += " AND fl.sk_centro_custo = %s"
            params.append(centro_custo_id)
            
        query += " ORDER BY dt.data DESC LIMIT %s"
        params.append(limit)
        
        results = DatabaseManager.execute_query(query, tuple(params))
        return [FatoLancamentoResponse(**dict(row)) for row in results]
        
    except Exception as e:
        logger.error(f"Erro ao buscar lançamentos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/caixa", response_model=List[FatoCaixaResponse])
async def get_caixa(
    data_inicio: Optional[date] = Query(None, description="Data inicial"),
    data_fim: Optional[date] = Query(None, description="Data final"),
    limit: int = Query(100, le=1000, description="Limite de registros")
):
    """Retorna movimentação de caixa."""
    try:
        query = """
        SELECT 
            fc.sk_tempo, fc.sk_conta, fc.sk_centro_custo,
            fc.valor_entrada, fc.valor_saida, fc.saldo,
            fc.descricao, fc.origem_dados
        FROM fato_caixa fc
        JOIN dim_tempo dt ON fc.sk_tempo = dt.sk_tempo
        WHERE 1=1
        """
        params = []
        
        if data_inicio:
            query += " AND dt.data >= %s"
            params.append(data_inicio)
            
        if data_fim:
            query += " AND dt.data <= %s"
            params.append(data_fim)
            
        query += " ORDER BY dt.data DESC LIMIT %s"
        params.append(limit)
        
        results = DatabaseManager.execute_query(query, tuple(params))
        return [FatoCaixaResponse(**dict(row)) for row in results]
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados de caixa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/resumo-financeiro", response_model=List[ResumoFinanceiroResponse])
async def get_resumo_financeiro(
    data_inicio: Optional[date] = Query(None, description="Data inicial"),
    data_fim: Optional[date] = Query(None, description="Data final"),
    agrupamento: str = Query("mensal", regex="^(diario|mensal|trimestral|anual)$", 
                           description="Tipo de agrupamento")
):
    """Retorna resumo financeiro agregado por período."""
    try:
        # Define o agrupamento SQL baseado no parâmetro
        date_group = {
            "diario": "dt.data",
            "mensal": "CONCAT(dt.ano, '-', LPAD(dt.mes::text, 2, '0'))",
            "trimestral": "CONCAT(dt.ano, '-Q', dt.trimestre)",
            "anual": "dt.ano::text"
        }[agrupamento]
        
        query = f"""
        SELECT 
            {date_group} as periodo,
            COALESCE(SUM(CASE WHEN dc.tipo_conta = 'Receita' THEN fl.valor ELSE 0 END), 0) as total_receitas,
            COALESCE(SUM(CASE WHEN dc.tipo_conta = 'Despesa' THEN ABS(fl.valor) ELSE 0 END), 0) as total_despesas,
            COALESCE(SUM(CASE WHEN dc.tipo_conta = 'Receita' THEN fl.valor 
                             WHEN dc.tipo_conta = 'Despesa' THEN -ABS(fl.valor) 
                             ELSE 0 END), 0) as resultado
        FROM fato_lancamentos fl
        JOIN dim_tempo dt ON fl.sk_tempo = dt.sk_tempo
        JOIN dim_contas dc ON fl.sk_conta = dc.sk_conta
        WHERE 1=1
        """
        params = []
        
        if data_inicio:
            query += " AND dt.data >= %s"
            params.append(data_inicio)
            
        if data_fim:
            query += " AND dt.data <= %s"
            params.append(data_fim)
            
        query += f" GROUP BY {date_group} ORDER BY periodo"
        
        results = DatabaseManager.execute_query(query, tuple(params) if params else None)
        
        # Calcula margem percentual
        response_data = []
        for row in results:
            row_dict = dict(row)
            receitas = float(row_dict['total_receitas'])
            despesas = float(row_dict['total_despesas'])
            resultado = float(row_dict['resultado'])
            
            margem = (resultado / receitas * 100) if receitas > 0 else None
            row_dict['margem_percentual'] = margem
            
            response_data.append(ResumoFinanceiroResponse(**row_dict))
            
        return response_data
        
    except Exception as e:
        logger.error(f"Erro ao buscar resumo financeiro: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/analise-contas", response_model=List[AnaliseContaResponse])
async def get_analise_contas(
    data_inicio: Optional[date] = Query(None, description="Data inicial"),
    data_fim: Optional[date] = Query(None, description="Data final"),
    tipo_conta: Optional[str] = Query(None, description="Filtrar por tipo de conta"),
    top_n: int = Query(10, le=50, description="Top N contas por valor")
):
    """Retorna análise das principais contas por valor."""
    try:
        query = """
        WITH conta_valores AS (
            SELECT 
                dc.sk_conta, dc.id_conta_origem, dc.nome_conta, dc.tipo_conta, dc.grupo_conta,
                SUM(ABS(fl.valor)) as valor_periodo
            FROM fato_lancamentos fl
            JOIN dim_tempo dt ON fl.sk_tempo = dt.sk_tempo
            JOIN dim_contas dc ON fl.sk_conta = dc.sk_conta
            WHERE 1=1
        """
        params = []
        
        if data_inicio:
            query += " AND dt.data >= %s"
            params.append(data_inicio)
            
        if data_fim:
            query += " AND dt.data <= %s"
            params.append(data_fim)
            
        if tipo_conta:
            query += " AND dc.tipo_conta = %s"
            params.append(tipo_conta)
            
        query += """
            GROUP BY dc.sk_conta, dc.id_conta_origem, dc.nome_conta, dc.tipo_conta, dc.grupo_conta
        ),
        total_geral AS (
            SELECT SUM(valor_periodo) as total FROM conta_valores
        )
        SELECT 
            cv.*,
            ROUND((cv.valor_periodo / tg.total * 100)::numeric, 2) as percentual_total
        FROM conta_valores cv
        CROSS JOIN total_geral tg
        ORDER BY cv.valor_periodo DESC
        LIMIT %s
        """
        params.append(top_n)
        
        results = DatabaseManager.execute_query(query, tuple(params))
        
        response_data = []
        for row in results:
            row_dict = dict(row)
            conta_data = {
                'sk_conta': row_dict['sk_conta'],
                'id_conta_origem': row_dict['id_conta_origem'],
                'nome_conta': row_dict['nome_conta'],
                'tipo_conta': row_dict['tipo_conta'],
                'grupo_conta': row_dict['grupo_conta']
            }
            
            analysis_data = {
                'conta': conta_data,
                'valor_periodo': row_dict['valor_periodo'],
                'percentual_total': float(row_dict['percentual_total'])
            }
            
            response_data.append(AnaliseContaResponse(**analysis_data))
            
        return response_data
        
    except Exception as e:
        logger.error(f"Erro ao buscar análise de contas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/kpis")
async def get_kpis(
    data_inicio: Optional[date] = Query(None, description="Data inicial"),
    data_fim: Optional[date] = Query(None, description="Data final")
):
    """Retorna KPIs financeiros principais."""
    try:
        query = """
        SELECT 
            COUNT(*) as total_lancamentos,
            SUM(CASE WHEN dc.tipo_conta = 'Receita' THEN fl.valor ELSE 0 END) as receitas_total,
            SUM(CASE WHEN dc.tipo_conta = 'Despesa' THEN ABS(fl.valor) ELSE 0 END) as despesas_total,
            COUNT(DISTINCT dc.sk_conta) as contas_ativas,
            COUNT(DISTINCT dcc.sk_centro_custo) as centros_custo_ativos,
            AVG(ABS(fl.valor)) as ticket_medio_transacao
        FROM fato_lancamentos fl
        JOIN dim_tempo dt ON fl.sk_tempo = dt.sk_tempo
        JOIN dim_contas dc ON fl.sk_conta = dc.sk_conta
        LEFT JOIN dim_centros_custo dcc ON fl.sk_centro_custo = dcc.sk_centro_custo
        WHERE 1=1
        """
        params = []
        
        if data_inicio:
            query += " AND dt.data >= %s"
            params.append(data_inicio)
            
        if data_fim:
            query += " AND dt.data <= %s"
            params.append(data_fim)
        
        results = DatabaseManager.execute_query(query, tuple(params) if params else None)
        
        if not results:
            return {"message": "Nenhum dado encontrado para o período"}
            
        kpis = dict(results[0])
        
        # Calcula KPIs derivados
        receitas = float(kpis.get('receitas_total', 0))
        despesas = float(kpis.get('despesas_total', 0))
        resultado = receitas - despesas
        margem = (resultado / receitas * 100) if receitas > 0 else 0
        
        kpis.update({
            'resultado_liquido': resultado,
            'margem_liquida': round(margem, 2),
            'ticket_medio_transacao': round(float(kpis.get('ticket_medio_transacao', 0)), 2)
        })
        
        return kpis
        
    except Exception as e:
        logger.error(f"Erro ao buscar KPIs: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")