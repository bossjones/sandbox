#!/usr/bin/env python
# SOURCE: https://github.com/pgrabovets/srt-to-json/blob/master/srttojson.py
# USAGE: python srttojson.py filename.srt filename.json
import re
import json
import sys
from sys import argv
import random

from rich import print
from rich import inspect
import srt

from IPython.core import ultratb
from IPython.core.debugger import Tracer  # noqa

sys.excepthook = ultratb.FormattedTB(
    mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
)

def rich_inspect(data):
    inspect(data, methods=True)

with open('test.srt') as f:
    srt_data = f.read()

# len(srt_data)
# print(srt_data)

parsed_srt_data = list(srt.parse(srt_data))


# print(parsed_srt_data)
rich_inspect(parsed_srt_data)

srt_dict = {}
# counter = 1

for i in parsed_srt_data:
    srt_dict[i.index] = {}
    srt_dict[i.index]["index"] = i.index
    srt_dict[i.index]["start"] = f"{i.start}"
    srt_dict[i.index]["end"] = f"{i.start}"
    srt_dict[i.index]["content"] = f"{i.content}"


# import bpdb
# bpdb.set_trace()

print(srt_dict)

# %timeit -n 1000 list(srt.parse(srt_data))
# # 7.09 ms ± 90.7 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

# %timeit -n 1000 pysrt.SubRipFile.from_string(srt_data)
# # 9.9 ms ± 116 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

# %timeit -n 1000 pysrt.open('/dev/shm/John Wick 2.srt')
# # 15.8 ms ± 280 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)