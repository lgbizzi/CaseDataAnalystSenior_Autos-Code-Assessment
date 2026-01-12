from __future__ import annotations

from datetime import date
from typing import Dict, Any, List, Optional

from repositories.base_repo import BaseRepository


class DashboardAnaliticoRepository(BaseRepository):

    def pnl_mensal(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        sql = """
        WITH
        veic AS (
          SELECT TRUNC(DT_VENDA,'MM') AS MES,
                 SUM(NVL(VALOR_VENDA,0)) AS RECEITA,
                 SUM(NVL(LUCRO_VENDA,0)) AS LUCRO
          FROM BRZ_HIST_VENDAS_VEICULOS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
          GROUP BY TRUNC(DT_VENDA,'MM')
        ),
        pec AS (
          SELECT TRUNC(DT_VENDA,'MM') AS MES,
                 SUM(NVL(VALOR_VENDA,0)) AS RECEITA,
                 SUM(NVL(LUCRO_VENDA,0)) AS LUCRO
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
          GROUP BY TRUNC(DT_VENDA,'MM')
        ),
        srv AS (
          SELECT TRUNC(DT_REALIZACAO_SERVICO,'MM') AS MES,
                 SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA,
                 SUM(NVL(LUCRO_SERVICO,0)) AS LUCRO
          FROM BRZ_HIST_SERVICOS
          WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
          GROUP BY TRUNC(DT_REALIZACAO_SERVICO,'MM')
        ),
        base AS (
          SELECT MES FROM veic
          UNION SELECT MES FROM pec
          UNION SELECT MES FROM srv
        )
        SELECT
          b.MES,
          NVL(v.RECEITA,0) AS VEIC_RECEITA, NVL(v.LUCRO,0) AS VEIC_LUCRO,
          NVL(p.RECEITA,0) AS PEC_RECEITA,  NVL(p.LUCRO,0) AS PEC_LUCRO,
          NVL(s.RECEITA,0) AS SRV_RECEITA,  NVL(s.LUCRO,0) AS SRV_LUCRO,
          (NVL(v.LUCRO,0)+NVL(p.LUCRO,0)+NVL(s.LUCRO,0)) AS LUCRO_TOTAL,
          (NVL(v.RECEITA,0)+NVL(p.RECEITA,0)+NVL(s.RECEITA,0)) AS RECEITA_TOTAL
        FROM base b
        LEFT JOIN veic v ON v.MES = b.MES
        LEFT JOIN pec  p ON p.MES = b.MES
        LEFT JOIN srv  s ON s.MES = b.MES
        ORDER BY b.MES
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})

    def roi_por_filial_periodo(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        sql = """
        WITH
        lucro AS (
          SELECT COD_FILIAL, NOME_FILIAL,
                 SUM(NVL(LUCRO_VENDA,0)) AS LUCRO_VEIC
          FROM BRZ_HIST_VENDAS_VEICULOS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
          GROUP BY COD_FILIAL, NOME_FILIAL

          UNION ALL
          SELECT COD_FILIAL, NOME_FILIAL,
                 SUM(NVL(LUCRO_VENDA,0)) AS LUCRO_VEIC
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
          GROUP BY COD_FILIAL, NOME_FILIAL

          UNION ALL
          SELECT COD_FILIAL, NOME_FILIAL,
                 SUM(NVL(LUCRO_SERVICO,0)) AS LUCRO_VEIC
          FROM BRZ_HIST_SERVICOS
          WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
          GROUP BY COD_FILIAL, NOME_FILIAL
        ),
        lucro_filial AS (
          SELECT COD_FILIAL, NOME_FILIAL, SUM(LUCRO_VEIC) AS LUCRO_TOTAL
          FROM lucro
          GROUP BY COD_FILIAL, NOME_FILIAL
        ),
        estoque AS (
          SELECT COD_FILIAL, NOME_FILIAL, SUM(NVL(CUSTO_VEICULO,0)) AS ESTOQUE_VEIC
          FROM BRZ_ESTOQUE_VEICULOS
          GROUP BY COD_FILIAL, NOME_FILIAL
        ),
        estoque2 AS (
          SELECT COD_FILIAL, NOME_FILIAL, SUM(NVL(VALOR_PECA_ESTOQUE,0)) AS ESTOQUE_PEC
          FROM BRZ_ESTOQUE_PECAS
          GROUP BY COD_FILIAL, NOME_FILIAL
        )
        SELECT
          l.COD_FILIAL,
          l.NOME_FILIAL,
          l.LUCRO_TOTAL,
          (NVL(e.ESTOQUE_VEIC,0) + NVL(p.ESTOQUE_PEC,0)) AS CAPITAL_ESTOQUE,
          CASE WHEN (NVL(e.ESTOQUE_VEIC,0) + NVL(p.ESTOQUE_PEC,0)) = 0 THEN NULL
               ELSE l.LUCRO_TOTAL / (NVL(e.ESTOQUE_VEIC,0) + NVL(p.ESTOQUE_PEC,0))
          END AS ROI_ESTOQUE
        FROM lucro_filial l
        LEFT JOIN estoque e  ON e.COD_FILIAL = l.COD_FILIAL
        LEFT JOIN estoque2 p ON p.COD_FILIAL = l.COD_FILIAL
        ORDER BY ROI_ESTOQUE DESC NULLS LAST
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})

    def lucro_por_vendedor(self, dt_ini: date, dt_fim: date, top_n: int = 20) -> List[Dict[str, Any]]:
        sql = f"""
        WITH
        vv AS (
          SELECT NOME_VENDEDOR AS VENDEDOR,
                 SUM(NVL(LUCRO_VENDA,0)) AS LUCRO,
                 SUM(NVL(VALOR_VENDA,0)) AS RECEITA
          FROM BRZ_HIST_VENDAS_VEICULOS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
            AND NOME_VENDEDOR IS NOT NULL
          GROUP BY NOME_VENDEDOR
        ),
        vp AS (
          SELECT NOME_VENDEDOR AS VENDEDOR,
                 SUM(NVL(LUCRO_VENDA,0)) AS LUCRO,
                 SUM(NVL(VALOR_VENDA,0)) AS RECEITA
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
            AND NOME_VENDEDOR IS NOT NULL
          GROUP BY NOME_VENDEDOR
        ),
        vs AS (
          SELECT NOME_VENDEDOR_SERVICO AS VENDEDOR,
                 SUM(NVL(LUCRO_SERVICO,0)) AS LUCRO,
                 SUM(NVL(VALOR_TOTAL_SERVICO,0)) AS RECEITA
          FROM BRZ_HIST_SERVICOS
          WHERE DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
            AND NOME_VENDEDOR_SERVICO IS NOT NULL
          GROUP BY NOME_VENDEDOR_SERVICO
        ),
        allv AS (
          SELECT * FROM vv
          UNION ALL SELECT * FROM vp
          UNION ALL SELECT * FROM vs
        )
        SELECT
          VENDEDOR,
          SUM(LUCRO) AS LUCRO_TOTAL,
          SUM(RECEITA) AS RECEITA_TOTAL,
          CASE WHEN SUM(RECEITA)=0 THEN NULL ELSE SUM(LUCRO)/SUM(RECEITA) END AS MARGEM
        FROM allv
        GROUP BY VENDEDOR
        ORDER BY LUCRO_TOTAL DESC
        FETCH FIRST {int(top_n)} ROWS ONLY
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})

    def estoque_kpis(self) -> Dict[str, Any]:
        sql = """
        SELECT
          (SELECT SUM(NVL(CUSTO_VEICULO,0)) FROM BRZ_ESTOQUE_VEICULOS) AS ESTOQUE_VEIC_VALOR,
          (SELECT AVG(NVL(TEMPO_TOTAL_ESTOQUE_DIAS,0)) FROM BRZ_ESTOQUE_VEICULOS) AS ESTOQUE_VEIC_DIAS_MEDIO_ATUAL,
          (SELECT SUM(NVL(VALOR_PECA_ESTOQUE,0)) FROM BRZ_ESTOQUE_PECAS) AS ESTOQUE_PEC_VALOR
        FROM dual
        """
        return self.query_one(sql, {})

    def top_pecas_valor_estoque(self, top_n: int = 20) -> List[Dict[str, Any]]:
        sql = f"""
        SELECT
          DESCRICAO_PECA,
          CATEGORIA_PECA,
          SUM(NVL(QTDE_PECA_ESTOQUE,0)) AS QTDE,
          SUM(NVL(VALOR_PECA_ESTOQUE,0)) AS VALOR_ESTOQUE
        FROM BRZ_ESTOQUE_PECAS
        GROUP BY DESCRICAO_PECA, CATEGORIA_PECA
        ORDER BY VALOR_ESTOQUE DESC
        FETCH FIRST {int(top_n)} ROWS ONLY
        """
        return self.query_dicts(sql, {})

    def rotatividade_pecas_categoria_proxy(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        """
        Proxy de giro por categoria = receita no período / valor em estoque atual da categoria.
        """
        sql = """
        WITH
        vendas AS (
          SELECT CATEGORIA_PECA,
                 SUM(NVL(VALOR_VENDA,0)) AS RECEITA_PERIODO
          FROM BRZ_HIST_VENDAS_PECAS
          WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
          GROUP BY CATEGORIA_PECA
        ),
        estoque AS (
          SELECT CATEGORIA_PECA,
                 SUM(NVL(VALOR_PECA_ESTOQUE,0)) AS VALOR_ESTOQUE
          FROM BRZ_ESTOQUE_PECAS
          GROUP BY CATEGORIA_PECA
        ),
        base AS (
          SELECT CATEGORIA_PECA FROM vendas
          UNION
          SELECT CATEGORIA_PECA FROM estoque
        )
        SELECT
          b.CATEGORIA_PECA,
          NVL(v.RECEITA_PERIODO,0) AS RECEITA_PERIODO,
          NVL(e.VALOR_ESTOQUE,0) AS VALOR_ESTOQUE,
          CASE WHEN NVL(e.VALOR_ESTOQUE,0)=0 THEN NULL
               ELSE NVL(v.RECEITA_PERIODO,0)/NVL(e.VALOR_ESTOQUE,0)
          END AS GIRO_PROXY
        FROM base b
        LEFT JOIN vendas v ON v.CATEGORIA_PECA = b.CATEGORIA_PECA
        LEFT JOIN estoque e ON e.CATEGORIA_PECA = b.CATEGORIA_PECA
        ORDER BY GIRO_PROXY DESC NULLS LAST
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})
    
    def dias_estoque_historico_venda_mensal(self, dt_ini: date, dt_fim: date) -> List[Dict[str, Any]]:
        """
        Histórico: média de DIAS_EM_ESTOQUE dos veículos vendidos por mês.
        (Isso representa quanto tempo os veículos ficaram em estoque antes de vender.)
        """
        sql = """
        SELECT
          TRUNC(DT_VENDA,'MM') AS MES,
          AVG(NVL(DIAS_EM_ESTOQUE,0)) AS DIAS_MEDIO_VENDA
        FROM BRZ_HIST_VENDAS_VEICULOS
        WHERE DT_VENDA BETWEEN :dt_ini AND :dt_fim
        GROUP BY TRUNC(DT_VENDA,'MM')
        ORDER BY MES
        """
        return self.query_dicts(sql, {"dt_ini": dt_ini, "dt_fim": dt_fim})
