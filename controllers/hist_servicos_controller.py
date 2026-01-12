# controllers/hist_servicos_controller.py

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
from models.models import BRZHistServicos


NOME = "HistServicosController"

# criação do logger (uma vez, no início do script/classe)
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, f"{NOME}.txt")
logger = LoggerController(logfile)

class HistServicosController:
    TABLE_NAME = "BRZ_HIST_SERVICOS"

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
        self.logger.info(f"[{NOME}] Linhas lidas do CSV: {len(df)} | Delimitador detectado: '{read_result.delimiter}'")

        print("\nDataFrame: ")
        print(df)

        records = self._transform_to_brz_records(df)
        self.logger.info(f"[{NOME}] Registros prontos para insert: {len(records)}")

        if not records:
            self.logger.info(f"[{NOME}] Nada para inserir.")
            return 0

        inserted = self.connector.bulk_insert(self.TABLE_NAME, records)
        self.logger.info(f"[{NOME}] Inseridos no Oracle: {inserted}")
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

        # Map linha a linha
        for _, row in df.iterrows():
            brz = {
                "COD_CONCESSIONARIA": str(row.get("Cod_Concessionaria", "")).strip() or None,
                "COD_FILIAL": str(row.get("Cod_Filial", "")).strip() or None,
                "NOME_CONCESSIONARIA": self._safe_str(row.get("Nome_Da_Concessionaria", "")).strip() or None,
                "NOME_FILIAL": self._safe_str(row.get("Nome_Da_Filial", "")).strip() or None,
                "DT_REALIZACAO_SERVICO": parse_date_yyyy_mm_dd(row.get("Data_De_Realizacao_Do_Servico")),
                "QTDE_SERVICOS": self._safe_int(row.get("Quantidade_De_Servicos_Realizados")),
                "VALOR_TOTAL_SERVICO": self._safe_float(row.get("Valor_Total_Do_Servico_Realizado")),
                "LUCRO_SERVICO": self._safe_float(row.get("Lucro_Do_Servico")),
                "DESCRICAO_SERVICO": self._safe_str(row.get("Descricao_Do_Servico_Feito", "")).strip() or None,
                "SECAO_SERVICO": str(row.get("Secao_Que_O_Servico_Foi_Feito", "")).strip() or None,
                "DEPARTAMENTO_SERVICO": str(row.get("Departamento_Que_Realizou_O_Servico", "")).strip() or None,
                "CATEGORIA_SERVICO": str(row.get("Categoria_Do_Servico", "")).strip() or None,
                "NOME_VENDEDOR_SERVICO": self._safe_str(row.get("Nome_Do_Vendedor_Que_Vendeu_O_Servico", "")).strip() or None,
                "NOME_MECANICO": self._safe_str(row.get("Nome_Do_Mecanico_Que_Fez_O_Servico", "")).strip() or None,
                "NOME_CLIENTE": self._safe_str(row.get("Nome_Do_Cliente_Que_Fez_O_Servico", "")).strip() or None,
            }

            # Validação Pydantic usando o model como contrato [file:35]
            try:
                model = BRZHistServicos(**brz)
                # Exclui ID (identity) para insert [file:35]
                out.append(model.model_dump(by_alias=True, exclude={"ID_SERVICO"}, exclude_none=False))
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
        
    def _safe_int(self, v: Any) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        try:
            return int(v)
        except Exception:
            return None