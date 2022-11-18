import logging
import os
import re
import sys
from datetime import datetime
from logging.handlers import WatchedFileHandler

import json_log_formatter
from simple_example.web_app_example.settings import LoggingConfiguration


class AppFormatter(logging.Formatter):
    @staticmethod
    def filter_sensitive_information(s: str):
        return re.sub(r":\/\/(.*?)\@", r":***:***@//", s)

    def format(self, record: logging.LogRecord):
        record = logging.Formatter.format(self, record)
        record = self.filter_sensitive_information(record)
        return record


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message: str, extra: dict, record: logging.LogRecord) -> dict:
        extra["message"] = AppFormatter.filter_sensitive_information(message)

        # Include builtins
        extra["level"] = record.levelname
        extra["name"] = record.name

        if "time" not in extra:
            extra["time"] = datetime.utcnow()

        if record.exc_info:
            extra["exc_info"] = self.formatException(record.exc_info)

        return extra


class LogLevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level
        super().__init__()

    def filter(self, record) -> bool:
        return record.levelno == self.level


def create_watched_file_handler(
    log_path: str,
    filename: str,
    level: int,
    formatter: logging.Formatter,
    apply_level_filter: bool = True,
) -> WatchedFileHandler:
    path = os.path.join(log_path, filename)
    file_handler = WatchedFileHandler(path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    if apply_level_filter:
        file_handler.addFilter(LogLevelFilter(level=level))
    return file_handler


def get_standard_logger(
    name: str, log_settings: LoggingConfiguration
) -> logging.Logger:

    # Global format Logger
    prefix_log_format = f"[{name}] %(asctime)s %(levelname)-8s [%(module)s.%(funcName)s:%(lineno)d]: "

    stream_log_format = prefix_log_format + "CONSOLE %(message)s"

    # Basic config settings
    stdout_stream_handler = logging.StreamHandler(sys.stdout)
    stdout_stream_handler.setLevel(log_settings.MIN_LOG_LEVEL)
    stdout_stream_handler.setFormatter(AppFormatter(stream_log_format))

    stderr_stream_handler = logging.StreamHandler(sys.stderr)
    stderr_stream_handler.setLevel(logging.ERROR)
    stderr_stream_handler.setFormatter(AppFormatter(stream_log_format))

    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[stdout_stream_handler, stderr_stream_handler],
        level=log_settings.MIN_LOG_LEVEL,
    )

    standard_logger = logging.getLogger(name)

    if log_settings.LOG_SQL:
        sql_logger = logging.getLogger("databases")
        sql_logger.setLevel(level=log_settings.MIN_LOG_LEVEL)
        if not log_settings.LOG_TO_FILE:
            sql_logger.addHandler(stdout_stream_handler)

    if log_settings.LOG_TO_FILE:
        file_log_format = prefix_log_format + "%(message)s"

        app_formatter = AppFormatter(file_log_format)

        if log_settings.LOG_SQL:

            sql_logger.addHandler(
                create_watched_file_handler(
                    log_path=log_settings.LOG_PATH,
                    filename="databases.log",
                    level=log_settings.MIN_LOG_LEVEL,
                    formatter=app_formatter,
                    apply_level_filter=False,
                )
            )

        if log_settings.LOG_JSON:
            json_formatter = json_log_formatter.JSONFormatter()

            standard_logger.addHandler(
                create_watched_file_handler(
                    log_path=log_settings.LOG_PATH,
                    filename=log_settings.JSON_LOG_FILE,
                    level=log_settings.MIN_LOG_LEVEL,
                    formatter=json_formatter,
                    apply_level_filter=False,
                )
            )
        if log_settings.LOG_TO_LEVEL_FILES:
            for log_level in [
                logging.CRITICAL,
                logging.FATAL,
                logging.ERROR,
                logging.WARNING,
                logging.WARN,
                logging.INFO,
                logging.DEBUG,
            ]:
                if log_level >= log_settings.MIN_LOG_LEVEL:
                    standard_logger.addHandler(
                        create_watched_file_handler(
                            log_path=log_settings.LOG_PATH,
                            filename=f"{logging.getLevelName(level=log_level)}.log",
                            level=log_level,
                            formatter=app_formatter,
                        )
                    )

    return standard_logger
