import os
from pathlib import Path
from typing import Any

import yaml

from shine2mqtt import PROJECT_ROOT
from shine2mqtt.app.config.config import (
    ENV_PREFIX,
)

DEFAULT_CONFIG_FILE = PROJECT_ROOT / "config.yaml"


class ConfigFileLoader:
    def __init__(self, environ: dict[str, str], default_path: Path):
        self.environ = environ
        self.default_path = default_path

        self._alternative_paths = [
            self.environ.get(f"{ENV_PREFIX}CONFIG_FILE", None),
            self.default_path if self.default_path.is_file() else None,
        ]

    @staticmethod
    def create() -> ConfigFileLoader:
        return ConfigFileLoader(dict(os.environ), DEFAULT_CONFIG_FILE)

    def load(self, path: Path | None = None) -> dict[str, Any]:
        file_path = self._resolve_path(path)
        return self._load_file(file_path)

    def _resolve_path(self, path: Path | None) -> Path | None:
        if path:
            return path

        for alternative_path in self._alternative_paths:
            if not alternative_path:
                continue
            return Path(alternative_path)

        return None

    def _load_file(self, path: Path | None) -> dict:
        if path is None:
            return {}

        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Could not open config file {path}: {e}") from e
