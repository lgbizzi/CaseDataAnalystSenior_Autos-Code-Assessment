# views/estoque_pecas_view.py

from __future__ import annotations

from typing import Optional

from controllers.estoque_pecas_controller import EstoquePecasController


class EstoquePecasView:
    def __init__(self, controller: Optional[EstoquePecasController] = None):
        self.controller = controller or EstoquePecasController()

    def run(self, csv_path: str) -> int:
        return self.controller.run(csv_path)
