# mains/main_llm_agent.py

from __future__ import annotations

import os
import sys
import time
import re

# Garante import relativo do projeto (mesmo padrão das suas mains)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.data_analyst_agent import build_data_analyst_agent


def _sleep_from_rate_limit(err_msg: str) -> None:
    """
    Tenta respeitar o 'Please try again in XXXms' que vem no erro 429.
    Se não achar, aplica um fallback simples.
    """
    msg = (err_msg or "").lower()
    m = re.search(r"try again in (\d+)\s*ms", msg)
    if m:
        time.sleep(int(m.group(1)) / 1000)
    else:
        time.sleep(1.0)


def main():
    agent = build_data_analyst_agent()

    print("Agent ready. Ask a Question (or type 'exit').")
    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() in ("sair", "exit", "quit"):
            break

        try:
            result = agent.invoke({"input": user_input})
        except Exception as e:
            # Trata rate limit 429 (TPM/RPM)
            if "rate limit" in str(e).lower() or "429" in str(e):
                _sleep_from_rate_limit(str(e))
                result = agent.invoke({"input": user_input})
            else:
                raise

        print("\nAnswer:\n")
        print(result["output"])


if __name__ == "__main__":
    main()
