# utils/csv_handler.py

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Iterable
import sys

import pandas as pd

# Ajuste do path para manter compatível com o padrão usado no connector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger_controller import LoggerController

NOME = "csv_handler"

# criação do logger (uma vez, no início do script/classe)
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, f"{NOME}.txt")
logger = LoggerController(logfile)

@dataclass
class CSVReadResult:
    df: pd.DataFrame
    delimiter: str
    encoding: str
    columns_original: List[str]
    file_path: str


class CSVHandler:
    """
    CSVHandler
    - Detecta automaticamente delimitador (',' ou ';')
    - Detecta encoding (utf-8 / utf-8-sig / latin-1) com fallback
    - Lê CSV com pandas em modo tolerante
    - Opcional: normaliza nomes de colunas
    - Opcional: salva linhas rejeitadas em arquivo para inspeção
    """

    NAME = "CSVHandler"

    def __init__(self, log_directory: str = "logs"):
        self.logger = logger

    # -------------------------
    # Public API
    # -------------------------
    def read_csv(
        self,
        file_path: Union[str, Path],
        *,
        normalize_columns: bool = False,
        expected_columns: Optional[List[str]] = None,
        dtype: Optional[Dict[str, str]] = None,
        keep_default_na: bool = True,
        save_rejected_rows: bool = True,
        rejected_dir: Union[str, Path] = "rejected_rows",
        sample_size_bytes: int = 64 * 1024,
    ) -> CSVReadResult:
        """
        Lê CSV com autodetecção de delimitador e encoding.

        Args:
            file_path: caminho do arquivo.
            normalize_columns: se True, normaliza colunas (strip + espaços -> '_' e remove BOM).
            expected_columns: se informado, valida presença (após normalização, se habilitada).
            dtype: dtypes opcionais para pandas.
            keep_default_na: comportamento padrão do pandas para NA.
            save_rejected_rows: salva linhas "ruins" em arquivo (quando possível).
            rejected_dir: pasta para guardar rejeitados.
            sample_size_bytes: tamanho do sample para sniff de delimiter/encoding.

        Returns:
            CSVReadResult (df, delimiter, encoding, colunas originais).
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV não encontrado: {path}")

        encoding = self._detect_encoding(path, sample_size_bytes=sample_size_bytes)
        delimiter = self._detect_delimiter(path, encoding=encoding, sample_size_bytes=sample_size_bytes)

        self.logger.info(f"[CSVHandler] Lendo arquivo: {path}")
        self.logger.info(f"[CSVHandler] Encoding: {encoding} | Delimiter: '{delimiter}'")

        # Pandas: engine python é mais tolerante com separadores e linhas fora do padrão
        # on_bad_lines:
        # - 'skip' pula linhas ruins
        # - callable permite capturar (pandas >= 1.3); aqui mantemos simples e auditável
        rejected_path = None
        if save_rejected_rows:
            rejected_path = self._rejected_file_path(path, rejected_dir=rejected_dir)
            os.makedirs(Path(rejected_path).parent, exist_ok=True)

        # Leitura principal
        # Nota: on_bad_lines='skip' evita quebrar por linhas com colunas a mais/menos.
        df = pd.read_csv(
            path,
            sep=delimiter,
            encoding=encoding,
            dtype=dtype,
            keep_default_na=keep_default_na,
            engine="python",
            on_bad_lines="skip",
        )

        columns_original = list(df.columns)

        # Normalização opcional de colunas
        if normalize_columns:
            df.columns = [self._normalize_colname(c) for c in df.columns]

        # Validação de colunas esperadas (opcional)
        if expected_columns:
            missing = [c for c in expected_columns if c not in df.columns]
            if missing:
                raise ValueError(
                    f"Colunas esperadas não encontradas em {path.name}: {missing}. "
                    f"Colunas presentes: {list(df.columns)}"
                )

        # Detectar headers duplicados (muito comum quando CSV vem com coluna repetida)
        duplicates = self._find_duplicate_columns(df.columns)
        if duplicates:
            self.logger.info(f"[CSVHandler] Atenção: colunas duplicadas detectadas: {duplicates}")

        # Tentativa de auditoria de rejeitados:
        # pandas não expõe diretamente as linhas "puladas" por on_bad_lines='skip'.
        # Então aqui é melhor gerar um arquivo "rejeitados" via varredura simples do CSV,
        # comparando o número de campos por linha com o número de colunas esperado.
        if save_rejected_rows:
            try:
                self._export_rejected_rows_simple(
                    path=path,
                    encoding=encoding,
                    delimiter=delimiter,
                    expected_n_fields=len(columns_original),
                    output_path=rejected_path,
                )
                self.logger.info(f"[CSVHandler] Rejeitados (heurística): {rejected_path}")
            except Exception as e:
                self.logger.error(f"[CSVHandler] Falha ao gerar rejeitados: {e}")

        return CSVReadResult(
            df=df,
            delimiter=delimiter,
            encoding=encoding,
            columns_original=columns_original,
            file_path=str(path),
        )

    # -------------------------
    # Detection helpers
    # -------------------------
    def _detect_encoding(self, path: Path, *, sample_size_bytes: int) -> str:
        """
        Detecta encoding com fallback simples.
        Prioriza utf-8/utf-8-sig e cai para latin-1 (muito comum em Windows).
        """
        candidates = ["utf-8-sig", "utf-8", "latin-1"]
        raw = path.read_bytes()[:sample_size_bytes]

        for enc in candidates:
            try:
                raw.decode(enc)
                return enc
            except UnicodeDecodeError:
                continue

        # fallback final
        return "latin-1"

    def _detect_delimiter(self, path: Path, *, encoding: str, sample_size_bytes: int) -> str:
        """
        Detecta delimitador entre ',' e ';' usando:
        - csv.Sniffer em amostra
        - fallback por contagem de ocorrências
        """
        sample = path.read_bytes()[:sample_size_bytes].decode(encoding, errors="replace")

        # csv.Sniffer às vezes erra se o sample tiver muito texto, então limitamos delimiters
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";"])
            if dialect.delimiter in [",", ";"]:
                return dialect.delimiter
        except Exception:
            pass

        # fallback: contagem simples
        comma = sample.count(",")
        semicolon = sample.count(";")
        return ";" if semicolon > comma else ","

    # -------------------------
    # Column helpers
    # -------------------------
    def _normalize_colname(self, col: str) -> str:
        # Remove BOM/whitespace e padroniza espaços
        c = (col or "").replace("\ufeff", "").strip()
        c = c.replace(" ", "_")
        # Evita "__"
        while "__" in c:
            c = c.replace("__", "_")
        return c

    def _find_duplicate_columns(self, cols: Iterable[str]) -> List[str]:
        seen = set()
        dup = []
        for c in cols:
            if c in seen and c not in dup:
                dup.append(c)
            seen.add(c)
        return dup

    # -------------------------
    # Rejected rows export
    # -------------------------
    def _rejected_file_path(self, path: Path, *, rejected_dir: Union[str, Path]) -> str:
        rejected_dir = Path(rejected_dir)
        return str(rejected_dir / f"{path.stem}__rejected.csv")

    def _export_rejected_rows_simple(
        self,
        *,
        path: Path,
        encoding: str,
        delimiter: str,
        expected_n_fields: int,
        output_path: str,
        max_rejected: int = 50_000,
    ) -> None:
        """
        Heurística simples:
        - lê o CSV linha a linha
        - marca como rejeitada qualquer linha cujo nº de colunas != expected_n_fields
        - escreve essas linhas num arquivo para auditoria
        """
        rejected_count = 0
        wrote_header = False

        with path.open("r", encoding=encoding, errors="replace", newline="") as f_in:
            reader = csv.reader(f_in, delimiter=delimiter)

            for i, row in enumerate(reader):
                # pula header (linha 0)
                if i == 0:
                    continue

                if len(row) != expected_n_fields:
                    if rejected_count >= max_rejected:
                        break

                    # cria arquivo apenas quando encontrar o primeiro rejeitado
                    mode = "w" if not wrote_header else "a"
                    with open(output_path, mode, encoding="utf-8", newline="") as f_out:
                        w = csv.writer(f_out)
                        if not wrote_header:
                            w.writerow(["line_number", "n_fields", "raw_row"])
                            wrote_header = True
                        w.writerow([i + 1, len(row), "|".join(row)])

                    rejected_count += 1

        if rejected_count == 0 and wrote_header:
            # não deve ocorrer, mas por segurança
            try:
                os.remove(output_path)
            except OSError:
                pass
