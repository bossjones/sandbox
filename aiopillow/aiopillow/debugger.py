"""Debugging module. Import these functions in pdb or jupyter notebooks to figure step through code execution."""
import logging

import rich
from rich import print

from aiopillow.dbx_logger import get_logger  # noqa: E402

LOGGER = get_logger(__name__, provider="Debugger", level=logging.DEBUG)


def init_debugger():
    import sys

    from IPython.core import ultratb
    from IPython.core.debugger import Tracer  # noqa

    sys.excepthook = ultratb.FormattedTB(
        mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
    )


# source: http://blender.stackexchange.com/questions/1879/is-it-possible-to-dump-an-objects-properties-and-methods
def debug_dump(obj):
    for attr in dir(obj):
        if hasattr(obj, attr):
            print("obj.%s = %s" % (attr, getattr(obj, attr)))


def debug_dump_exclude(obj, exclude=["__builtins__", "__doc__"]):
    for attr in dir(obj):
        if hasattr(obj, attr):
            if attr not in exclude:
                print("obj.%s = %s" % (attr, getattr(obj, attr)))


def rich_inspect(obj) -> None:
    rich.inspect(obj, methods=True)


# NOTE: What is a lexer - A lexer is a software program that performs lexical analysis. Lexical analysis is the process of separating a stream of characters into different words, which in computer science we call 'tokens' . When you read my answer you are performing the lexical operation of breaking the string of text at the space characters into multiple words.
def dump_color(obj):
    # source: https://gist.github.com/EdwardBetts/0814484fdf7bbf808f6f
    from pygments import highlight
    from pygments.formatters.terminal256 import (  # pylint: disable=no-name-in-module
        Terminal256Formatter,
    )
    # Module name actually exists, but pygments loads things in a strange manner
    from pygments.lexers import Python3Lexer  # pylint: disable=no-name-in-module

    for attr in dir(obj):
        if hasattr(obj, attr):
            obj_data = "obj.%s = %s" % (attr, getattr(obj, attr))
            print(highlight(obj_data, Python3Lexer(), Terminal256Formatter()))


# SOURCE: https://github.com/j0nnib0y/gtao_python_wrapper/blob/9cdae5ce40f9a41775e29754b51325652584cf25/debug.py
def dump_magic(obj, magic=False):
    """Dumps every attribute of an object to the console.
    Args:
        obj (any object): object you want to dump
        magic (bool, optional): True if you want to output "magic" attributes (like __init__, ...)
    """
    for attr in dir(obj):
        if magic is True:
            print("obj.%s = %s" % (attr, getattr(obj, attr)))
        else:
            if not attr.startswith("__"):
                print("obj.%s = %s" % (attr, getattr(obj, attr)))


def get_pprint():
    import pprint

    # global pretty print for debugging
    pp = pprint.PrettyPrinter(indent=4)
    return pp


def pprint_color(obj):
    # source: https://gist.github.com/EdwardBetts/0814484fdf7bbf808f6f
    from pprint import pformat

    from pygments import highlight
    from pygments.formatters.terminal256 import (  # pylint: disable=no-name-in-module
        Terminal256Formatter,
    )
    # Module name actually exists, but pygments loads things in a strange manner
    from pygments.lexers import PythonLexer  # pylint: disable=no-name-in-module

    print(highlight(pformat(obj), PythonLexer(), Terminal256Formatter()))


# SOURCE: https://stackoverflow.com/questions/192109/is-there-a-built-in-function-to-print-all-the-current-properties-and-values-of-a
def dump_dir(obj):
    """Without arguments, return the list of names in the current local scope. With an argument, attempt to return a list of valid attributes for that object."""
    pp = get_pprint()
    l = dir(obj)
    print("dump_dir for object: {}".format(obj))
    pp.pprint(l)
    return l


def dump_dict(obj):
    pp = get_pprint()
    d = obj.__dict__
    print("dump_dict for object: {}".format(obj))
    pp.pprint(d)
    return d


def dump_vars(obj):
    pp = get_pprint()
    print("dump_vars for object: {}".format(obj))
    v = vars(obj)
    pp.pprint(v)
    return v


def dump_all(obj):
    print("[run]--------------[dir(obj)]--------------")
    dump_dir(obj)
    print("[run]--------------[obj.__dict__]--------------")
    dump_dict(obj)
    print("[run]--------------[pp.pprint(vars(obj))]--------------")
    dump_vars(obj)


# TODO: Change this to use a Gauge
# def enable(statsd_client: 'statsd.StatsClient', interval: float = 0.25, loop: asyncio.AbstractEventLoop = None) -> None:
# 	'''
# 	Start logging event loop lags to StatsD. In ideal circumstances they should be very close to zero.
# 	Lags may increase if event loop callbacks block for too long.
# 	'''
# 	if loop is None:
# 		loop = asyncio.get_event_loop()

# 	async def monitor():
# 		while loop.is_running():
# 			t0 = loop.time()
# 			await asyncio.sleep(interval)
# 			lag = loop.time() - t0 - interval # Should be close to zero.
# 			statsd_client.timing('aiodebug.monitor_loop_lag', lag * 1000)

# 	loop.create_task(monitor())
