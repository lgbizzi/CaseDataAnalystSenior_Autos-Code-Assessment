# agents/sql_oracle_tool.py

from __future__ import annotations

import re
from typing import Any, Dict, List, ClassVar, Type, Optional

from pydantic import BaseModel, Field, PrivateAttr

from connector.oracle_connector import OracleConnector  # sua conexão [file:39]
from langchain_core.tools import BaseTool


def _is_select_only(sql: str) -> bool:
    s = (sql or "").strip().lower()
    if not s.startswith("select"):
        return False
    blocked = ["insert", "update", "delete", "merge", "drop", "alter", "truncate", "create", "grant", "revoke"]
    return not any(re.search(rf"\b{kw}\b", s) for kw in blocked)

def _strip_markdown_fences(text: str) -> str:
    if not text:
        return text
    s = text.strip()

    # Remove ```sql ... ``` ou ``` ... ```
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", s)  # remove a primeira linha ```sql
        s = re.sub(r"\n?```$", "", s)               # remove o ``` final
        s = s.strip()

    return s

class OracleSQLInput(BaseModel):
    sql: str = Field(..., description="Query SQL (apenas SELECT).")
    limit: int = Field(200, description="Limite máximo de linhas retornadas.")


class OracleSQLTool(BaseTool):
    name: str = "oracle_sql_query"
    description: str = "Executa uma consulta SQL (somente SELECT) no Oracle e retorna uma lista de linhas (dict)."

    args_schema: ClassVar[Type[BaseModel]] = OracleSQLInput

    # atributo privado (não é field do Pydantic)
    # para rodar com a OracleConnector que já existe
    _connector: OracleConnector = PrivateAttr()

    def __init__(self, connector: Optional[OracleConnector] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self._connector = connector or OracleConnector()

    def _run(self, sql: str, limit: int = 200) -> List[Dict[str, Any]]:
        # 1) Limpa markdown fences e ; antes de validar
        sql_clean = _strip_markdown_fences(sql)
        sql_clean = (sql_clean or "").strip().rstrip(";")

        # 2) Valida SELECT-only no texto limpo
        if not _is_select_only(sql_clean):
            raise ValueError("Apenas SELECT é permitido nesta ferramenta.")

        lower = sql_clean.lower()

        # 3) Limite defensivo com ROWNUM (Oracle)
        if "fetch first" not in lower and "rownum" not in lower:
            sql_clean = f"""
            SELECT * FROM (
                {sql_clean}
            ) WHERE ROWNUM <= {int(limit)}
            """

        return self._connector.execute_query(sql_clean, fetchall=True)
