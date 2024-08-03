from __future__ import annotations

from typing import Any, Callable, Dict

import parsl
from parsl.app.bash import BashApp
from parsl.concurrent import ParslPoolExecutor

from cwl.executors.config import ExecutorConfig


class CWLExecutor(ParslPoolExecutor):
    def __init__(self, config: parsl.Config) -> None:
        """Parsl executor for CWL apps

        Submit CWL apps to run using Parsl

        Args:
            config: Parsl configuration object
        """
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


class ParslConfig(ExecutorConfig):
    def __init__(self, config_options: Dict[str, Any]) -> None:
        """Create a Parsl configuration object

        Args:
            config_options: Parsl configuration options
                {
                    "type": "htex" | "thread",
                    "options": Dict[str, Any]  # Options for the parsl config
                }
        """
        self._config = self._create_parsl_config(config_options=config_options)

    def get_config(self) -> parsl.Config:
        """Get the Parsl configuration object"""
        return self._config

    def _create_parsl_config(
        self, config_options: Dict[str, Any]
    ) -> parsl.Config:
        """Create a Parsl configuration object

        Args:
            config_options: Parsl configuration options

        Returns:
            Parsl configuration object
        """
        config_type = config_options["type"]
        options = config_options.get("options", {})

        if config_type == "htex":
            return self._create_htex_config(options)

        elif config_type == "thread":
            return self._create_thread_config(options)
        else:
            raise ValueError(f"Unknown Parsl executor type: {config_type}")

    def _create_htex_config(self, options: Dict[str, Any]) -> parsl.Config:
        """Create a Parsl HighThroughputExecutor configuration object

        Args:
            options: Options for the HighThroughputExecutor

        Returns:
            HighThroughputExecutor configuration object
        """
        return parsl.Config(
            executors=[
                parsl.executors.HighThroughputExecutor(label="htex", **options)
            ]
        )

    def _create_thread_config(self, options: Dict[str, Any]) -> parsl.Config:
        """Create a Parsl ThreadPoolExecutor configuration object

        Args:
            options: Options for the ThreadPoolExecutor

        Returns:
            ThreadPoolExecutor configuration object
        """
        return parsl.Config(
            executors=[
                parsl.executors.ThreadPoolExecutor(label="thread", **options)
            ]
        )
