"""
Cliente para SEC EDGAR API
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import config

logger = logging.getLogger(__name__)

class SECClient:
    """Cliente para acessar dados da SEC EDGAR API"""
    
    def __init__(self):
        self.base_url = config.sec.base_url
        self.headers = {
            'User-Agent': config.sec.user_agent,
            'Accept': 'application/json'
        }
        
    async def get_company_facts(self, cik: str) -> Optional[Dict[str, Any]]:
        """Busca company facts da SEC para um CIK específico"""
        cik_formatted = cik.zfill(10)
        url = f"{self.base_url}/CIK{cik_formatted}.json"
        
        async with aiohttp.ClientSession() as session:
            try:
                logger.info(f"Buscando dados SEC para CIK {cik}")
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Dados obtidos para CIK {cik}")
                        return data
                    else:
                        logger.error(f"Erro HTTP {response.status} para CIK {cik}")
                        return None
                        
            except Exception as e:
                logger.error(f"Erro ao buscar CIK {cik}: {e}")
                return None

    async def test_connection(self) -> bool:
        """Testa conexão com SEC usando Apple como exemplo"""
        try:
            result = await self.get_company_facts('0000320193')
            return result is not None
        except Exception:
            return False
