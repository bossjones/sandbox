# SOURCE: https://blog.bartab.fr/fastapi-logging-on-the-fly/
from __future__ import annotations

from typing import Any, List, Optional

# pylint: disable=no-name-in-module
from pydantic import BaseModel


class LoggerPatch(BaseModel):
    name: str
    level: str


# ListLoggerModel = ForwardRef("List[LoggerModel]")


class LoggerModel(BaseModel):
    name: str
    level: Optional[int]
    # children: Optional[List["LoggerModel"]] = None
    # fixes: https://github.com/samuelcolvin/pydantic/issues/545
    children: Optional[List[Any]] = None
    # children: ListLoggerModel = None


LoggerModel.update_forward_refs()
