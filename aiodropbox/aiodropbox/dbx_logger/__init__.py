#!/usr/bin/env python3

"""aiodropbox dbx_logger -- Setup loguru logging with stderr and file with click."""

import collections

try:  # python 3
    from collections import abc
except ImportError:  # python 2
    import collections as abc

import concurrent.futures
from datetime import datetime
import functools
import gc
import inspect
import logging
from logging import Logger, LogRecord
import os
from pathlib import Path
from pprint import pformat
# import slack
import sys
from time import process_time
from types import FrameType

from typing import TYPE_CHECKING, Any, Deque, Dict, Optional, Union, cast

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from aiodropbox.models.loggers import LoggerModel, LoggerPatch


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
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


# logger.level("INFO", color="<green>")
# logger.level("WARNING", color="<yellow>")
# logger.level("CRITICAL", color="<yellow>")
# logger.level("ERROR", color="<red>")
# logger.level("DEBUG", color="<blue>")


# DEFAULT_STDERR_LOG_LEVEL = "INFO"
# DEFAULT_FILE_LOG_LEVEL = "DEBUG"
# NO_LEVEL_BELOW = 30  # Don't print level for messages below this level
# SKIP_FIELDS = -7

# class CerebroLoguru:
#     """Creates decorators for use with click to control loguru logging ."""

#     @attr.s(auto_attribs=True)
#     class LogState:
#         """Click context object for verbosity, quiet, and logfile info."""

#         verbose: bool = False
#         quiet: bool = False
#         logfile: bool = True
#         profile_mem: bool = True
#         logfile_path: Path = None
#         logfile_handler_id: int = None
#         subcommand: str = None
#         user_options: attr.s = {}
#         max_mem: int = 0

#     def __init__(
#         self,
#         name,
#         version,
#         retention=None,
#         stderr_format_func=None,
#         log_dir_parent=None,
#         file_log_level=DEFAULT_FILE_LOG_LEVEL,
#         stderr_log_level=DEFAULT_STDERR_LOG_LEVEL,
#         timer_log_level="debug",
#     ):
#         """Initialize logging setup info."""
#         self._name = name
#         self._version = version
#         self._retention = retention
#         self._log_dir_parent = log_dir_parent
#         self._file_log_level = file_log_level
#         self._stderr_log_level = stderr_log_level
#         self.timer_log_level = timer_log_level.upper()
#         self.start_times = {
#             "Total": {"wall": datetime.now(), "process": process_time()}
#         }
#         self.phase = None
#         if stderr_format_func is None:

#             def format_func(msgdict):
#                 """Do level-sensitive formatting."""
#                 if msgdict["level"].no < NO_LEVEL_BELOW:
#                     return "<level>{message}</level>\n"
#                 return "<level>{level}</level>: <level>{message}</level>\n"

#             self.stderr_format_func = format_func
#         else:
#             self.stderr_format_func = stderr_format_func

#     def _verbose_option(self, user_func):
#         """Define verbose option."""

#         def callback(ctx, unused_param, value):
#             """Set verbose state."""
#             state = ctx.ensure_object(self.LogState)
#             state.verbose = value
#             return value

#         return option(
#             "-v",
#             "--verbose",
#             is_flag=True,
#             show_default=True,
#             default=False,
#             help="Log debugging info to stderr.",
#             callback=callback,
#         )(user_func)

#     def _quiet_option(self, user_func):
#         """Define quiet option."""

#         def callback(ctx, unused_param, value):
#             """Set quiet state."""
#             state = ctx.ensure_object(self.LogState)
#             state.quiet = value
#             return value

#         return option(
#             "-q",
#             "--quiet",
#             is_flag=True,
#             show_default=True,
#             default=False,
#             help="Suppress info to stderr.",
#             callback=callback,
#         )(user_func)

#     def _logfile_option(self, user_func):
#         """Define logfile option."""

#         def callback(ctx, unused_param, value):
#             """Set logfile state."""
#             state = ctx.ensure_object(self.LogState)
#             state.logfile = value
#             return value

#         return option(
#             "--logfile/--no-logfile",
#             is_flag=True,
#             show_default=True,
#             default=True,
#             help="Log to file.",
#             callback=callback,
#         )(user_func)

#     def _profile_mem_option(self, user_func):
#         """Define logfile option."""

#         def callback(ctx, unused_param, value):
#             """Set logfile state."""
#             state = ctx.ensure_object(self.LogState)
#             state.profile_mem = value
#             return value

#         return option(
#             "--profile_mem",
#             is_flag=True,
#             show_default=True,
#             default=False,
#             help="Profile peak memory use.",
#             callback=callback,
#         )(user_func)

#     def logging_options(self, user_func):
#         """Set all logging options."""
#         user_func = self._verbose_option(user_func)
#         user_func = self._quiet_option(user_func)
#         user_func = self._logfile_option(user_func)
#         user_func = self._profile_mem_option(user_func)
#         return user_func

#     def init_logger(self, log_dir_parent=None, logfile=True):
#         """Log to stderr and to logfile at different levels."""

#         def decorator(user_func):
#             @functools.wraps(user_func)
#             def wrapper(*args, **kwargs):
#                 state = cur_ctx().find_object(self.LogState)
#                 # get the verbose/quiet levels from context
#                 if state.verbose:
#                     log_level = "DEBUG"
#                 elif state.quiet:
#                     log_level = "ERROR"
#                 else:
#                     log_level = self._stderr_log_level
#                 logger.remove()  # remove existing default logger
#                 logger.add(
#                     sys.stderr, level=log_level, format=self.stderr_format_func
#                 )
#                 if logfile and state.logfile:  # start a log file
#                     # If a subcommand was used, log to a file in the
#                     # logs/ subdirectory with the subcommand in the file name.
#                     if log_dir_parent is not None:
#                         self._log_dir_parent = log_dir_parent
#                     if self._log_dir_parent is None:
#                         log_dir_path = Path(".") / "logs"
#                     else:
#                         log_dir_path = Path(self._log_dir_parent)
#                     subcommand = cur_ctx().invoked_subcommand
#                     if subcommand is None:
#                         subcommand = state.subcommand
#                     if subcommand is not None:
#                         logfile_prefix = f"{self._name}-{subcommand}"
#                     else:
#                         logfile_prefix = f"{self._name}"
#                     if log_dir_path.exists():
#                         log_numbers = [
#                             f.name[len(logfile_prefix) + 1 : -4]
#                             for f in log_dir_path.glob(
#                                 logfile_prefix + "_*.log"
#                             )
#                         ]
#                         log_number_ints = sorted(
#                             [int(n) for n in log_numbers if n.isnumeric()]
#                         )
#                         if len(log_number_ints) > 0:
#                             log_number = log_number_ints[-1] + 1
#                             if (
#                                 self._retention is not None
#                                 and len(log_number_ints) > self._retention
#                             ):
#                                 for remove in log_number_ints[
#                                     : len(log_number_ints) - self._retention
#                                 ]:
#                                     (
#                                         log_dir_path
#                                         / f"{logfile_prefix}_{remove}.log"
#                                     ).unlink()
#                         else:
#                             log_number = 0
#                     else:
#                         log_number = 0
#                     if self._retention == 0:
#                         state.logfile_path = (
#                             log_dir_path / f"{logfile_prefix}.log"
#                         )
#                     else:
#                         state.logfile_path = (
#                             log_dir_path / f"{logfile_prefix}_{log_number}.log"
#                         )
#                     state.logfile_handler_id = logger.add(
#                         str(state.logfile_path), level=self._file_log_level
#                     )
#                 logger.debug(f'Command line: "{" ".join(sys.argv)}"')
#                 logger.debug(f"{self._name} version {self._version}")
#                 logger.debug(
#                     f"Run started at {str(self.start_times['Total']['wall'])[:SKIP_FIELDS]}"
#                 )
#                 return user_func(*args, **kwargs)

#             return wrapper

#         return decorator

#     def log_elapsed_time(self, level="debug"):
#         """Log the elapsed time for (sub)command."""

#         def decorator(user_func):
#             @functools.wraps(user_func)
#             def wrapper(*args, **kwargs):
#                 returnobj = user_func(*args, **kwargs)
#                 logger.log(
#                     level.upper(), self._format_time("Total"),
#                 )
#                 return returnobj

#             return wrapper

#         return decorator

#     def log_peak_memory_use(self, level="debug"):
#         """Log the peak memory use for (sub)command."""

#         def decorator(user_func):
#             @functools.wraps(user_func)
#             def wrapper(*args, **kwargs):
#                 state = cur_ctx().find_object(self.LogState)
#                 if state.profile_mem:
#                     max_mem, returnobj = memory_usage(
#                         (user_func, args, kwargs),
#                         retval=True,
#                         include_children=True,
#                         max_usage=True,
#                         multiprocess=True,
#                         max_iterations=1,
#                     )
#                     state.max_mem = int(max_mem)
#                     logger.log(
#                         level.upper(),
#                         f"Peak total memory use = {state.max_mem} MB.",
#                     )
#                 else:
#                     returnobj = user_func(*args, **kwargs)
#                 return returnobj

#             return wrapper

#         return decorator

#     def stash_subcommand(self):
#         """Save the subcommand to the context object."""

#         def decorator(user_func):
#             @functools.wraps(user_func)
#             def wrapper(*args, **kwargs):
#                 state = cur_ctx().find_object(self.LogState)
#                 state.subcommand = cur_ctx().invoked_subcommand
#                 return user_func(*args, **kwargs)

#             return wrapper

#         return decorator

#     def get_global_options(self):
#         """Return dictionary of global options."""
#         return cur_ctx().find_object(self.LogState)

#     def get_user_global_options(self):
#         """Return dict of global user options."""
#         return cur_ctx().find_object(self.LogState).user_options

#     def user_global_options_callback(self, ctx, param, value):
#         """Put user global options in user dict."""
#         state = ctx.ensure_object(self.LogState)
#         state.user_options[param.name] = value
#         return value

#     def elapsed_time(self, phase):
#         """Log the elapsed time of a phase."""
#         old_phase = self.phase
#         if phase is None:
#             self.phase = None
#         else:
#             self.phase = phase.capitalize()
#             self.start_times[self.phase] = {
#                 "wall": datetime.now(),
#                 "process": process_time(),
#             }
#         if old_phase is None:
#             return
#         logger.log(
#             self.timer_log_level, self._format_time(old_phase),
#         )

#     def _format_time(self, phase_name):
#         """Return a formatted elapsed time string."""
#         wall = str(datetime.now() - self.start_times[phase_name]["wall"])[
#             :SKIP_FIELDS
#         ]
#         cpu = process_time() - self.start_times[phase_name]["process"]
#         return f"{phase_name} elapsed time is {wall}, {cpu:.1f} s process CPU"


# import sys

# from IPython.core import ultratb
# from IPython.core.debugger import Tracer  # noqa

# sys.excepthook = ultratb.FormattedTB(
#     mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
# )

# LOGGERS = __name__
# print(LOGGERS)

if TYPE_CHECKING:
    from better_exceptions.log import BetExcLogger
    from loguru._logger import Logger as _Logger

# Root logger
# loggers: logging.Logger
# loggers = logging.getLogger(LOGGERS)

LOGLEVEL_MAPPING = {
    50: "CRITICAL",
    40: "ERROR",
    30: "WARNING",
    20: "INFO",
    10: "DEBUG",
    0: "NOTSET",
}


class InterceptHandler(logging.Handler):
    """
    Intercept all logging calls (with standard logging) into our Loguru Sink
    See: https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
    """

    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


logging.basicConfig(handlers=[InterceptHandler()], level=0)


# """ Logging handler intercepting existing handlers to redirect them to loguru """
class LoopDetector(logging.Filter):
    """
    Log filter which looks for repeating WARNING and ERROR log lines, which can
    often indicate that a module is spinning on a error or stuck waiting for a
    condition.

    When a repeating line is found, a summary message is printed and a message
    optionally sent to Slack.
    """

    LINE_HISTORY_SIZE = 50
    LINE_REPETITION_THRESHOLD = 5

    def __init__(self) -> None:
        self._recent_lines: Deque[str] = collections.deque(
            maxlen=self.LINE_HISTORY_SIZE
        )
        self._supressed_lines: collections.Counter = collections.Counter()

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno < logging.WARNING:
            return True

        self._recent_lines.append(record.getMessage())

        counter = collections.Counter(list(self._recent_lines))
        repeated_lines = [
            line
            for line, count in counter.most_common()
            if count > self.LINE_REPETITION_THRESHOLD
            and line not in self._supressed_lines
        ]

        if repeated_lines:
            for line in repeated_lines:
                self._supressed_lines[line] = self.LINE_HISTORY_SIZE

        for line, count in self._supressed_lines.items():
            self._supressed_lines[line] = count - 1
            # mypy doesn't understand how to deal with collection.Counter's
            # unary addition operator
            self._supressed_lines = +self._supressed_lines  # type: ignore

        # https://docs.python.org/3/library/logging.html#logging.Filter.filter
        # The docs lie when they say that this returns an int, it's really a bool.
        # https://bugs.python.org/issue42011
        # H6yQOs93Cgg
        return True


def get_logger(
    name: str,
    provider: Optional[str] = None,
    level: int = logging.INFO,
    logger: logging.Logger = logger,
) -> logging.Logger:
    # if provider is not None:
    #     name = "{}#{}".format(name, provider)
    #     # fmt = "[%(levelname)s] {}: %(message)s".format(provider.upper())

    #     # colorize = True, format = "<green>{time}</green> <level>{message}</level>")

    #     fmt = "[{level}] " + provider + ": {message}"
    # else:
    #     # fmt = "[%(levelname)s] %(message)s"
    #     fmt = "[{level}] {message}"

    # logger.level("NOTSET", no=logging.INFO, color="<yellow>")

    # 50: "CRITICAL",
    # 40: "ERROR",
    # 30: "WARNING",
    # 20: "INFO",
    # 10: "DEBUG",
    # 0: "NOTSET",
    # global loggers

    # if (loggers.hasHandlers()):
    #     # remove all handlers
    #     loggers.handlers.clear()

    # loggers = loggers

    # intercept_handler = InterceptHandler()

    config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "colorize": True,
                "format": format_record,
                "level": logging.DEBUG,
                "enqueue": True,
                "diagnose": True,
            },
            # {"sink": "file.log", "serialize": True},
        ],
        # "extra": {"user": "someone"}
    }

    logger.remove()
    logger.configure(**config)
    # logger.add(InterceptHandler())

    # logger
    # logger.add(sys.stdout, format=fmt, level=LOGLEVEL_MAPPING[level])
    logger.add(
        sys.stdout,
        format=format_record,
        filter="requests.packages.urllib3.connectionpool",
        level="ERROR",
        enqueue=True,
        diagnose=True,
    )
    # logger.add(sys.stdout, format=fmt, filter=LoopDetector())

    log_file_path = Path("./audit/bot.log")
    # Automatically rotate too big file
    logger.add(f"{log_file_path}", rotation="500 MB")

    # # if loggers.get(name):
    # #     return loggers.get(name)
    # # else:
    # loggers = logging.getLogger(name)
    # # Add stdout handler
    # stdout_handler = logging.StreamHandler(sys.stdout)
    # formatter = logging.Formatter(fmt)
    # stdout_handler.setFormatter(formatter)
    # loggers.addHandler(stdout_handler)
    # intercept_handler = InterceptHandler()
    # loggers.addHandler(intercept_handler)

    # # For now, run log all the time
    # # if enable_file_logger:
    # file_handler = logging.FileHandler("tui.log")
    # file_formatter = logging.Formatter(
    #     "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    # )
    # file_handler.setFormatter(file_formatter)
    # logger.addHandler(file_handler)

    # # Set logging level
    # loggers.setLevel(level)
    # logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
    #     logging.ERROR
    # )

    # for logger_name in LOGGERS:
    #     logging_logger = logging.getLogger(logger_name)
    #     logging_logger.handlers = [InterceptHandler(level=level)]
    #     logging_logger.propagate = False
    #     logging_logger.enqueue = True
    #     logging_logger.diagnose = True

    # # Disable propagation to avoid conflict with Artifactory
    # loggers.propagate = False

    # # set to true for async or multiprocessing logging
    # loggers.enqueue = True

    # # Caution, may leak sensitive data in prod
    # loggers.diagnose = True

    # loggers.addFilter(LoopDetector())

    return logger


# SOURCE: https://github.com/joint-online-judge/fastapi-rest-framework/blob/b0e93f0c0085597fcea4bb79606b653422f16700/fastapi_rest_framework/logging.py#L43
def intercept_all_loggers(level: int = logging.DEBUG) -> None:
    logging.basicConfig(handlers=[InterceptHandler()], level=level)
    logging.getLogger("uvicorn").handlers = []


# SOURCE: https://github.com/jupiterbjy/CUIAudioPlayer/blob/dev_master/CUIAudioPlayer/LoggingConfigurator.py
def get_caller_stack_name(depth=1):
    """
    Gets the name of caller.
    :param depth: determine which scope to inspect, for nested usage.
    """
    return inspect.stack()[depth][3]


# SOURCE: https://github.com/jupiterbjy/CUIAudioPlayer/blob/dev_master/CUIAudioPlayer/LoggingConfigurator.py
def get_caller_stack_and_association(depth=1):
    stack_frame = inspect.stack()[depth][0]
    f_code_ref = stack_frame.f_code

    def get_reference_filter():
        for obj in gc.get_referrers(f_code_ref):
            try:
                if obj.__code__ is f_code_ref:  # checking identity
                    return obj
            except AttributeError:
                continue

    actual_function_ref = get_reference_filter()
    try:
        return actual_function_ref.__qualname__
    except AttributeError:
        return "<Module>"


# https://stackoverflow.com/questions/52715425


def log_caller():
    return f"<{get_caller_stack_name()}>"


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

    LOGGER = get_logger("Logger Smoke Tests", provider="Logger")
    intercept_all_loggers()

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
