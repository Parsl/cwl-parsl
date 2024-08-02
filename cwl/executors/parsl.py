from __future__ import annotations

from typing import Callable, Dict

import parsl
from parsl.app.bash import BashApp
from parsl.concurrent import ParslPoolExecutor
from parsl.executors import HighThroughputExecutor
from parsl.executors.threads import ThreadPoolExecutor


class CWLExecutor(ParslPoolExecutor):
    def __init__(self, config: parsl.Config = None):
        if config is None:
            config = parsl.Config(
                executors=[HighThroughputExecutor()],
            )
        super().__init__(config)
        self._app_cache: Dict[callable, BashApp] = {}

    def _get_app(self, fn: Callable) -> BashApp:
        """Create a BashApp for a function

        Args:
            fn: Function to be turned into a Parsl app
        Returns:
            BashApp version of that function
        """
        if fn in self._app_cache:
            return self._app_cache[fn]
        app = BashApp(fn, data_flow_kernel=self.dfk)
        self._app_cache[fn] = app
        return app
