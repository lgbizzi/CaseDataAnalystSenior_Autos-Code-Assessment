from __future__ import annotations

import configparser
import hmac
import inspect
import os
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from utils.logger_controller import LoggerController


NOME = "AuthService"
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, "AuthService.txt")
logger = LoggerController(logfile)


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


class AuthService:
    def __init__(self, config_file: str | None = None):
        # Default absoluto: .../streamlit_app/config/config.ini
        default_path = Path(__file__).resolve().parents[1] / "config" / "config.ini"
        self.config_file = Path(config_file).resolve() if config_file else default_path

        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(
            NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ",
            f"Inicializando AuthService - config_file={self.config_file}"
        )

    @staticmethod
    @st.cache_data(ttl=10, show_spinner=False)
    def _load_config_cached(config_file_str: str, file_mtime: float) -> Credentials:
        """
        Lê credenciais do INI.
        - cache_data (não resource) porque o conteúdo pode mudar em dev.
        - file_mtime entra como parte da chave do cache para invalidar quando o arquivo muda.
        """
        config_file = Path(config_file_str)

        if not config_file.exists():
            raise FileNotFoundError(f"Arquivo de config não encontrado: {config_file}")

        config = configparser.ConfigParser()
        config.read(config_file, encoding="utf-8")

        if not config.has_section("AUTH"):
            raise ValueError("Seção [AUTH] não encontrada no config.ini")

        user = config.get("AUTH", "username", fallback="").strip()
        pwd = config.get("AUTH", "password", fallback="").strip()

        if not user or not pwd:
            raise ValueError("Credenciais vazias no [AUTH] (username/password).")

        return Credentials(username=user, password=pwd)

    def get_credentials(self) -> Credentials:
        mtime = self.config_file.stat().st_mtime

        creds = self._load_config_cached(str(self.config_file), mtime)

        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(
            NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ",
            f"Credenciais carregadas para usuário={creds.username} | arquivo={self.config_file}"
        )

        return creds

    def authenticate(self, username: str, password: str) -> bool:
        creds = self.get_credentials()

        user_ok = hmac.compare_digest((username or "").strip(), creds.username)
        pass_ok = hmac.compare_digest((password or "").strip(), creds.password)

        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(
            NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ",
            f"Tentativa de login - user={username!r} - ok={user_ok and pass_ok}"
        )

        return user_ok and pass_ok
