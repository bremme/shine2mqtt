import logging
import sys

from loguru import logger


def _should_log_record(record):
    return "paho.mqtt" not in record["name"]


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.patch(
            lambda r: r.update(
                name=record.name,
                function=record.funcName,
                line=record.lineno,
            )
        ).log(level, record.getMessage())


class LoggerConfigurator:
    @staticmethod
    def setup(log_level: str, color: bool | None = None) -> None:
        LoggerConfigurator._clear_existing_handlers()
        LoggerConfigurator._redirect_standard_logging()
        LoggerConfigurator._configure_third_party_loggers()
        LoggerConfigurator._configure_loguru(log_level, color)

    @staticmethod
    def _clear_existing_handlers() -> None:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    @staticmethod
    def _redirect_standard_logging() -> None:
        logging.basicConfig(handlers=[_InterceptHandler()], level=logging.NOTSET)

    @staticmethod
    def _configure_third_party_loggers() -> None:
        intercepted_loggers = (
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "fastapi",
            "asyncio",
            "starlette",
        )

        for logger_name in intercepted_loggers:
            third_party_logger = logging.getLogger(logger_name)
            third_party_logger.handlers = []
            third_party_logger.propagate = True

    @staticmethod
    def _configure_loguru(log_level: str, color: bool | None) -> None:
        standard_format = "<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module: <10}</cyan> - <level>{message}</level>"
        debug_format = "<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

        log_format = debug_format if log_level == "DEBUG" else standard_format

        logger.remove()
        logger.add(
            sys.stderr,
            format=log_format,
            level=log_level,
            colorize=color,
            enqueue=True,
            filter=_should_log_record,
        )
