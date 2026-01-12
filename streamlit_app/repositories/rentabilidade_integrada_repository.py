from __future__ import annotations

from datetime import date
from typing import Optional, Dict, Any, List

from repositories.base_repo import BaseRepository


class RentabilidadeIntegradaRepository(BaseRepository):
    def margem_integrada_por_venda_veiculo(
        self,
        dt_ini: date,
        dt_fim: date,
        janela_dias: int = 30,
        cod_concessionaria: Optional[int] = None,
        cod_filial: Optional[int] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        sql = f"""
        WITH base_venda AS (
            SELECT
                v.ID_VENDA_VEICULO,
                v.COD_CONCESSIONARIA,
                v.COD_FILIAL,
                v.NOME_FILIAL,
                v.DT_VENDA,
                v.NOME_COMPRADOR,
                v.MARCA_VEICULO,
                v.MODELO_VEICULO,
                SUM(NVL(v.VALOR_VENDA,0)) AS RECEITA_VEICULO,
                SUM(NVL(v.LUCRO_VENDA,0)) AS LUCRO_VEICULO
            FROM BRZ_HIST_VENDAS_VEICULOS v
            WHERE v.DT_VENDA BETWEEN :dt_ini AND :dt_fim
              AND (:cod_concessionaria IS NULL OR v.COD_CONCESSIONARIA = :cod_concessionaria)
              AND (:cod_filial IS NULL OR v.COD_FILIAL = :cod_filial)
            GROUP BY
                v.ID_VENDA_VEICULO, v.COD_CONCESSIONARIA, v.COD_FILIAL, v.NOME_FILIAL,
                v.DT_VENDA, v.NOME_COMPRADOR, v.MARCA_VEICULO, v.MODELO_VEICULO
        ),
        srv AS (
            SELECT
                b.ID_VENDA_VEICULO,
                SUM(NVL(s.VALOR_TOTAL_SERVICO,0)) AS RECEITA_SERVICOS,
                SUM(NVL(s.LUCRO_SERVICO,0)) AS LUCRO_SERVICOS
            FROM base_venda b
            LEFT JOIN BRZ_HIST_SERVICOS s
              ON s.NOME_CLIENTE = b.NOME_COMPRADOR
             AND s.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA
             AND s.DT_REALIZACAO_SERVICO BETWEEN b.DT_VENDA AND (b.DT_VENDA + :janela_dias)
            GROUP BY b.ID_VENDA_VEICULO
        ),
        pec AS (
            SELECT
                b.ID_VENDA_VEICULO,
                SUM(NVL(p.VALOR_VENDA,0)) AS RECEITA_PECAS,
                SUM(NVL(p.LUCRO_VENDA,0)) AS LUCRO_PECAS
            FROM base_venda b
            LEFT JOIN BRZ_HIST_VENDAS_PECAS p
              ON p.NOME_COMPRADOR = b.NOME_COMPRADOR
             AND p.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA
             AND p.DT_VENDA BETWEEN b.DT_VENDA AND (b.DT_VENDA + :janela_dias)
            GROUP BY b.ID_VENDA_VEICULO
        )
        SELECT
            b.COD_CONCESSIONARIA,
            b.COD_FILIAL,
            b.NOME_FILIAL,
            b.DT_VENDA,
            b.NOME_COMPRADOR,
            b.MARCA_VEICULO,
            b.MODELO_VEICULO,

            b.RECEITA_VEICULO,
            b.LUCRO_VEICULO,
            CASE WHEN b.RECEITA_VEICULO = 0 THEN NULL ELSE b.LUCRO_VEICULO / b.RECEITA_VEICULO END AS MARGEM_VEICULO,

            NVL(s.RECEITA_SERVICOS,0) AS RECEITA_SERVICOS,
            NVL(s.LUCRO_SERVICOS,0)   AS LUCRO_SERVICOS,
            CASE WHEN NVL(s.RECEITA_SERVICOS,0) = 0 THEN NULL ELSE NVL(s.LUCRO_SERVICOS,0) / NVL(s.RECEITA_SERVICOS,0) END AS MARGEM_SERVICOS,

            NVL(p.RECEITA_PECAS,0) AS RECEITA_PECAS,
            NVL(p.LUCRO_PECAS,0)   AS LUCRO_PECAS,
            CASE WHEN NVL(p.RECEITA_PECAS,0) = 0 THEN NULL ELSE NVL(p.LUCRO_PECAS,0) / NVL(p.RECEITA_PECAS,0) END AS MARGEM_PECAS,

            ( b.LUCRO_VEICULO + NVL(s.LUCRO_SERVICOS,0) + NVL(p.LUCRO_PECAS,0) ) AS LUCRO_INTEGRADO,
            ( b.RECEITA_VEICULO + NVL(s.RECEITA_SERVICOS,0) + NVL(p.RECEITA_PECAS,0) ) AS RECEITA_INTEGRADA,

            CASE
              WHEN ( b.RECEITA_VEICULO + NVL(s.RECEITA_SERVICOS,0) + NVL(p.RECEITA_PECAS,0) ) = 0 THEN NULL
              ELSE ( b.LUCRO_VEICULO + NVL(s.LUCRO_SERVICOS,0) + NVL(p.LUCRO_PECAS,0) )
                   / ( b.RECEITA_VEICULO + NVL(s.RECEITA_SERVICOS,0) + NVL(p.RECEITA_PECAS,0) )
            END AS MARGEM_INTEGRADA

        FROM base_venda b
        LEFT JOIN srv s ON s.ID_VENDA_VEICULO = b.ID_VENDA_VEICULO
        LEFT JOIN pec p ON p.ID_VENDA_VEICULO = b.ID_VENDA_VEICULO
        ORDER BY b.DT_VENDA DESC
        FETCH FIRST {int(limit)} ROWS ONLY
        """

        params: Dict[str, Any] = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "janela_dias": int(janela_dias),
            "cod_concessionaria": cod_concessionaria,
            "cod_filial": cod_filial,
        }

        return self.query_dicts(sql, params)

    def ranking_modelos_rentabilidade_integrada(
        self,
        dt_ini: date,
        dt_fim: date,
        janela_dias: int = 30,
        cod_concessionaria: Optional[int] = None,
        cod_filial: Optional[int] = None,
        top_n: int = 15,
        min_receita_veiculo: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        ANÁLISE 2: ranking de modelos por margem integrada (proxy de ROI).
        """
        sql = f"""
        WITH base_venda AS (
            SELECT
                v.ID_VENDA_VEICULO,
                v.COD_CONCESSIONARIA,
                v.COD_FILIAL,
                v.DT_VENDA,
                v.NOME_COMPRADOR,
                v.MARCA_VEICULO,
                v.MODELO_VEICULO,
                SUM(NVL(v.VALOR_VENDA,0)) AS RECEITA_VEICULO,
                SUM(NVL(v.LUCRO_VENDA,0)) AS LUCRO_VEICULO
            FROM BRZ_HIST_VENDAS_VEICULOS v
            WHERE v.DT_VENDA BETWEEN :dt_ini AND :dt_fim
              AND (:cod_concessionaria IS NULL OR v.COD_CONCESSIONARIA = :cod_concessionaria)
              AND (:cod_filial IS NULL OR v.COD_FILIAL = :cod_filial)
            GROUP BY
                v.ID_VENDA_VEICULO, v.COD_CONCESSIONARIA, v.COD_FILIAL,
                v.DT_VENDA, v.NOME_COMPRADOR, v.MARCA_VEICULO, v.MODELO_VEICULO
        ),
        srv AS (
            SELECT
                b.ID_VENDA_VEICULO,
                SUM(NVL(s.VALOR_TOTAL_SERVICO,0)) AS RECEITA_SERVICOS,
                SUM(NVL(s.LUCRO_SERVICO,0)) AS LUCRO_SERVICOS
            FROM base_venda b
            LEFT JOIN BRZ_HIST_SERVICOS s
              ON s.NOME_CLIENTE = b.NOME_COMPRADOR
             AND s.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA
             AND s.DT_REALIZACAO_SERVICO BETWEEN b.DT_VENDA AND (b.DT_VENDA + :janela_dias)
            GROUP BY b.ID_VENDA_VEICULO
        ),
        pec AS (
            SELECT
                b.ID_VENDA_VEICULO,
                SUM(NVL(p.VALOR_VENDA,0)) AS RECEITA_PECAS,
                SUM(NVL(p.LUCRO_VENDA,0)) AS LUCRO_PECAS
            FROM base_venda b
            LEFT JOIN BRZ_HIST_VENDAS_PECAS p
              ON p.NOME_COMPRADOR = b.NOME_COMPRADOR
             AND p.COD_CONCESSIONARIA = b.COD_CONCESSIONARIA
             AND p.DT_VENDA BETWEEN b.DT_VENDA AND (b.DT_VENDA + :janela_dias)
            GROUP BY b.ID_VENDA_VEICULO
        ),
        integ AS (
            SELECT
                b.MARCA_VEICULO,
                b.MODELO_VEICULO,
                (b.LUCRO_VEICULO + NVL(s.LUCRO_SERVICOS,0) + NVL(p.LUCRO_PECAS,0)) AS LUCRO_INTEGRADO,
                (b.RECEITA_VEICULO + NVL(s.RECEITA_SERVICOS,0) + NVL(p.RECEITA_PECAS,0)) AS RECEITA_INTEGRADA,
                b.RECEITA_VEICULO,
                b.LUCRO_VEICULO,
                NVL(s.RECEITA_SERVICOS,0) AS RECEITA_SERVICOS,
                NVL(p.RECEITA_PECAS,0) AS RECEITA_PECAS
            FROM base_venda b
            LEFT JOIN srv s ON s.ID_VENDA_VEICULO = b.ID_VENDA_VEICULO
            LEFT JOIN pec p ON p.ID_VENDA_VEICULO = b.ID_VENDA_VEICULO
        )
        SELECT
            MARCA_VEICULO,
            MODELO_VEICULO,
            COUNT(*) AS QTD_VENDAS,
            SUM(RECEITA_VEICULO) AS RECEITA_VEICULO,
            SUM(RECEITA_SERVICOS) AS RECEITA_SERVICOS,
            SUM(RECEITA_PECAS) AS RECEITA_PECAS,
            SUM(RECEITA_INTEGRADA) AS RECEITA_INTEGRADA,
            SUM(LUCRO_INTEGRADO) AS LUCRO_INTEGRADO,
            CASE WHEN SUM(RECEITA_INTEGRADA) = 0 THEN NULL
                 ELSE SUM(LUCRO_INTEGRADO)/SUM(RECEITA_INTEGRADA)
            END AS MARGEM_INTEGRADA
        FROM integ
        GROUP BY MARCA_VEICULO, MODELO_VEICULO
        HAVING SUM(RECEITA_VEICULO) >= :min_receita_veiculo
        ORDER BY MARGEM_INTEGRADA DESC NULLS LAST, RECEITA_INTEGRADA DESC
        FETCH FIRST {int(top_n)} ROWS ONLY
        """

        params: Dict[str, Any] = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "janela_dias": int(janela_dias),
            "cod_concessionaria": cod_concessionaria,
            "cod_filial": cod_filial,
            "min_receita_veiculo": float(min_receita_veiculo),
        }
        return self.query_dicts(sql, params)
    

    def fluxo_caixa_proxy(
        self,
        dt_ini: date,
        dt_fim: date,
        cod_concessionaria: Optional[int] = None,
        cod_filial: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        ANÁLISE 3 (proxy): compara capital imobilizado (estoques) com entradas de caixa (receitas) no período.
        """
        sql = """
        WITH
        estoque AS (
            SELECT
                SUM(NVL(ep.VALOR_PECA_ESTOQUE,0)) AS ESTOQUE_PECAS,
                (SELECT SUM(NVL(ev.CUSTO_VEICULO,0))
                   FROM BRZ_ESTOQUE_VEICULOS ev
                  WHERE (:cod_concessionaria IS NULL OR ev.COD_CONCESSIONARIA = :cod_concessionaria)
                    AND (:cod_filial IS NULL OR ev.COD_FILIAL = :cod_filial)
                ) AS ESTOQUE_VEICULOS
            FROM BRZ_ESTOQUE_PECAS ep
            WHERE (:cod_concessionaria IS NULL OR ep.COD_CONCESSIONARIA = :cod_concessionaria)
              AND (:cod_filial IS NULL OR ep.COD_FILIAL = :cod_filial)
        ),
        entradas AS (
            SELECT
                (SELECT SUM(NVL(v.VALOR_VENDA,0))
                   FROM BRZ_HIST_VENDAS_VEICULOS v
                  WHERE v.DT_VENDA BETWEEN :dt_ini AND :dt_fim
                    AND (:cod_concessionaria IS NULL OR v.COD_CONCESSIONARIA = :cod_concessionaria)
                    AND (:cod_filial IS NULL OR v.COD_FILIAL = :cod_filial)
                ) AS RECEITA_VENDAS_VEICULOS,
                (SELECT SUM(NVL(p.VALOR_VENDA,0))
                   FROM BRZ_HIST_VENDAS_PECAS p
                  WHERE p.DT_VENDA BETWEEN :dt_ini AND :dt_fim
                    AND (:cod_concessionaria IS NULL OR p.COD_CONCESSIONARIA = :cod_concessionaria)
                    AND (:cod_filial IS NULL OR p.COD_FILIAL = :cod_filial)
                ) AS RECEITA_VENDAS_PECAS,
                (SELECT SUM(NVL(s.VALOR_TOTAL_SERVICO,0))
                   FROM BRZ_HIST_SERVICOS s
                  WHERE s.DT_REALIZACAO_SERVICO BETWEEN :dt_ini AND :dt_fim
                    AND (:cod_concessionaria IS NULL OR s.COD_CONCESSIONARIA = :cod_concessionaria)
                    AND (:cod_filial IS NULL OR s.COD_FILIAL = :cod_filial)
                ) AS RECEITA_SERVICOS
            FROM dual
        )
        SELECT 'Capital imobilizado (estoque)' AS TIPO, 'Veículos (custo)' AS ITEM, NVL(e.ESTOQUE_VEICULOS,0) AS VALOR FROM estoque e
        UNION ALL
        SELECT 'Capital imobilizado (estoque)' AS TIPO, 'Peças (valor)' AS ITEM, NVL(e.ESTOQUE_PECAS,0) AS VALOR FROM estoque e
        UNION ALL
        SELECT 'Entradas no período' AS TIPO, 'Receita veículos' AS ITEM, NVL(x.RECEITA_VENDAS_VEICULOS,0) AS VALOR FROM entradas x
        UNION ALL
        SELECT 'Entradas no período' AS TIPO, 'Receita peças' AS ITEM, NVL(x.RECEITA_VENDAS_PECAS,0) AS VALOR FROM entradas x
        UNION ALL
        SELECT 'Entradas no período' AS TIPO, 'Receita serviços' AS ITEM, NVL(x.RECEITA_SERVICOS,0) AS VALOR FROM entradas x
        """

        params: Dict[str, Any] = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "cod_concessionaria": cod_concessionaria,
            "cod_filial": cod_filial,
        }
        return self.query_dicts(sql, params)