# views/hist_servicos_view.py

from __future__ import annotations

from typing import Optional

from controllers.hist_servicos_controller import HistServicosController


class HistServicosView:
    def __init__(self, controller: Optional[HistServicosController] = None):
        self.controller = controller or HistServicosController()

    def run(self, csv_path: str) -> int:
        return self.controller.run(csv_path)