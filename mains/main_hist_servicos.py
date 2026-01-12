# mains/main_hist_servicos.py

from __future__ import annotations

import os
import sys

# Garante import relativo do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from views.hist_servicos_view import HistServicosView


def main():
    # Resolve o caminho a partir da raiz do projeto (independente do working directory)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_path = os.path.join(base_dir, "bases", "historico-de-servicos-realizados.csv")

    view = HistServicosView()
    inserted = view.run(csv_path)

    print(f"[main_hist_servicos] Linhas inseridas: {inserted}")


if __name__ == "__main__":
    main()
