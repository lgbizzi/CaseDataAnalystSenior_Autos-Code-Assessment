# mains/main_hist_vendas_veiculos.py

from __future__ import annotations

import os
import sys

# Garante import relativo do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from views.hist_vendas_veiculos_view import HistVendasVeiculosView


def main():
    # Resolve o caminho a partir da raiz do projeto (independente do working directory)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_path = os.path.join(base_dir, "bases", "historico-de-vendas-de-veiculos.csv")

    view = HistVendasVeiculosView()
    inserted = view.run(csv_path)

    print(f"[main_hist_vendas_veiculos] Linhas inseridas: {inserted}")


if __name__ == "__main__":
    main()
