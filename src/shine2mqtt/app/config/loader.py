import os
from argparse import Namespace
from pathlib import Path

import yaml

from shine2mqtt import PROJECT_ROOT, util
from shine2mqtt.app.config.config import (
    ENV_PREFIX,
    NESTED_DELIMITER,
    ApplicationConfig,
)

DEFAULT_CONFIG_FILE = PROJECT_ROOT / "config.yaml"


class ConfigLoader:
    def load(self, cli_args: Namespace) -> ApplicationConfig:
        file_path = self._get_config_file(cli_args.config_file)
        file_config = self._load_config_file(file_path)

        cli_args_dict = util.remove_none_values(vars(cli_args))
        cli_config = self._convert_cli_args_to_nested_dict(cli_args_dict)

        merged_config = util.merge_dict(base=file_config, override=cli_config)

        return ApplicationConfig(**merged_config)

    def _get_config_file(self, file_path: Path | None) -> Path | None:
        if file_path:
            return file_path

        env_config_file = os.environ.get(f"{ENV_PREFIX}CONFIG_FILE")

        if env_config_file:
            return Path(env_config_file)

        if DEFAULT_CONFIG_FILE.is_file():
            return DEFAULT_CONFIG_FILE

        return None

    def _load_config_file(self, path: Path | None) -> dict:
        if path is None:
            return {}

        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Could not open config file {path}: {e}") from e

    def _convert_cli_args_to_nested_dict(self, cli_args: dict) -> dict:
        return util.convert_to_nested_dict(cli_args, delimiter=NESTED_DELIMITER)
