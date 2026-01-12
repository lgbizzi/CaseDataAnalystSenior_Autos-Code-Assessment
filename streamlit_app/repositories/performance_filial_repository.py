from __future__ import annotations

from datetime import date
from typing import Optional, Dict, Any, List

from repositories.base_repo import BaseRepository


class PerformanceFilialRepository(BaseRepository):

    def performance_por_filial(
        self,
        dt_ini: date,
        dt_fim: date,
        cod_concessionaria: Optional[int] = None,
        top_n: int = 50,
    ) -> List[Dict[str, Any]]:

        sql = f"""
        WITH
        veic AS (
            SELECT
              COD_CONCESSIONARIA,
              COD_FILIAL,
              NOME_FILIAL,
              SUM(NVL(QTDE_VENDIDA,0)) AS VEIC_QTD,
              SUM(NVL(VALOR_VENDA,0)) AS VEIC_RECEITA,
              SUM(NVL(LUCRO_VENDA,0)) AS VEIC_LUCRO
            FROM BRZ_HIST_VENDAS_VEICULOS
            WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
              AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
            GROUP BY COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL
        ),
        pec AS (
            SELECT
              COD_CONCESSIONARIA,
              COD_FILIAL,
              NOME_FILIAL,
              SUM(NVL(QTDE_VENDIDA,0)) AS PEC_QTD,
              SUM(NVL(VALOR_VENDA,0)) AS PEC_RECEITA,
              SUM(NVL(LUCRO_VENDA,0)) AS PEC_LUCRO
            FROM BRZ_HIST_VENDAS_PECAS
            WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
              AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
            GROUP BY COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL
        ),
        srv AS (
            SELECT
              COD_CONCESSIONARIA,
              COD_FILIAL,
              NOME_FILIAL,
              SUM(NVL(QTDE_SERVICOS,0)) AS SRV_QTD,
              SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS SRV_RECEITA,
              SUM(NVL(LUCRO_SERVICO,0)) AS SRV_LUCRO
            FROM BRZ_HIST_SERVICOS
            WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
              AND (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
            GROUP BY COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL
        ),
        est_pec AS (
            SELECT
              COD_CONCESSIONARIA,
              COD_FILIAL,
              NOME_FILIAL,
              SUM(NVL(VALOR_PECA_ESTOQUE,0)) AS ESTOQUE_PECAS
            FROM BRZ_ESTOQUE_PECAS
            WHERE (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
            GROUP BY COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL
        ),
        est_veic AS (
            SELECT
              COD_CONCESSIONARIA,
              COD_FILIAL,
              NOME_FILIAL,
              SUM(NVL(CUSTO_VEICULO,0)) AS ESTOQUE_VEICULOS
            FROM BRZ_ESTOQUE_VEICULOS
            WHERE (:cod_concessionaria IS NULL OR COD_CONCESSIONARIA = :cod_concessionaria)
            GROUP BY COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL
        ),
        base AS (
            SELECT COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL FROM veic
            UNION
            SELECT COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL FROM pec
            UNION
            SELECT COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL FROM srv
            UNION
            SELECT COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL FROM est_pec
            UNION
            SELECT COD_CONCESSIONARIA, COD_FILIAL, NOME_FILIAL FROM est_veic
        )
        SELECT
          b.COD_CONCESSIONARIA,
          b.COD_FILIAL,
          b.NOME_FILIAL,

          NVL(v.VEIC_QTD,0) AS VEIC_QTD,
          NVL(v.VEIC_RECEITA,0) AS VEIC_RECEITA,
          NVL(v.VEIC_LUCRO,0) AS VEIC_LUCRO,
          CASE WHEN NVL(v.VEIC_RECEITA,0) = 0 THEN NULL ELSE NVL(v.VEIC_LUCRO,0)/NVL(v.VEIC_RECEITA,0) END AS VEIC_MARGEM,

          NVL(p.PEC_QTD,0) AS PEC_QTD,
          NVL(p.PEC_RECEITA,0) AS PEC_RECEITA,
          NVL(p.PEC_LUCRO,0) AS PEC_LUCRO,
          CASE WHEN NVL(p.PEC_RECEITA,0) = 0 THEN NULL ELSE NVL(p.PEC_LUCRO,0)/NVL(p.PEC_RECEITA,0) END AS PEC_MARGEM,

          NVL(s.SRV_QTD,0) AS SRV_QTD,
          NVL(s.SRV_RECEITA,0) AS SRV_RECEITA,
          NVL(s.SRV_LUCRO,0) AS SRV_LUCRO,
          CASE WHEN NVL(s.SRV_RECEITA,0) = 0 THEN NULL ELSE NVL(s.SRV_LUCRO,0)/NVL(s.SRV_RECEITA,0) END AS SRV_MARGEM,

          (NVL(v.VEIC_LUCRO,0) + NVL(p.PEC_LUCRO,0) + NVL(s.SRV_LUCRO,0)) AS LUCRO_TOTAL,
          (NVL(v.VEIC_RECEITA,0) + NVL(p.PEC_RECEITA,0) + NVL(s.SRV_RECEITA,0)) AS RECEITA_TOTAL,

          NVL(ev.ESTOQUE_VEICULOS,0) AS ESTOQUE_VEICULOS,
          NVL(ep.ESTOQUE_PECAS,0) AS ESTOQUE_PECAS,
          (NVL(ev.ESTOQUE_VEICULOS,0) + NVL(ep.ESTOQUE_PECAS,0)) AS CAPITAL_ESTOQUE,

          CASE
            WHEN (NVL(ev.ESTOQUE_VEICULOS,0) + NVL(ep.ESTOQUE_PECAS,0)) = 0 THEN NULL
            ELSE (NVL(v.VEIC_LUCRO,0) + NVL(p.PEC_LUCRO,0) + NVL(s.SRV_LUCRO,0))
                 / (NVL(ev.ESTOQUE_VEICULOS,0) + NVL(ep.ESTOQUE_PECAS,0))
          END AS ROI_ESTOQUE

        FROM base b
        LEFT JOIN veic v ON v.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA AND v.COD_FILIAL = b.COD_FILIAL
        LEFT JOIN pec  p ON p.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA AND p.COD_FILIAL = b.COD_FILIAL
        LEFT JOIN srv  s ON s.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA AND s.COD_FILIAL = b.COD_FILIAL
        LEFT JOIN est_veic ev ON ev.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA AND ev.COD_FILIAL = b.COD_FILIAL
        LEFT JOIN est_pec  ep ON ep.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA AND ep.COD_FILIAL = b.COD_FILIAL
        ORDER BY ROI_ESTOQUE DESC NULLS LAST, LUCRO_TOTAL DESC
        FETCH FIRST {int(top_n)} ROWS ONLY
        """

        params: Dict[str, Any] = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "cod_concessionaria": cod_concessionaria,
        }
        return self.query_dicts(sql, params)
