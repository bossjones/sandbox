from __future__ import annotations

# pyright: reportMissingImports=false, reportUnusedVariable=warning, reportUntypedBaseClass=error, reportGeneralTypeIssues=false
import pathlib
from types import TracebackType

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    NewType,
    Sequence as Seq,
    Tuple,
    Type,
    TypedDict,
    Union,
    Union as U,
)

import numpy as np

# Human-readable type names.
TYPES = {
    "mp3": "MP3",
    "aac": "AAC",
    "alac": "ALAC",
    "ogg": "OGG",
    "opus": "Opus",
    "flac": "FLAC",
    "ape": "APE",
    "wv": "WavPack",
    "mpc": "Musepack",
    "asf": "Windows Media",
    "aiff": "AIFF",
    "dsf": "DSD Stream File",
}

PREFERRED_IMAGE_EXTENSIONS = {"jpeg": "jpg"}


# for type hinting
# SOURCE: https://stackoverflow.com/questions/51291722/define-a-jsonable-type-using-mypy-pep-526
# SOURCE: https://github.com/python/typing/issues/182
# currently not supported by mypy
JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

##########################################################
# alternative #2 json type hinting
##########################################################
# Values for JSON that aren't nested
JSON_v = Union[str, int, float, bool, None]

# If MyPy ever permits recursive definitions, just uncomment this:
# JSON = Union[List['JSON'], Mapping[str, 'JSON'], JSON_v]

# Until then, here's a multi-layer way to represent any (reasonable) JSON we
# might send or receive.  It terminates at JSON_4, so the maximum depth of
# the JSON is 5 dicts/lists, like: {'a': {'b': {'c': {'d': {'e': 'f'}}}}}.

JSON_5 = JSON_v
JSON_4 = Union[JSON_v, List[JSON_5], Mapping[str, JSON_5]]
JSON_3 = Union[JSON_v, List[JSON_4], Mapping[str, JSON_4]]
JSON_2 = Union[JSON_v, List[JSON_3], Mapping[str, JSON_3]]
JSON_1 = Union[JSON_v, List[JSON_2], Mapping[str, JSON_2]]
JSON = Union[JSON_v, List[JSON_1], Mapping[str, JSON_1]]

# To allow deeper nesting, you can of course expand the JSON definition above,
# or you can keep typechecking for the first levels but skip typechecking
# at the deepest levels by using UnsafeJSON:

UnsafeJSON_5 = Union[JSON_v, List[Any], Mapping[str, Any]]
UnsafeJSON_4 = Union[JSON_v, List[UnsafeJSON_5], Mapping[str, UnsafeJSON_5]]
UnsafeJSON_3 = Union[JSON_v, List[UnsafeJSON_4], Mapping[str, UnsafeJSON_4]]
UnsafeJSON_2 = Union[JSON_v, List[UnsafeJSON_3], Mapping[str, UnsafeJSON_3]]
UnsafeJSON_1 = Union[JSON_v, List[UnsafeJSON_2], Mapping[str, UnsafeJSON_2]]
UnsafeJSON = Union[JSON_v, List[UnsafeJSON_1], Mapping[str, UnsafeJSON_1]]
##########################################################

Pathlib = Union[str, pathlib.Path]  # typed from memory, may be wrong.

# This is a WOEFULLY inadequate stub for a duck-array type.
# Mostly, just a placeholder for the concept of needing an ArrayLike type.
# Ultimately, this should come from https://github.com/napari/image-types
# and should probably be replaced by a typing.Protocol
# note, numpy.typing.ArrayLike (in v1.20) is not quite what we want either,
# since it includes all valid arguments for np.array() ( int, float, str...)
# ArrayLike = Union[np.ndarray, 'dask.array.Array', 'zarr.Array']
ArrayLike = np.ndarray


# layer data may be: (data,) (data, meta), or (data, meta, layer_type)
# using "Any" for the data type until ArrayLike is more mature.
FullLayerData = Tuple[Any, Dict, str]
LayerData = Union[Tuple[Any], Tuple[Any, Dict], FullLayerData]

PathLike = Union[str, List[str]]
ReaderFunction = Callable[[PathLike], List[LayerData]]
WriterFunction = Callable[[str, List[FullLayerData]], List[str]]

ExcInfo = Union[
    Tuple[Type[BaseException], BaseException, TracebackType],
    Tuple[None, None, None],
]

# # Types for GUI HookSpecs
# # WidgetCallable = Callable[..., Union['FunctionGui', 'QWidget']]
# WidgetCallable = Callable[
#     ..., Union["Widget", "ScrollMenu", "CheckBoxMenu", "TextBox", "ScrollTextBlock"]
# ]
# AugmentedWidget = Union[WidgetCallable, Tuple[WidgetCallable, dict]]


# these types are mostly "intentionality" placeholders.  While it's still hard
# to use actual types to define what is acceptable data for a given layer,
# these types let us point to a concrete namespace to indicate "this data is
# intended to be (and is capable of) being turned into X layer type".
# while their names should not change (without deprecation), their typing
# implementations may... or may be rolled over to napari/image-types

if tuple(np.__version__.split(".")) < ("1", "20"):
    # this hack is because NewType doesn't allow `Any` as a base type
    # and numpy <=1.20 didn't provide type stubs for np.ndarray
    # https://github.com/python/mypy/issues/6701#issuecomment-609638202
    class ArrayBase(np.ndarray):
        def __getattr__(self, name: str) -> Any:
            # Super of 'ArrayBase' has no '__getattr__' member (no-member)
            return super().__getattr__(name)  # pylint: disable=E1101


else:
    ArrayBase = np.ndarray  # type: ignore

# SOURCE: https://github.com/napari/image-types/blob/master/imtypes/_types.py
# Base image type: an Image is just a NumPy array
AnyImage = NewType("AnyImage", np.ndarray)

# Single Channel image
Image = NewType("Image", AnyImage)

# 2D image types: a subtype of Image that is 2D only
Image2D = NewType("Image2D", Image)

# Multichannel images: a NumPy array in which the last dimension
# represents "channels", ie measurements of different information at the same
# coordinates
ImageCh = NewType("ImageCh", AnyImage)

# Multichannel 2D images: a subtype of ImageCh restricted to only two channels
ImageCh2D = NewType("ImageCh2D", ImageCh)

AnyImage2D = U[Image2D, ImageCh2D]


Coords = NewType("Coords", np.ndarray)


Sigma = U[float, Seq[float]]

Spacing = U[float, Seq[float]]

# NOTE: https://stackoverflow.com/questions/37031928/type-annotations-for-args-and-kwargs
# NOTE: If one wants to describe specific named arguments expected in kwargs, one can instead pass in a TypedDict(which defines required and optional parameters). Optional parameters are what were the kwargs. Note: TypedDict is in python >= 3.8 See this example:
class DataCmdRequiredProps(TypedDict):
    # all of these must be present
    name: str


class DataCmdOptionalProps(TypedDict, total=False):
    # these can be included or they can be omitted
    cmd: str
    uri: str


class ReqAndOptional(DataCmdRequiredProps, DataCmdOptionalProps):
    pass
