# controllers/hist_vendas_veiculos_controller.py

from __future__ import annotations

import os
import sys
import inspect
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional

import pandas as pd

# Garante import relativo do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connector.oracle_connector import OracleConnector  # [file:39]
from utils.csv_handler import CSVHandler
from utils.logger_controller import LoggerController
from models.models import BRZHistVendasVeiculos

NOME = "HistVendasVeiculosController"

# logger singleton no padrão
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, f"{NOME}.txt")
logger = LoggerController(logfile)


class HistVendasVeiculosController:
    TABLE_NAME = "BRZ_HIST_VENDAS_VEICULOS"  # [file:37]

    UFS_VALIDAS = {
        "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
        "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"
    }

    MACROREGIOES_VALIDAS = {"NORTE", "NORDESTE", "CENTRO-OESTE", "SUDESTE", "SUL"}

    # padrão de chassi (VIN): 17 caracteres alfanuméricos (sem I,O,Q normalmente; mas não vamos impor)
    VIN_RE = re.compile(r"^[A-Z0-9]{10,20}$")  # flexível p/ sujeira: 10-20, mas 17 costuma ser o correto

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
        self.logger.info(f"[{NOME}] Linhas lidas do CSV: {len(df)} | Delimitador detectado: '{read_result.delimiter}'")

        # Remove coluna extra sem título no final (no arquivo aparece um ';' extra no header) [file:44]
        df = self._drop_unnamed_last_column(df)

        records = self._transform_to_brz_records(df)
        self.logger.info(f"[{NOME}] Registros prontos para insert: {len(records)}")

        if not records:
            self.logger.info(f"[{NOME}] Nada para inserir.")
            return 0

        inserted = self.connector.bulk_insert(self.TABLE_NAME, records)
        self.logger.info(f"[{NOME}] Inseridos no Oracle: {inserted}")
        return inserted

    # -------------------------
    # Regras de COD_FILIAL
    # -------------------------
    def _map_cod_filial(self, nome_filial: Optional[str], cod_concessionaria: Optional[str]) -> Optional[str]:
        # mesmo padrão usado antes (Estoque Veículos / instrução do usuário)
        if not nome_filial:
            return None

        nf = nome_filial.strip().upper()

        if nf == "CCM AUTOS 1":
            return "0-1-1"
        if nf == "CCM AUTOS 2":
            return "0-1-2"
        if nf == "CCM AUTOS 3":
            return "0-1-3"

        if cod_concessionaria:
            return f"{cod_concessionaria}-1-0"

        return nome_filial.strip()

    # -------------------------
    # Tratamentos estruturais
    # -------------------------
    def _drop_unnamed_last_column(self, df: pd.DataFrame) -> pd.DataFrame:
        # quando existe ';' no final do header, costuma virar uma coluna vazia
        empty_named = [c for c in df.columns if not str(c).strip() or str(c).strip().lower().startswith("unnamed")]
        if empty_named:
            df = df.drop(columns=empty_named)
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
            # Base fields (como vêm do CSV)
            cod_conc_raw = self._safe_str(row.get("Cod_Concessionaria"))
            cod_fil_raw = self._safe_str(row.get("Cod_Filial"))
            nome_filial = self._safe_str(row.get("Nome_da_Filial"))

            # Padroniza COD_FILIAL pela regra baseada no nome (você pediu explicitamente)
            cod_fil = self._map_cod_filial(nome_filial, cod_conc_raw) or cod_fil_raw

            vendedor = self._fix_mojibake(self._safe_str(row.get("Nome_do_Vendedor_que_Realizou_a_Venda")))
            comprador = self._fix_mojibake(self._safe_str(row.get("Nome_do_Comprador_do_Veiculo")))

            # UF restrita
            uf = self._safe_str(row.get("Estado_Brasileiro_da_Venda"))
            uf = uf.upper().strip() if uf else None
            if uf and uf not in self.UFS_VALIDAS:
                uf = None

            # Macroregião restrita
            macro = self._safe_str(row.get("Macroregiao_Geografica_da_Venda"))
            macro = macro.upper().strip() if macro else None
            if macro and macro not in self.MACROREGIOES_VALIDAS:
                macro = None

            # Tratamento do "deslocamento":
            # Se 'Dias_que_o_Carro_Ficou_no_Estoque' vier com cara de VIN (ex.: 9BWAG45U4PT01905),
            # significa que as colunas seguintes foram deslocadas uma posição.
            dias_raw = self._safe_str(row.get("Dias_que_o_Carro_Ficou_no_Estoque"))
            looks_like_vin = bool(dias_raw and self.VIN_RE.match(dias_raw))

            # padrão: dias como int; se sujo (vin), zera os campos afetados e guarda o VIN em CHASSI_VEICULO
            chassi = self._safe_str(row.get("Chassi_do_Veiculo"))  # no header não existe; fica None [file:44]
            dias_em_estoque = self._safe_int(row.get("Dias_que_o_Carro_Ficou_no_Estoque"))

            tipo_venda_veiculo = self._safe_str(row.get("Tipo_de_Venda_do_Veiculo"))
            cidade = self._safe_str(row.get("Cidade_da_Venda"))

            if looks_like_vin:
                chassi = dias_raw  # VIN caiu na coluna de dias [file:44]
                dias_em_estoque = None

                # E o restante fica comprometido (você descreveu que desloca as próximas colunas)
                tipo_venda_veiculo = None
                vendedor = None
                comprador = None
                cidade = None
                uf = None
                macro = None

            brz = {
                "COD_CONCESSIONARIA": cod_conc_raw,
                "COD_FILIAL": cod_fil,

                "NOME_CONCESSIONARIA": self._safe_str(row.get("Nome_da_Concessionaria")),
                "NOME_FILIAL": nome_filial,
                "MARCA_FILIAL": self._safe_str(row.get("Marca_da_Filial")),

                "DT_VENDA": parse_date_dd_mm_yyyy(row.get("Data_da_Venda")),

                "QTDE_VENDIDA": self._safe_int(row.get("Quantidade_Vendida")),
                "TIPO_TRANSACAO": self._safe_str(row.get("Tipo_de_Transacao")),

                "VALOR_VENDA": self._safe_float(row.get("Valor_da_Venda")),
                "CUSTO_VEICULO": self._safe_float(row.get("Custo_do_Veiculo")),
                "LUCRO_VENDA": self._safe_float(row.get("Lucro_da_Venda")),
                "MARGEM_VENDA": self._safe_float(row.get("Margem_da_Venda")),

                "MARCA_VEICULO": self._safe_str(row.get("Marca_do_Veiculo")),
                "MODELO_VEICULO": self._safe_str(row.get("Modelo_do_Veiculo")),
                "FAMILIA_VEICULO": self._safe_str(row.get("Familia_do_Veiculo")),
                "CATEGORIA_VEICULO": self._safe_str(row.get("Categoria_do_Veiculo")),
                "COR_VEICULO": self._safe_str(row.get("Cor_do_Veiculo")),

                "VEICULO_NOVO_SEMINOVO": self._safe_str(row.get("Veiculo_Novo_ou_Semi_Novo")),
                "TIPO_COMBUSTIVEL": self._safe_str(row.get("Tipo_do_Combustivel")),

                "ANO_MODELO": self._safe_int(row.get("Ano_Modelo_do_Veiculo")),
                "ANO_FABRICACAO": self._safe_int(row.get("Ano_Fabricacao_do_Veiculo")),

                "CHASSI_VEICULO": chassi,
                "DIAS_EM_ESTOQUE": dias_em_estoque,

                "TIPO_VENDA_VEICULO": tipo_venda_veiculo,
                "NOME_VENDEDOR": vendedor,
                "NOME_COMPRADOR": comprador,

                "CIDADE_VENDA": cidade,
                "ESTADO_VENDA": uf,
                "MACROREGIAO_VENDA": macro,
            }

            try:
                model = BRZHistVendasVeiculos(**brz)
                # ID_VENDA_VEICULO está comentado no seu contrato, então não precisa excluir.
                out.append(model.model_dump(by_alias=True, exclude_none=False))
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

    def _fix_mojibake(self, s: Optional[str]) -> Optional[str]:
        if not s:
            return s
        try:
            return s.encode("latin1").decode("utf-8")
        except Exception:
            return s
