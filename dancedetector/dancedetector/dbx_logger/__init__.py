#!/usr/bin/env python3
"""dancedetector dbx_logger -- Setup loguru logging with stderr and file with click."""

from datetime import datetime
import functools
import gc
import inspect
import logging
from logging import Logger, LogRecord
import os
from pathlib import Path
from pprint import pformat

import sys
from time import process_time
from types import FrameType

from typing import TYPE_CHECKING, Any, Deque, Dict, Optional, Union, cast

import loguru
from loguru import logger
from loguru._defaults import LOGURU_FORMAT
from sys import stdout
from datetime import datetime, timezone
from dancedetector.models.loggers import LoggerModel, LoggerPatch

# References
# Solution comes from:
#   https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
#   https://github.com/pahntanapat/Unified-FastAPI-Gunicorn-Log
#   https://github.com/Delgan/loguru/issues/365
#   https://loguru.readthedocs.io/en/stable/api/logger.html#sink

def set_log_extras(record):
    """set_log_extras [summary].

    [extended_summary]

    Args:
        record ([type]): [description]
    """
    record["extra"]["datetime"] = datetime.now(
        timezone.utc
    )  # Log datetime in UTC time zone, even if server is using another timezone

# SOURCE: https://github.com/joint-online-judge/fastapi-rest-framework/blob/b0e93f0c0085597fcea4bb79606b653422f16700/fastapi_rest_framework/logging.py#L43
def format_record(record: Dict[str, Any]) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True},
    >>>     {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """

    format_string = LOGURU_FORMAT
    # format_string += "<green>{extra[datetime]}</green> | "
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


if TYPE_CHECKING:
    from better_exceptions.log import BetExcLogger
    from loguru._logger import Logger as _Logger

LOGLEVEL_MAPPING = {
    50: "CRITICAL",
    40: "ERROR",
    30: "WARNING",
    20: "INFO",
    10: "DEBUG",
    0: "NOTSET",
}

# #
# # Set Gunicorn loggin handler to NullHandler, this allow
# # Loguru to capture the logs emitted by Gunicorn
# #
# class StubbedGunicornLogger(Logger):
#     """StubbedGunicornLogger [summary].

#     [extended_summary]

#     Args:
#         Logger ([type]): [description]
#     """

#     def setup(self, cfg):
#         """Make the setup of Gunicorn Logger.

#         [extended_summary]

#         Args:
#             cfg ([type]): [description]
#         """
#         self.loglevel = self.LOG_LEVELS.get(cfg.loglevel.lower(), logging.INFO)

#         handler = logging.NullHandler()

#         self.error_logger = logging.getLogger("gunicorn.error")
#         self.error_logger.addHandler(handler)

#         self.access_logger = logging.getLogger("gunicorn.access")
#         self.access_logger.addHandler(handler)

#         self.error_logger.setLevel(self.loglevel)
#         self.access_logger.setLevel(self.loglevel)


class InterceptHandler(logging.Handler):
    """
    Intercept all logging calls (with standard logging) into our Loguru Sink
    See: https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
    """

    loglevel_mapping = {
        logging.CRITICAL: "CRITICAL",
        logging.ERROR: "ERROR",
        logging.FATAL: "FATAL",
        logging.WARNING: "WARNING",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG",
        1: "DUMMY",
        0: "NOTSET",
    }

    # from logging import DEBUG
    # from logging import ERROR
    # from logging import FATAL
    # from logging import INFO
    # from logging import WARN
    # https://issueexplorer.com/issue/tiangolo/fastapi/4026
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            # DISABLED 12/10/2021 # level = str(record.levelno)
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = frame.f_back
            # DISABLED 12/10/2021 # frame = cast(FrameType, frame.f_back)
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


# logging.basicConfig(handlers=[InterceptHandler()], level=0)


# # """ Logging handler intercepting existing handlers to redirect them to loguru """
# class LoopDetector(logging.Filter):
#     """
#     Log filter which looks for repeating WARNING and ERROR log lines, which can
#     often indicate that a module is spinning on a error or stuck waiting for a
#     condition.

#     When a repeating line is found, a summary message is printed and a message
#     optionally sent to Slack.
#     """

#     LINE_HISTORY_SIZE = 50
#     LINE_REPETITION_THRESHOLD = 5

#     def __init__(self) -> None:
#         self._recent_lines: Deque[str] = collections.deque(
#             maxlen=self.LINE_HISTORY_SIZE
#         )
#         self._supressed_lines: collections.Counter = collections.Counter()

#     def filter(self, record: logging.LogRecord) -> bool:
#         if record.levelno < logging.WARNING:
#             return True

#         self._recent_lines.append(record.getMessage())

#         counter = collections.Counter(list(self._recent_lines))
#         repeated_lines = [
#             line
#             for line, count in counter.most_common()
#             if count > self.LINE_REPETITION_THRESHOLD
#             and line not in self._supressed_lines
#         ]

#         if repeated_lines:
#             for line in repeated_lines:
#                 self._supressed_lines[line] = self.LINE_HISTORY_SIZE

#         for line, count in self._supressed_lines.items():
#             self._supressed_lines[line] = count - 1
#             # mypy doesn't understand how to deal with collection.Counter's
#             # unary addition operator
#             self._supressed_lines = +self._supressed_lines  # type: ignore

#         # https://docs.python.org/3/library/logging.html#logging.Filter.filter
#         # The docs lie when they say that this returns an int, it's really a bool.
#         # https://bugs.python.org/issue42011
#         # H6yQOs93Cgg
#         return True


def get_logger(
    name: str,
    provider: Optional[str] = None,
    level: int = logging.INFO,
    logger: logging.Logger = logger,
) -> logging.Logger:


#     config = {
#         "handlers": [
#             {
#                 "sink": sys.stdout,
#                 "colorize": True,
#                 "format": format_record,
#                 "level": logging.DEBUG,
#                 "enqueue": True,
#                 "diagnose": True,
#             },
#             # {"sink": "file.log", "serialize": True},
#         ],
#         # "extra": {"user": "someone"}
#     }

#     logger.remove()
#     logger.configure(**config)

#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="requests.packages.urllib3.connectionpool",
#         level="ERROR",
#         enqueue=True,
#         diagnose=True,
#     )

#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="handler",
#         level="ERROR",
#         enqueue=True,
#         diagnose=True,
#     )
#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="asyncio",
#         level="ERROR",
#         enqueue=True,
#         diagnose=True,
#     )
#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="selenium",
#         level="ERROR",
#         enqueue=True,
#         diagnose=True,
#     )
#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="webdriver_manager",
#         level="ERROR",
#         enqueue=True,
#         diagnose=True,
#     )
#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="arsenic",
#         level="DEBUG",
#         enqueue=True,
#         diagnose=True,
#     )
#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="aiohttp",
#         level="DEBUG",
#         enqueue=True,
#         diagnose=True,
#     )
#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="tensorflow",
#         level="DEBUG",
#         enqueue=True,
#         diagnose=True,
#     )
#     logger.add(
#         sys.stdout,
#         format=format_record,
#         filter="keras",
#         level="ERROR",
#         enqueue=True,
#         diagnose=True,
#     )


#     logging.basicConfig(handlers=[InterceptHandler()], level=0)

    return logger


# # SOURCE: https://github.com/joint-online-judge/fastapi-rest-framework/blob/b0e93f0c0085597fcea4bb79606b653422f16700/fastapi_rest_framework/logging.py#L43
# def intercept_all_loggers(level: int = logging.DEBUG) -> None:
#     logging.basicConfig(handlers=[InterceptHandler()], level=level)
#     logging.getLogger("uvicorn").handlers = []


# # SOURCE: https://github.com/jupiterbjy/CUIAudioPlayer/blob/dev_master/CUIAudioPlayer/LoggingConfigurator.py
# def get_caller_stack_name(depth=1):
#     """
#     Gets the name of caller.
#     :param depth: determine which scope to inspect, for nested usage.
#     """
#     return inspect.stack()[depth][3]


# # SOURCE: https://github.com/jupiterbjy/CUIAudioPlayer/blob/dev_master/CUIAudioPlayer/LoggingConfigurator.py
# def get_caller_stack_and_association(depth=1):
#     stack_frame = inspect.stack()[depth][0]
#     f_code_ref = stack_frame.f_code

#     def get_reference_filter():
#         for obj in gc.get_referrers(f_code_ref):
#             try:
#                 if obj.__code__ is f_code_ref:  # checking identity
#                     return obj
#             except AttributeError:
#                 continue

#     actual_function_ref = get_reference_filter()
#     try:
#         return actual_function_ref.__qualname__
#     except AttributeError:
#         return "<Module>"


# # https://stackoverflow.com/questions/52715425


# def log_caller():
#     return f"<{get_caller_stack_name()}>"


# FIXME: https://github.com/abnerjacobsen/fastapi-mvc-loguru-demo/blob/main/mvc_demo/core/loguru_logs.py
# SOURCE: https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger
def global_log_config(
    log_level: Union[str, int] = logging.DEBUG, json: bool = False
):
    """global_log_config [summary].

    [extended_summary]

    Args:
        log_level (Union[str, int], optional): [description].
            Defaults to logging.DEBUG.
        json (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    if isinstance(log_level, str) and (log_level in logging._nameToLevel):
        log_level = logging.DEBUG

    intercept_handler = InterceptHandler()
    # logging.basicConfig(handlers=[intercept_handler], level=LOG_LEVEL)
    # logging.root.handlers = [intercept_handler]
    logging.root.setLevel(log_level)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        # "requests.packages.urllib3.connectionpool",
        # "handler",
        "asyncio",
        # "selenium",
        # "webdriver_manager",
        # "arsenic",
        # "aiohttp",
        # "tensorflow",
        # "keras",
        # "gunicorn",
        # "gunicorn.access",
        # "gunicorn.error",
        # "uvicorn",
        # "uvicorn.access",
        # "uvicorn.error",
        # "uvicorn.config",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]


    logger.configure(
        handlers=[
            {
                # sink (file-like object, str, pathlib.Path, callable, coroutine function or logging.Handler) - An object in charge of receiving formatted logging messages and propagating them to an appropriate endpoint.
                "sink": stdout,
                # serialize (bool, optional) - Whether the logged message and its records should be first converted to a JSON string before being sent to the sink.
                "serialize": False,
                # format (str or callable, optional) - The template used to format logged messages before being sent to the sink. If a callable is passed, it should take a logging.Record as its first argument and return a string.
                "format": format_record,
                # diagnose (bool, optional) - Whether the exception trace should display the variables values to eases the debugging. This should be set to False in production to avoid leaking sensitive
                "diagnose": True,
                # backtrace (bool, optional) - Whether the exception trace formatted should be extended upward, beyond the catching point, to show the full stacktrace which generated the error.
                "backtrace": True,
                # enqueue (bool, optional) - Whether the messages to be logged should first pass through a multiprocessing-safe queue before reaching the sink. This is useful while logging to a file through multiple processes. This also has the advantage of making logging calls non-blocking.
                "enqueue": True,
                # catch (bool, optional) - Whether errors occurring while sink handles logs messages should be automatically caught. If True, an exception message is displayed on sys.stderr but the exception is not propagated to the caller, preventing your app to crash.
                "catch": True
            }
        ]
    )
    # logger.configure(patcher=set_log_extras)

    return logger



def get_lm_from_tree(loggertree: LoggerModel, find_me: str) -> LoggerModel:
    if find_me == loggertree.name:
        LOGGER.debug("Found")
        return loggertree
    else:
        for ch in loggertree.children:
            LOGGER.debug(f"Looking in: {ch.name}")
            i = get_lm_from_tree(ch, find_me)
            if i:
                return i


def generate_tree() -> LoggerModel:
    # pylint: disable=no-member
    # adapted from logging_tree package https://github.com/brandon-rhodes/logging_tree
    rootm = LoggerModel(
        name="root", level=logging.getLogger().getEffectiveLevel(), children=[]
    )
    nodesm = {}
    items = list(logging.root.manager.loggerDict.items())  # type: ignore
    items.sort()
    for name, loggeritem in items:
        if isinstance(loggeritem, logging.PlaceHolder):
            nodesm[name] = nodem = LoggerModel(name=name, children=[])
        else:
            nodesm[name] = nodem = LoggerModel(
                name=name, level=loggeritem.getEffectiveLevel(), children=[]
            )
        i = name.rfind(".", 0, len(name) - 1)  # same formula used in `logging`
        if i == -1:
            parentm = rootm
        else:
            parentm = nodesm[name[:i]]
        parentm.children.append(nodem)
    return rootm


# SMOKE-TESTS
if __name__ == "__main__":
    from logging_tree import printout
    # import logging
    # from loguru import logger
    # from dancedetector.dbx_logger import (
    #     global_log_config
    # )

    global_log_config(
        log_level=logging.getLevelName("DEBUG"),
        json=False,
    )
    LOGGER = logger

    # LOGGER = get_logger("Logger Smoke Tests", provider="Logger")
    # intercept_all_loggers()

    def dump_logger_tree():
        rootm = generate_tree()
        LOGGER.debug(rootm)

    def dump_logger(logger_name: str):
        LOGGER.debug(f"getting logger {logger_name}")
        rootm = generate_tree()
        lm = get_lm_from_tree(rootm, logger_name)
        return lm

    LOGGER.info("TESTING TESTING 1-2-3")
    printout()

    # <--""
    #    Level NOTSET so inherits level NOTSET
    #    Handler <InterceptHandler (NOTSET)>
    #      Formatter fmt='%(levelname)s:%(name)s:%(message)s' datefmt=None
    #    |
    #    o<--"asyncio"
    #    |   Level NOTSET so inherits level NOTSET
    #    |
    #    o<--[concurrent]
    #        |
    #        o<--"concurrent.futures"
    #            Level NOTSET so inherits level NOTSET
    # [INFO] Logger: TESTING TESTING 1-2-3
