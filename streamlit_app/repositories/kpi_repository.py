from __future__ import annotations

from datetime import date
from typing import Optional, Dict, Any, List
from datetime import date

from repositories.base_repo import BaseRepository


class KpiRepository(BaseRepository):
    def kpis_gerais_periodo(
        self,
        dt_ini: date,
        dt_fim: date,
        cod_concessionaria: Optional[int] = None,
        cod_filial: Optional[int] = None,
    ) -> Dict[str, Any]:

        sql = """
        WITH
        v_veic AS (
            SELECT
                SUM(NVL(VALOR_VENDA,0)) AS RECEITA_VEIC,
                SUM(NVL(LUCRO_VENDA,0)) AS LUCRO_VEIC
            FROM BRZ_HIST_VENDAS_VEICULOS
            WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
              AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
              AND (:cod_filial IS NULL OR COD_FILIAL = :cod_filial)
        ),
        v_pec AS (
            SELECT
                SUM(NVL(VALOR_VENDA,0)) AS RECEITA_PEC,
                SUM(NVL(LUCRO_VENDA,0)) AS LUCRO_PEC
            FROM BRZ_HIST_VENDAS_PECAS
            WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
              AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
              AND (:cod_filial IS NULL OR COD_FILIAL = :cod_filial)
        ),
        v_srv AS (
            SELECT
                SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA_SRV,
                SUM(NVL(LUCRO_SERVICO,0)) AS LUCRO_SRV
            FROM BRZ_HIST_SERVICOS
            WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
              AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
              AND (:cod_filial IS NULL OR COD_FILIAL = :cod_filial)
        ),
        v_est AS (
            SELECT
                SUM(NVL(VALOR_PECA_ESTOQUE,0)) AS VALOR_ESTOQUE_PEC
            FROM BRZ_ESTOQUE_PECAS
            WHERE (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
              AND (:cod_filial IS NULL OR COD_FILIAL = :cod_filial)
        )
        SELECT
            (v_veic.RECEITA_VEIC + v_pec.RECEITA_PEC + v_srv.RECEITA_SRV) AS RECEITA_TOTAL,
            (v_veic.LUCRO_VEIC   + v_pec.LUCRO_PEC   + v_srv.LUCRO_SRV)   AS LUCRO_TOTAL,
            v_veic.RECEITA_VEIC, v_veic.LUCRO_VEIC,
            v_pec.RECEITA_PEC,   v_pec.LUCRO_PEC,
            v_srv.RECEITA_SRV,   v_srv.LUCRO_SRV,
            v_est.VALOR_ESTOQUE_PEC
        FROM v_veic, v_pec, v_srv, v_est
        """

        params: Dict[str, Any] = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "cod_concessionaria": cod_concessionaria,
            "cod_filial": cod_filial,
        }

        return self.query_one(sql, params)

    def receita_mensal_total(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        sql = """
        WITH
        veic AS (
            SELECT TRUNC(DT_VENDA, 'MM') AS MES, SUM(NVL(VALOR_VENDA,0)) AS RECEITA
            FROM BRZ_HIST_VENDAS_VEICULOS
            WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
            GROUP BY TRUNC(DT_VENDA, 'MM')
        ),
        pec AS (
            SELECT TRUNC(DT_VENDA, 'MM') AS MES, SUM(NVL(VALOR_VENDA,0)) AS RECEITA
            FROM BRZ_HIST_VENDAS_PECAS
            WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
            GROUP BY TRUNC(DT_VENDA, 'MM')
        ),
        srv AS (
            SELECT TRUNC(DT_REALIZACAO_SERVICO, 'MM') AS MES, SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA
            FROM BRZ_HIST_SERVICOS
            WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
            GROUP BY TRUNC(DT_REALIZACAO_SERVICO, 'MM')
        )
        SELECT
            MES,
            SUM(RECEITA) AS RECEITA_TOTAL
        FROM (
            SELECT * FROM veic
            UNION ALL
            SELECT * FROM pec
            UNION ALL
            SELECT * FROM srv
        )
        GROUP BY MES
        ORDER BY MES
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})