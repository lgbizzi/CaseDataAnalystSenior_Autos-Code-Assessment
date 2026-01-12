# controllers/estoque_veiculos_controller.py

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
from models.models import BRZEstoqueVeiculos

NOME = "EstoqueVeiculosController"

# logger singleton no padrão
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, f"{NOME}.txt")
logger = LoggerController(logfile)


class EstoqueVeiculosController:
    TABLE_NAME = "BRZ_ESTOQUE_VEICULOS"  # [file:34]

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

        df = self._fix_duplicate_dt_entrada_columns(df)
        df = self._dedupe_rows(df)

        records = self._transform_to_brz_records(df)
        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:",f"[{NOME}] Registros prontos para insert: {len(records)}")

        if not records:
            context = inspect.currentframe()
            self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:",f"[{NOME}] Nada para inserir.")
            return 0

        inserted = self.connector.bulk_insert(self.TABLE_NAME, records)
        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:",f"[{NOME}] Inseridos no Oracle: {inserted}")
        return inserted

    # -------------------------
    # Regras de CODs (derivação)
    # -------------------------
    def _map_cod_concessionaria(self, nome_concessionaria: Optional[str]) -> Optional[str]:
        # Regra informada: Nome_Concessionaria == 'CCM' => COD_CONCESSIONARIA = '0'
        if not nome_concessionaria:
            return None
        if nome_concessionaria.strip().upper() == "CCM":
            return "0"
        # fallback: mantém o próprio valor (ajuste se tiver outros mapeamentos)

        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"Coluna 'COD_CONCESSIONARIA' tratada.")
        return nome_concessionaria.strip()

    def _map_cod_filial(self, nome_filial: Optional[str], cod_concessionaria: Optional[str]) -> Optional[str]:
        # Regras informadas:
        # 'CCM AUTOS 1' => '0-1-1'
        # 'CCM AUTOS 2' => '0-1-2'
        # 'CCM AUTOS 3' => '0-1-3'
        if not nome_filial:
            return None

        nf = nome_filial.strip().upper()

        if nf == "CCM AUTOS 1":
            return "0-1-1"
        if nf == "CCM AUTOS 2":
            return "0-1-2"
        if nf == "CCM AUTOS 3":
            return "0-1-3"

        # fallback: tenta prefixar com o cod_concessionaria se existir
        if cod_concessionaria:
            return f"{cod_concessionaria}-1-0"

        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"Coluna 'COD_FILIAL' tratada.")
        return nome_filial.strip()

    # -------------------------
    # Correção de colunas repetidas
    # -------------------------
    def _fix_duplicate_dt_entrada_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        No CSV a coluna 'Data_de_Entrada_do_Veiculo_no_Estoque' aparece 3 vezes. [file:42]
        Regra: criar/usar uma coluna canônica e pegar a primeira data não nula por linha.
        """
        base = "Data_de_Entrada_do_Veiculo_no_Estoque"

        # pega a canônica + possíveis renomes (_1, _2) do CSVHandler
        cols = []
        for c in df.columns:
            if c == base or c.startswith(base + "_"):
                cols.append(c)

        if len(cols) <= 1:
            return df

        canonical = base if base in df.columns else cols[0]

        def pick_first(row):
            for c in cols:
                v = row.get(c)
                if v is None:
                    continue
                if isinstance(v, float) and pd.isna(v):
                    continue
                s = str(v).strip()
                if s and s.lower() not in ("nan", "none"):
                    return s
            return None

        df[canonical] = df.apply(pick_first, axis=1)

        to_drop = [c for c in cols if c != canonical and c in df.columns]
        df = df.drop(columns=to_drop)

        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:",
                        f"DT_ENTRADA: mantida='{canonical}', removidas={to_drop}")
        return df

    # -------------------------
    # Deduplicação de linhas
    # -------------------------
    def _dedupe_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Como o CSV não traz chassi/placa, dedupe por conjunto estável.
        (O banco tem UNIQUE(CHASSI_VEICULO), mas como ele vem None aqui, não dá para usar.) [file:34][file:42]
        """
        strong_cols = [
            "Nome_da_Concessionaria",
            "Nome_da_Filial",
            "Marca_do_Veiculo",
            "Modelo_do_Veiculo",
            "Cor_do_Veiculo",
            "Ano_Modelo_do_Veiculo",
            "Ano_Fabricacao_do_Veiculo",
            "Data_de_Entrada_do_Veiculo_no_Estoque",
        ]
        subset = [c for c in strong_cols if c in df.columns]

        before = len(df)
        df = df.drop_duplicates(subset=subset, keep="first") if subset else df.drop_duplicates(keep="first")
        after = len(df)

        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:",
                        f"Dedup linhas: antes={before} depois={after} subset={subset if subset else 'FULL'}")
        return df

    # -------------------------
    # Transformação para BRZ_*
    # -------------------------
    def _transform_to_brz_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []

        def parse_date_dd_mm_yyyy(val: Any) -> Optional[date]:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            s = str(val).strip()
            if not s or s.lower() in ("nan", "none"):
                return None
            try:
                return datetime.strptime(s, "%d/%m/%Y").date()
            except Exception:
                return None

        for _, row in df.iterrows():
            nome_conc = self._safe_str(row.get("Nome_da_Concessionaria"))
            nome_fil = self._safe_str(row.get("Nome_da_Filial"))

            cod_conc = self._map_cod_concessionaria(nome_conc)
            cod_fil = self._map_cod_filial(nome_fil, cod_conc)

            brz = {
                "COD_CONCESSIONARIA": cod_conc,
                "COD_FILIAL": cod_fil,

                "NOME_CONCESSIONARIA": nome_conc,
                "NOME_FILIAL": nome_fil,
                "MARCA_FILIAL": self._safe_str(row.get("Marca_da_Filial")),

                "CUSTO_VEICULO": self._safe_float(row.get("Custo_do_Veiculo")),

                "MARCA_VEICULO": self._safe_str(row.get("Marca_do_Veiculo")),
                "MODELO_VEICULO": self._safe_str(row.get("Modelo_do_Veiculo")),
                "COR_VEICULO": self._safe_str(row.get("Cor_do_Veiculo")),

                "VEICULO_NOVO_SEMINOVO": self._safe_str(row.get("Veiculo_Novo_ou_Semi_Novo")),
                "TIPO_COMBUSTIVEL": self._safe_str(row.get("Tipo_do_Combustivel")),

                "ANO_MODELO": self._safe_int(row.get("Ano_Modelo_do_Veiculo")),
                "ANO_FABRICACAO": self._safe_int(row.get("Ano_Fabricacao_do_Veiculo")),

                "CHASSI_VEICULO": self._safe_str(row.get("Chassi_do_Veiculo")),
                "TEMPO_TOTAL_ESTOQUE_DIAS": self._parse_tempo_total_dias(row.get("Tempo_Total_no_Estoque")),
                "KM_ATUAL": self._safe_int(row.get("Kilometragem_Atual_do_Veiculo")),
                "PLACA_VEICULO": self._safe_str(row.get("Placa_do_Veiculo")),

                "DT_ENTRADA_ESTOQUE": parse_date_dd_mm_yyyy(row.get("Data_de_Entrada_do_Veiculo_no_Estoque")),
            }

            try:
                model = BRZEstoqueVeiculos(**brz)
                # Identity existe no model, então excluir explicitamente do insert
                out.append(model.model_dump(by_alias=True, exclude={"ID_ESTOQUE_VEICULO"}, exclude_none=False))
            except Exception as e:
                context = inspect.currentframe()
                self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno,
                                "ERRO!!!", f"[{NOME}] Linha ignorada por erro de validação: {e}")

        return out

    # -------------------------
    # Parsers e helpers
    # -------------------------
    def _parse_tempo_total_dias(self, v: Any) -> Optional[int]:
        """
        No CSV, 'Tempo_Total_no_Estoque' vem textual (ex.: 'MENOS DE 1 MES', '1 A 3 MESES', '2 A 3 ANOS'). [file:42]
        Converte para dias aproximados (regra simples, suficiente para BRZ).
        """
        s = self._safe_str(v)
        if not s:
            return None
        u = s.upper()

        if "MENOS DE 1 MES" in u:
            return 15
        if "1 A 3 MESES" in u:
            return 60
        if "3 A 6 MESES" in u:
            return 135
        if "6 A 9 MESES" in u:
            return 225
        if "9 A 12 MESES" in u:
            return 315
        if "1 A 2 ANOS" in u:
            return 540
        if "2 A 3 ANOS" in u:
            return 900

        # fallback: tenta extrair número (se vier algo diferente)

        context = inspect.currentframe()
        self.logger.log(NOME, os.path.dirname(__file__), __name__, context.f_lineno, "INFO:", f"Coluna 'TEMPO_TOTAL_ESTOQUE_DIAS' tratada.")
        return self._safe_int(s)

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
        # aceita tanto 178139.58 quanto 178.139,58
        s2 = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
        try:
            return float(s2)
        except Exception:
            return None

    def _safe_int(self, v: Any) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        s = str(v).strip()
        if not s or s.lower() in ("nan", "none"):
            return None
        try:
            return int(float(s.replace(",", ".")))
        except Exception:
            return None
