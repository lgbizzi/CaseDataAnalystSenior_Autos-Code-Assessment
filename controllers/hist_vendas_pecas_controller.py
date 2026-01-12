# controllers/hist_vendas_pecas_controller.py

from __future__ import annotations

import os
import sys
import inspect
from datetime import datetime, date
from typing import Any, Dict, List, Optional

import pandas as pd

# Garante import relativo do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connector.oracle_connector import OracleConnector  # [file:39]
from utils.csv_handler import CSVHandler
from utils.logger_controller import LoggerController
from models.models import BRZHistVendasPecas

NOME = "HistVendasPecasController"

# logger singleton no padrão
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, f"{NOME}.txt")
logger = LoggerController(logfile)


class HistVendasPecasController:
    TABLE_NAME = "BRZ_HIST_VENDAS_PECAS"  # [file:36]

    # UFs permitidas (validação)
    UFS_VALIDAS = {
        "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
        "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"
    }

    def __init__(
        self,
        connector: Optional[OracleConnector] = None,
        csv_handler: Optional[CSVHandler] = None,
        log_directory: str = "logs",
    ):
        self.logger = logger
        self.connector = connector or OracleConnector()
        self.csv_handler = csv_handler or CSVHandler(log_directory=log_directory)

    # -------------------------
    # Pipeline principal
    # -------------------------
    def run(self, csv_path: str) -> int:
        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:",
                        f"Iniciando ETL: {csv_path}")

        read_result = self.csv_handler.read_csv(
            csv_path,
            normalize_columns=True,
            save_rejected_rows=True,
        )

        df = read_result.df
        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"[{NOME}] Linhas lidas do CSV: {len(df)} | Delimitador detectado: '{read_result.delimiter}'")

        # Tratamento: margem vazia -> 0
        if "Margem_da_Venda" in df.columns:
            df["Margem_da_Venda"] = df["Margem_da_Venda"].apply(self._margem_default_zero)

        records = self._transform_to_brz_records(df)
        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"[{NOME}] Registros prontos para insert: {len(records)}")

        if not records:
            context = inspect.currentframe()
            self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"[{NOME}] Nada para inserir.")
            return 0

        inserted = self.connector.bulk_insert(self.TABLE_NAME, records)
        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"[{NOME}] Inseridos no Oracle: {inserted}")
        return inserted

    # -------------------------
    # Transformação para BRZ_*
    # -------------------------
    def _transform_to_brz_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []

        def parse_date_yyyy_mm_dd(val: Any) -> Optional[date]:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            s = str(val).strip()
            if not s or s.lower() in ("nan", "none"):
                return None
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except Exception:
                return None

        for _, row in df.iterrows():
            vendedor = self._fix_mojibake(self._safe_str(row.get("Nome_do_Vendedor_que_Realizou_a_Venda")))
            comprador = self._fix_mojibake(self._safe_str(row.get("Nome_do_Comprador_da_Peca")))

            uf = self._safe_str(row.get("Estado_Brasileiro_da_Venda"))
            uf = uf.upper().strip() if uf else None
            if uf and uf not in self.UFS_VALIDAS:
                uf = None

            brz = {
                "COD_CONCESSIONARIA": self._safe_str(row.get("Cod_Concessionaria")),
                "COD_FILIAL": self._safe_str(row.get("Cod_Filial")),

                "NOME_CONCESSIONARIA": self._safe_str(row.get("Nome_da_Concessionaria")),
                "NOME_FILIAL": self._safe_str(row.get("Nome_da_Filial")),
                "MARCA_FILIAL": self._safe_str(row.get("Marca_da_Filial")),

                "DT_VENDA": parse_date_yyyy_mm_dd(row.get("Data_da_Venda")),

                "QTDE_VENDIDA": self._safe_float(row.get("Quantidade_Vendida")),
                "TIPO_TRANSACAO": self._safe_str(row.get("Tipo_de_Transacao")),

                "VALOR_VENDA": self._safe_float(row.get("Valor_da_Venda")),
                "CUSTO_PECA": self._safe_float(row.get("Custo_da_Peca")),
                "LUCRO_VENDA": self._safe_float(row.get("Lucro_da_Venda")),
                "MARGEM_VENDA": self._safe_float(row.get("Margem_da_Venda")),

                "DESCRICAO_PECA": self._safe_str(row.get("Descricao_da_Peca")),
                "CATEGORIA_PECA": self._safe_str(row.get("Categoria_da_Peca")),

                "DEPARTAMENTO_VENDA": self._safe_str(row.get("Departamento_da_Venda")),
                "TIPO_VENDA_PECA": self._safe_str(row.get("Tipo_de_Venda_da_Peca")),

                "NOME_VENDEDOR": vendedor,
                "NOME_COMPRADOR": comprador,

                "CIDADE_VENDA": self._safe_str(row.get("Cidade_da_Venda")),
                "ESTADO_VENDA": uf,
                "MACROREGIAO_VENDA": self._safe_str(row.get("Macroregiao_Geografica_da_Venda")),
            }

            try:
                model = BRZHistVendasPecas(**brz)
                out.append(model.model_dump(by_alias=True, exclude={"ID_VENDA_PECA"}, exclude_none=False))
            except Exception as e:
                context = inspect.currentframe()
                self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno,
                                "ERRO!!!", f"[{NOME}] Linha ignorada por erro de validação: {e}")

        return out

    # -------------------------
    # Helpers
    # -------------------------
    def _safe_str(self, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        s = str(v).strip()
        return s if s else None

    def _safe_float(self, v: Any) -> Optional[float]:
        if v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        s = str(v).strip()
        if not s or s.lower() in ("nan", "none"):
            return None
        # suporta "1234.56" e "1.234,56"
        s2 = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
        try:
            return float(s2)
        except Exception:
            return None

    def _margem_default_zero(self, v: Any) -> Any:
        # regra solicitada: vazios => 0
        if v is None:
            return 0
        if isinstance(v, float) and pd.isna(v):
            return 0
        s = str(v).strip()
        if not s or s.lower() in ("nan", "none"):
            return 0
        return v

    def _fix_mojibake(self, s: Optional[str]) -> Optional[str]:
        """
        Corrige casos clássicos de UTF-8 lido como Latin-1/CP1252:
        'ANDRÃ‰' -> 'ANDRÉ', 'ARAÃšJO' -> 'ARAÚJO', etc.
        Se não precisar, retorna o original.
        """
        if not s:
            return s
        try:
            fixed = s.encode("latin1").decode("utf-8")
            return fixed
        except Exception:
            return s
