from __future__ import annotations

# pylint: disable=no-value-for-parameter

from dataclasses import dataclass

from typing import Dict, Optional

from pydantic import validate_arguments

# from aiopillow import constants
from aiopillow.factories import SerializerFactory


# SOURCE: https://stackoverflow.com/questions/54863458/force-type-conversion-in-python-dataclass-init-method
@validate_arguments
@dataclass
class CmdSerializer(SerializerFactory):
    name: str
    cmd: Optional[str]
    uri: Optional[str]

    @staticmethod
    def create(d: Dict) -> CmdSerializer:
        return CmdSerializer(name=d["name"])


# SOURCE: https://stackoverflow.com/questions/54863458/force-type-conversion-in-python-dataclass-init-method

# @validate_arguments
# @dataclass
# class Guild(SerializerFactory):
#     id: str
#     cmd: Optional[str]
#     uri: Optional[str]

#     @staticmethod
#     def create(d: Dict) -> CmdSerializer:
#         return CmdSerializer(name=d["name"])

# smoke tests
if __name__ == "__main__":

    cmd_args = ["dummycmd"]

    cmd_kargs = {
        "cmd": f"youtube-dl -v -f best -n --ignore-errors --restrict-filenames --write-thumbnail --no-mtime --embed-thumbnail --recode-video mp4 --cookies=~/Downloads/yt-cookies.txt ",
        "uri": "https://www.youtube.com/watch?v=j-AY9aVIH9I",
    }

    test_cmd_metadata = CmdSerializer(*cmd_args, **cmd_kargs)

    print(test_cmd_metadata)
    print((test_cmd_metadata.name))
    print((test_cmd_metadata.cmd))
    print((test_cmd_metadata.uri))
