from __future__ import annotations

from datetime import date
from typing import Dict, Any, List

from repositories.base_repo import BaseRepository


class ClientesRepository(BaseRepository):

    def funil_clientes(self) -> Dict[str, Any]:
        sql = """
        WITH
        veic AS (
          SELECT DISTINCT UPPER(TRIM(NOME_COMPRADOR)) AS CLIENTE
          FROM BRZ_HIST_VENDAS_VEICULOS
          WHERE DT_VENDA >= DATE '2023-01-01' AND DT_VENDA < DATE '2024-01-01'
            AND NOME_COMPRADOR IS NOT NULL
        ),
        srv AS (
          SELECT DISTINCT UPPER(TRIM(NOME_CLIENTE)) AS CLIENTE
          FROM BRZ_HIST_SERVICOS
          WHERE DT_REALIZACAO_SERVICO >= DATE '2023-01-01' AND DT_REALIZACAO_SERVICO < DATE '2024-01-01'
            AND NOME_CLIENTE IS NOT NULL
        ),
        pec AS (
          SELECT DISTINCT UPPER(TRIM(NOME_COMPRADOR)) AS CLIENTE
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE DT_VENDA >= DATE '2023-01-01' AND DT_VENDA < DATE '2024-01-01'
            AND NOME_COMPRADOR IS NOT NULL
        )
        SELECT
          (SELECT COUNT(*) FROM veic) AS CLIENTES_VEIC_2023,
          (SELECT COUNT(*) FROM veic v JOIN srv s ON s.CLIENTE = v.CLIENTE) AS COM_SERVICO_POSTERIOR,
          (SELECT COUNT(*) FROM veic v JOIN pec p ON p.CLIENTE = v.CLIENTE) AS COM_COMPRA_PECAS
        FROM dual
        """
        return self.query_one(sql, {})

    def ltv_por_cliente(self, dt_ini: date, dt_fim: date, top_n: int = 50) -> List[Dict[str, Any]]:
        sql = f"""
        WITH
        tx AS (
          SELECT UPPER(TRIM(NOME_COMPRADOR)) AS CLIENTE,
                 DT_VENDA AS DT,
                 NVL(VALOR_VENDA,0) AS RECEITA,
                 NVL(LUCRO_VENDA,0) AS LUCRO,
                 'VEICULO' AS ORIGEM
          FROM BRZ_HIST_VENDAS_VEICULOS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
            AND NOME_COMPRADOR IS NOT NULL

          UNION ALL

          SELECT UPPER(TRIM(NOME_COMPRADOR)) AS CLIENTE,
                 DT_VENDA AS DT,
                 NVL(VALOR_VENDA,0) AS RECEITA,
                 NVL(LUCRO_VENDA,0) AS LUCRO,
                 'PECA' AS ORIGEM
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
            AND NOME_COMPRADOR IS NOT NULL

          UNION ALL

          SELECT UPPER(TRIM(NOME_CLIENTE)) AS CLIENTE,
                 DT_REALIZACAO_SERVICO AS DT,
                 NVL(VALOR_TOTAL_SERVICO,0) AS RECEITA,
                 NVL(LUCRO_SERVICO,0) AS LUCRO,
                 'SERVICO' AS ORIGEM
          FROM BRZ_HIST_SERVICOS
          WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
            AND NOME_CLIENTE IS NOT NULL
        )
        SELECT
          CLIENTE,
          COUNT(*) AS TRANSACOES,
          MIN(DT) AS PRIMEIRA_DATA,
          MAX(DT) AS ULTIMA_DATA,
          SUM(RECEITA) AS RECEITA_TOTAL,
          SUM(LUCRO) AS LUCRO_TOTAL
        FROM tx
        GROUP BY CLIENTE
        ORDER BY RECEITA_TOTAL DESC
        FETCH FIRST {int(top_n)} ROWS ONLY
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})

    def rfm_base(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        """
        Retorna Recency (dias), Frequency (transações) e Monetary (receita) por cliente no período.
        Recency = (dt_fim - última_data_no_período) em dias.
        """
        sql = """
        WITH
        tx AS (
          SELECT UPPER(TRIM(NOME_COMPRADOR)) AS CLIENTE,
                 DT_VENDA AS DT,
                 NVL(VALOR_VENDA,0) AS RECEITA
          FROM BRZ_HIST_VENDAS_VEICULOS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
            AND NOME_COMPRADOR IS NOT NULL

          UNION ALL

          SELECT UPPER(TRIM(NOME_COMPRADOR)) AS CLIENTE,
                 DT_VENDA AS DT,
                 NVL(VALOR_VENDA,0) AS RECEITA
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
            AND NOME_COMPRADOR IS NOT NULL

          UNION ALL

          SELECT UPPER(TRIM(NOME_CLIENTE)) AS CLIENTE,
                 DT_REALIZACAO_SERVICO AS DT,
                 NVL(VALOR_TOTAL_SERVICO,0) AS RECEITA
          FROM BRZ_HIST_SERVICOS
          WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
            AND NOME_CLIENTE IS NOT NULL
        )
        SELECT
          CLIENTE,
          MAX(DT) AS ULTIMA_DATA,
          TRUNC(:dt_fim) - TRUNC(MAX(DT)) AS RECENCY_DIAS,
          COUNT(*) AS FREQUENCY,
          SUM(RECEITA) AS MONETARY
        FROM tx
        GROUP BY CLIENTE
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})
