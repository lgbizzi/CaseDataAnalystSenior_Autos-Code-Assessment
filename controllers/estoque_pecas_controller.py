# controllers/estoque_pecas_controller.py

from __future__ import annotations

import os
import sys
import inspect
from pathlib import Path
from datetime import datetime, date
from typing import Any, Dict, List, Optional

import pandas as pd

# Ajuste do path para manter compatível com o padrão usado no connector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connector.oracle_connector import OracleConnector
from utils.csv_handler import CSVHandler
from utils.logger_controller import LoggerController
from models.models import BRZEstoquePecas


NOME = "EstoquePecasController"

# criação do logger (uma vez, no início do script/classe)
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, f"{NOME}.txt")
logger = LoggerController(logfile)

class EstoquePecasController:
    TABLE_NAME = "BRZ_ESTOQUE_PECAS"

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
        """
        Lê CSV -> padroniza -> valida (Pydantic) -> bulk insert no Oracle.
        Retorna quantidade inserida.
        """
        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"Iniciando ETL: {csv_path}")

        read_result = self.csv_handler.read_csv(
            csv_path,
            normalize_columns=True,
            save_rejected_rows=True,
        )

        df = read_result.df

        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"[{NOME}] Linhas lidas do CSV: {len(df)} | Delimitador detectado: '{read_result.delimiter}'")

        print("\nDataFrame: ")
        print(df)

        records = self._transform_to_brz_records(df)

        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"[{NOME}] Registros prontos para insert: {len(records)}")

        if not records:
            context = inspect.currentframe()
            self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"[{NOME}] Nada para inserir.")
            return 0

        inserted = self.connector.bulk_insert(self.TABLE_NAME, records)

        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", "INFO:", f"[{NOME}] Inseridos no Oracle: {inserted}")
        return inserted

    # -------------------------
    # Transformações
    # -------------------------
    def _transform_to_brz_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Converte DataFrame (colunas do CSV) em lista de dicts com colunas BRZ_*.
        Aqui mantemos o mínimo (base limpa). Tratamentos por base virão depois.
        """
        out: List[Dict[str, Any]] = []

        # Helper de datas
        def parse_date_yyyy_mm_dd(val: Any) -> Optional[date]:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            s = str(val).strip()
            if not s or s.lower() in ("nan", "none"):
                return None
            try:
                # CSV está em YYYY-MM-DD
                return datetime.strptime(s, "%Y-%m-%d").date()
            except Exception:
                return None

        def parse_obsoleta_flag(val: Any) -> Optional[str]:
            """
            CSV tem True/False. BRZ espera VARCHAR2(3) (ex.: SIM/NAO).
            """
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            if isinstance(val, bool):
                return "SIM" if val else "NAO"
            s = str(val).strip().lower()
            if s in ("true", "1", "sim", "yes", "y"):
                return "SIM"
            if s in ("false", "0", "nao", "não", "no", "n"):
                return "NAO"
            return None

        # Map linha a linha
        for _, row in df.iterrows():
            # Monta dict no contrato do Oracle (colunas do DDL) [file:35]
            brz = {
                "COD_CONCESSIONARIA": str(row.get("Cod_Concessionaria", "")).strip(),
                "COD_FILIAL": str(row.get("Cod_Filial", "")).strip(),
                "NOME_CONCESSIONARIA": self._safe_str(row.get("Nome_da_Concessionaria")),
                "NOME_FILIAL": self._safe_str(row.get("Nome_da_Filial")),
                "MARCA_FILIAL": self._safe_str(row.get("Marca_da_Filial")),
                "VALOR_PECA_ESTOQUE": self._safe_float(row.get("Valor_da_Peca_em_Estoque")),
                "QTDE_PECA_ESTOQUE": self._safe_float(row.get("Quantidade_da_Peca_em_Estoque")),
                "DESCRICAO_PECA": self._safe_str(row.get("Descricao_da_Peca")),
                "CATEGORIA_PECA": self._safe_str(row.get("Categoria_da_Peca")),
                "DT_ULTIMA_VENDA_PECA": parse_date_yyyy_mm_dd(row.get("Data_de_Ultima_Venda_da_Peca")),
                "DT_ULTIMA_ENTRADA_PECA": parse_date_yyyy_mm_dd(row.get("Data_da_Ultima_Entrada_no_Estoque_da_Peca")),
                "PECA_OBSOLETA_FLAG": parse_obsoleta_flag(row.get("Peca_Esta_Obsoleta")),
                # Ainda sem regra para TEMPO_OBSOLETA_DIAS (texto no CSV); vamos tratar depois.
                "TEMPO_OBSOLETA_DIAS": None,
                "MARCA_PECA": self._safe_str(row.get("Nome_da_Marca_da_Peca")),
                "CODIGO_PECA_ESTOQUE": self._safe_str(row.get("Codigo_da_Peca_no_Estoque")),
            }

            # Validação Pydantic usando o model como contrato [file:35]
            try:
                model = BRZEstoquePecas(**brz)
                # Exclui ID (identity) para insert [file:35]
                out.append(model.model_dump(by_alias=True, exclude={"ID_ESTOQUE_PECA"}, exclude_none=False))
            except Exception as e:
                # Por ora: loga e ignora a linha (tratamento fino depois)
                context = inspect.currentframe()
                self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "ERRO!!!", f"[{NOME}] Linha ignorada por erro de validação: {e}")

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
        try:
            return float(v)
        except Exception:
            return None
