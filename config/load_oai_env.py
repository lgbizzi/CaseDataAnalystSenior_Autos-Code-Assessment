# config/load_oai_env.py

from __future__ import annotations

import os
from dotenv import load_dotenv


def load_oai_env() -> None:
    # Caminho absoluto para evitar dependência do working directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(base_dir, "config", "oai.env")

    loaded = load_dotenv(dotenv_path=env_path, override=False)
    if not loaded:
        raise FileNotFoundError(f"Arquivo de ambiente não encontrado ou vazio: {env_path}")
