# views/estoque_veiculos_view.py

from __future__ import annotations

from typing import Optional
from controllers.estoque_veiculos_controller import EstoqueVeiculosController


class EstoqueVeiculosView:
    def __init__(self, controller: Optional[EstoqueVeiculosController] = None):
        self.controller = controller or EstoqueVeiculosController()

    def run(self, csv_path: str) -> int:
        return self.controller.run(csv_path)
