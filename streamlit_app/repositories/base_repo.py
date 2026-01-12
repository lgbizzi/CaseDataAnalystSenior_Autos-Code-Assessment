from __future__ import annotations

import inspect
import os
from typing import Any, Optional, Dict, List

import streamlit as st

from connector.oracle_connector import OracleConnector
from utils.logger_controller import LoggerController

import pandas as pd

NOME = "BaseRepository"
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, "BaseRepository.txt")
logger = LoggerController(logfile)


class BaseRepository:
    def __init__(self, config_file: str = "config/database.ini"):
        self._config_file = config_file

        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ",
                   f"Inicializando BaseRepository - config_file={config_file}")

    @staticmethod
    @st.cache_resource
    def _get_connector_cached(config_file: str) -> OracleConnector:
        return OracleConnector(config_file=config_file)

    def _get_connector(self) -> OracleConnector:
        return self._get_connector_cached(self._config_file)

    @staticmethod
    def _normalize_params(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return params or {}

    @st.cache_data(ttl=120, show_spinner=False)
    def query_dicts(_self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:


        """
        Executa SELECT e retorna resultados como lista de dicionários, com suporte
        a bind variables nomeadas (:dt_ini, :cod_filial, etc.).
        """
        p = _self._normalize_params(params)

        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ",
                   f"📊 query_dicts: {sql[:120]}...")
        if p:
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ",
                       f"Params: {p}")

        connector = _self._get_connector()

        try:
            with connector.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql, p)
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall() if columns else []
                finally:
                    cursor.close()

            results = [dict(zip(columns, row)) for row in rows]

            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ",
                       f"✅ query_dicts OK: {len(results)} registros retornados")
            return results

        except Exception as e:
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "ERRO!!!",
                       f"❌ query_dicts falhou: {e}")
            raise

    def query_one(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        rows = self.query_dicts(sql, params)
        return rows[0] if rows else {}


