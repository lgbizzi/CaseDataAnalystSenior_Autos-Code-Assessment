# views/hist_vendas_pecas_view.py

from __future__ import annotations

from typing import Optional
from controllers.hist_vendas_pecas_controller import HistVendasPecasController


class HistVendasPecasView:
    def __init__(self, controller: Optional[HistVendasPecasController] = None):
        self.controller = controller or HistVendasPecasController()

    def run(self, csv_path: str) -> int:
        return self.controller.run(csv_path)
