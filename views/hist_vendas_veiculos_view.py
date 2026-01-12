# views/hist_vendas_veiculos_view.py

from __future__ import annotations

from typing import Optional
from controllers.hist_vendas_veiculos_controller import HistVendasVeiculosController


class HistVendasVeiculosView:
    def __init__(self, controller: Optional[HistVendasVeiculosController] = None):
        self.controller = controller or HistVendasVeiculosController()

    def run(self, csv_path: str) -> int:
        return self.controller.run(csv_path)
