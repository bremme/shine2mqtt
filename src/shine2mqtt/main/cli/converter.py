from argparse import Namespace

from shine2mqtt import util
from shine2mqtt.main.config.config import NESTED_DELIMITER


class CliArgDictConverter:
    @staticmethod
    def convert(args: Namespace) -> dict[str, str | int | bool | None]:
        cli_args_dict = util.remove_none_values(vars(args))
        return util.convert_to_nested_dict(cli_args_dict, delimiter=NESTED_DELIMITER)
