from __future__ import annotations

from datetime import date
from typing import Optional, Dict, Any, List

from repositories.base_repo import BaseRepository


class PosVendaRepository(BaseRepository):

    def kpis_servicos(self, dt_ini: date, dt_fim: date,
                      cod_concessionaria: Optional[int] = None,
                      cod_filial: Optional[int] = None) -> Dict[str, Any]:
        sql = """
        SELECT
          COUNT(*) AS REGISTROS,
          SUM(NVL(QTDE_SERVICOS,0)) AS QTDE_SERVICOS,
          SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA_SERVICOS,
          SUM(NVL(LUCRO_SERVICO,0)) AS LUCRO_SERVICOS,
          CASE WHEN SUM(NVL(VALOR_TOTAL_SERVICO,0)) = 0 THEN NULL
               ELSE SUM(NVL(LUCRO_SERVICO,0))/SUM(NVL(VALOR_TOTAL_SERVICO,0))
          END AS MARGEM_SERVICOS,
          AVG(NVL(VALOR_TOTAL_SERVICO,0)) AS TICKET_MEDIO_POR_REGISTRO,
          AVG(NVL(QTDE_SERVICOS,0)) AS QTDE_MEDIA_SERVICOS_POR_REGISTRO
        FROM BRZ_HIST_SERVICOS
        WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
          AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
          AND (:cod_filial IS NULL OR COD_FILIAL = :cod_filial)
        """

        params = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "cod_concessionaria": cod_concessionaria,
            "cod_filial": cod_filial,
        }
        return self.query_one(sql, params)

    def por_departamento(self, dt_ini: date, dt_fim: date,
                         cod_concessionaria: Optional[int] = None,
                         cod_filial: Optional[int] = None,
                         top_n: int = 20) -> List[Dict[str, Any]]:
        sql = f"""
        SELECT
          DEPARTAMENTO_SERVICO,
          SUM(NVL(QTDE_SERVICOS,0)) AS QTDE_SERVICOS,
          SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA,
          SUM(NVL(LUCRO_SERVICO,0)) AS LUCRO,
          CASE WHEN SUM(NVL(VALOR_TOTAL_SERVICO,0)) = 0 THEN NULL
               ELSE SUM(NVL(LUCRO_SERVICO,0))/SUM(NVL(VALOR_TOTAL_SERVICO,0))
          END AS MARGEM
        FROM BRZ_HIST_SERVICOS
        WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
          AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
          AND (:cod_filial IS NULL OR COD_FILIAL = :cod_filial)
        GROUP BY DEPARTAMENTO_SERVICO
        ORDER BY RECEITA DESC NULLS LAST
        FETCH FIRST {int(top_n)} ROWS ONLY
        """
        params = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "cod_concessionaria": cod_concessionaria,
            "cod_filial": cod_filial,
        }
        return self.query_dicts(sql, params)

    def por_categoria_servico(self, dt_ini: date, dt_fim: date,
                             cod_concessionaria: Optional[int] = None,
                             cod_filial: Optional[int] = None,
                             top_n: int = 20) -> List[Dict[str, Any]]:
        sql = f"""
        SELECT
          CATEGORIA_SERVICO,
          SUM(NVL(QTDE_SERVICOS,0)) AS QTDE_SERVICOS,
          SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA,
          SUM(NVL(LUCRO_SERVICO,0)) AS LUCRO,
          CASE WHEN SUM(NVL(VALOR_TOTAL_SERVICO,0)) = 0 THEN NULL
               ELSE SUM(NVL(LUCRO_SERVICO,0))/SUM(NVL(VALOR_TOTAL_SERVICO,0))
          END AS MARGEM
        FROM BRZ_HIST_SERVICOS
        WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
          AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
          AND (:cod_filial IS NULL OR COD_FILIAL = :cod_filial)
        GROUP BY CATEGORIA_SERVICO
        ORDER BY LUCRO DESC NULLS LAST
        FETCH FIRST {int(top_n)} ROWS ONLY
        """
        params = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "cod_concessionaria": cod_concessionaria,
            "cod_filial": cod_filial,
        }
        return self.query_dicts(sql, params)
