from __future__ import annotations

from typing import Dict, Any, List

from repositories.base_repo import BaseRepository


class DashboardOperacionalRepository(BaseRepository):

    def kpis_vendas_veiculos_diario(self) -> Dict[str, Any]:
        sql = """
        WITH
        hoje AS (
          SELECT
            SUM(NVL(QTDE_VENDIDA,0)) AS QTD,
            SUM(NVL(VALOR_VENDA,0)) AS RECEITA,
            SUM(NVL(LUCRO_VENDA,0)) AS LUCRO
          FROM BRZ_HIST_VENDAS_VEICULOS
          WHERE TRUNC(DT_VENDA) = TRUNC(SYSDATE)
        ),
        ontem AS (
          SELECT
            SUM(NVL(QTDE_VENDIDA,0)) AS QTD,
            SUM(NVL(VALOR_VENDA,0)) AS RECEITA,
            SUM(NVL(LUCRO_VENDA,0)) AS LUCRO
          FROM BRZ_HIST_VENDAS_VEICULOS
          WHERE TRUNC(DT_VENDA) = TRUNC(SYSDATE-1)
        ),
        m30 AS (
          SELECT
            AVG(QTD_DIA) AS QTD_MEDIA_30D,
            AVG(RECEITA_DIA) AS RECEITA_MEDIA_30D
          FROM (
            SELECT
              TRUNC(DT_VENDA) AS DIA,
              SUM(NVL(QTDE_VENDIDA,0)) AS QTD_DIA,
              SUM(NVL(VALOR_VENDA,0)) AS RECEITA_DIA
            FROM BRZ_HIST_VENDAS_VEICULOS
            WHERE TRUNC(DT_VENDA) BETWEEN TRUNC(SYSDATE)-30 AND TRUNC(SYSDATE)-1
            GROUP BY TRUNC(DT_VENDA)
          )
        )
        SELECT
          h.QTD AS QTD_HOJE,
          o.QTD AS QTD_ONTEM,
          m.QTD_MEDIA_30D,
          h.RECEITA AS RECEITA_HOJE,
          o.RECEITA AS RECEITA_ONTEM,
          m.RECEITA_MEDIA_30D
        FROM hoje h, ontem o, m30 m
        """
        return self.query_one(sql, {})

    def kpis_vendas_pecas_diario(self) -> Dict[str, Any]:
        sql = """
        WITH
        hoje AS (
          SELECT
            SUM(NVL(QTDE_VENDIDA,0)) AS QTD,
            SUM(NVL(VALOR_VENDA,0)) AS RECEITA,
            SUM(NVL(LUCRO_VENDA,0)) AS LUCRO
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE TRUNC(DT_VENDA) = TRUNC(SYSDATE)
        ),
        m30 AS (
          SELECT
            AVG(QTD_DIA) AS QTD_MEDIA_30D,
            AVG(RECEITA_DIA) AS RECEITA_MEDIA_30D,
            AVG(MARGEM_DIA) AS MARGEM_MEDIA_30D
          FROM (
            SELECT
              TRUNC(DT_VENDA) AS DIA,
              SUM(NVL(QTDE_VENDIDA,0)) AS QTD_DIA,
              SUM(NVL(VALOR_VENDA,0)) AS RECEITA_DIA,
              CASE WHEN SUM(NVL(VALOR_VENDA,0))=0 THEN NULL
                   ELSE SUM(NVL(LUCRO_VENDA,0))/SUM(NVL(VALOR_VENDA,0))
              END AS MARGEM_DIA
            FROM BRZ_HIST_VENDAS_PECAS
            WHERE TRUNC(DT_VENDA) BETWEEN TRUNC(SYSDATE)-30 AND TRUNC(SYSDATE)-1
            GROUP BY TRUNC(DT_VENDA)
          )
        )
        SELECT
          h.QTD AS QTD_HOJE,
          h.RECEITA AS RECEITA_HOJE,
          CASE WHEN h.RECEITA=0 THEN NULL ELSE h.LUCRO/h.RECEITA END AS MARGEM_HOJE,
          m.QTD_MEDIA_30D,
          m.RECEITA_MEDIA_30D,
          m.MARGEM_MEDIA_30D
        FROM hoje h, m30 m
        """
        return self.query_one(sql, {})

    def top10_pecas_hoje(self) -> List[Dict[str, Any]]:
        sql = """
        SELECT
          DESCRICAO_PECA,
          SUM(NVL(QTDE_VENDIDA,0)) AS QTD,
          SUM(NVL(VALOR_VENDA,0)) AS RECEITA
        FROM BRZ_HIST_VENDAS_PECAS
        WHERE TRUNC(DT_VENDA) = TRUNC(SYSDATE)
        GROUP BY DESCRICAO_PECA
        ORDER BY QTD DESC, RECEITA DESC
        FETCH FIRST 10 ROWS ONLY
        """
        return self.query_dicts(sql, {})

    def kpis_servicos_diario(self) -> Dict[str, Any]:
        sql = """
        WITH
        hoje AS (
          SELECT
            SUM(NVL(QTDE_SERVICOS,0)) AS QTD,
            SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA,
            SUM(NVL(LUCRO_SERVICO,0)) AS LUCRO
          FROM BRZ_HIST_SERVICOS
          WHERE TRUNC(DT_REALIZACAO_SERVICO) = TRUNC(SYSDATE)
        ),
        m30 AS (
          SELECT
            AVG(QTD_DIA) AS QTD_MEDIA_30D,
            AVG(RECEITA_DIA) AS RECEITA_MEDIA_30D
          FROM (
            SELECT
              TRUNC(DT_REALIZACAO_SERVICO) AS DIA,
              SUM(NVL(QTDE_SERVICOS,0)) AS QTD_DIA,
              SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA_DIA
            FROM BRZ_HIST_SERVICOS
            WHERE TRUNC(DT_REALIZACAO_SERVICO) BETWEEN TRUNC(SYSDATE)-30 AND TRUNC(SYSDATE)-1
            GROUP BY TRUNC(DT_REALIZACAO_SERVICO)
          )
        )
        SELECT
          h.QTD AS QTD_HOJE,
          m.QTD_MEDIA_30D,
          h.RECEITA AS RECEITA_HOJE,
          m.RECEITA_MEDIA_30D
        FROM hoje h, m30 m
        """
        return self.query_one(sql, {})
