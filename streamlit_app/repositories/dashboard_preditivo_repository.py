from __future__ import annotations

from datetime import date
from typing import Dict, Any, List

from repositories.base_repo import BaseRepository


class DashboardPreditivoRepository(BaseRepository):

    def serie_diaria_veiculos_unidades(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        sql = """
        SELECT
          TRUNC(DT_VENDA) AS DIA,
          SUM(NVL(QTDE_VENDIDA,0)) AS Y
        FROM BRZ_HIST_VENDAS_VEICULOS
        WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
        GROUP BY TRUNC(DT_VENDA)
        ORDER BY DIA
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})

    def serie_diaria_pecas_receita(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        sql = """
        SELECT
          TRUNC(DT_VENDA) AS DIA,
          SUM(NVL(VALOR_VENDA,0)) AS Y
        FROM BRZ_HIST_VENDAS_PECAS
        WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
        GROUP BY TRUNC(DT_VENDA)
        ORDER BY DIA
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})

    def serie_diaria_servicos_receita(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        sql = """
        SELECT
          TRUNC(DT_REALIZACAO_SERVICO) AS DIA,
          SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS Y
        FROM BRZ_HIST_SERVICOS
        WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
        GROUP BY TRUNC(DT_REALIZACAO_SERVICO)
        ORDER BY DIA
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})

    def risco_falta_pecas_30d(self, dias_media: int = 30, top_n: int = 30) -> List[Dict[str, Any]]:
        """
        Heurística:
        - consumo_medio_diario = (qtde vendida nos últimos N dias) / N
        - dias_de_cobertura = estoque_atual / consumo_medio_diario
        - risco se dias_de_cobertura <= 30
        """
        sql = f"""
        WITH vendas AS (
          SELECT
            DESCRICAO_PECA,
            CATEGORIA_PECA,
            SUM(NVL(QTDE_VENDIDA,0)) AS QTD_{dias_media}D
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE DT_VENDA >= TRUNC(SYSDATE) - :dias_media
          GROUP BY DESCRICAO_PECA, CATEGORIA_PECA
        ),
        est AS (
          SELECT
            DESCRICAO_PECA,
            CATEGORIA_PECA,
            SUM(NVL(QTDE_PECA_ESTOQUE,0)) AS ESTOQUE_ATUAL
          FROM BRZ_ESTOQUE_PECAS
          GROUP BY DESCRICAO_PECA, CATEGORIA_PECA
        ),
        base AS (
          SELECT DESCRICAO_PECA, CATEGORIA_PECA FROM vendas
          UNION
          SELECT DESCRICAO_PECA, CATEGORIA_PECA FROM est
        )
        SELECT
          b.CATEGORIA_PECA,
          b.DESCRICAO_PECA,
          NVL(e.ESTOQUE_ATUAL,0) AS ESTOQUE_ATUAL,
          NVL(v.QTD_{dias_media}D,0) AS VENDAS_{dias_media}D,
          (NVL(v.QTD_{dias_media}D,0) / :dias_media) AS CONSUMO_MEDIO_DIA,
          CASE
            WHEN (NVL(v.QTD_{dias_media}D,0) / :dias_media) = 0 THEN NULL
            ELSE NVL(e.ESTOQUE_ATUAL,0) / (NVL(v.QTD_{dias_media}D,0) / :dias_media)
          END AS DIAS_COBERTURA
        FROM base b
        LEFT JOIN vendas v ON v.DESCRICAO_PECA = b.DESCRICAO_PECA AND v.CATEGORIA_PECA = b.CATEGORIA_PECA
        LEFT JOIN est e ON e.DESCRICAO_PECA = b.DESCRICAO_PECA AND e.CATEGORIA_PECA = b.CATEGORIA_PECA
        WHERE NVL(e.ESTOQUE_ATUAL,0) > 0
          AND NVL(v.QTD_{dias_media}D,0) > 0
          AND (NVL(e.ESTOQUE_ATUAL,0) / (NVL(v.QTD_{dias_media}D,0) / :dias_media)) <= 30
        ORDER BY DIAS_COBERTURA ASC
        FETCH FIRST {int(top_n)} ROWS ONLY
        """
        return self.query_dicts(sql, {"dias_media": int(dias_media)})

    def pecas_obsoletas(self, top_n: int = 50) -> List[Dict[str, Any]]:
        sql = f"""
        SELECT
        CATEGORIA_PECA,
        DESCRICAO_PECA,
        CODIGO_PECA_ESTOQUE,
        QTDE_PECA_ESTOQUE,
        VALOR_PECA_ESTOQUE,
        PECA_OBSOLETA_FLAG,
        TEMPO_OBSOLETA_DIAS,
        DT_ULTIMA_VENDA_PECA
        FROM BRZ_ESTOQUE_PECAS
        WHERE
        (
            UPPER(TRIM(PECA_OBSOLETA_FLAG)) IN ('SIM','S','Y','YES','1','TRUE')
            OR NVL(TEMPO_OBSOLETA_DIAS,0) >= 60
        )
        ORDER BY NVL(TEMPO_OBSOLETA_DIAS,0) DESC, NVL(VALOR_PECA_ESTOQUE,0) DESC
        FETCH FIRST {int(top_n)} ROWS ONLY
        """
        return self.query_dicts(sql, {})

