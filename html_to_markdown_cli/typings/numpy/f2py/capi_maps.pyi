"""
This type stub file was generated by pyright.
"""

from . import __version__
from .auxfuncs import *

"""

Copyright 1999,2000 Pearu Peterson all rights reserved,
Pearu Peterson <pearu@ioc.ee>
Permission to use, modify, and distribute this software is given under the
terms of the NumPy License.

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
$Date: 2005/05/06 10:57:33 $
Pearu Peterson

"""
__version__ = ...
f2py_version = ...
using_newcore = ...
depargs = ...
lcb_map = ...
lcb2_map = ...
c2py_map = ...
c2capi_map = ...
if using_newcore:
    c2capi_map = ...
c2pycode_map = ...
if using_newcore:
    c2pycode_map = ...
c2buildvalue_map = ...
if using_newcore:
    ...
f2cmap_all = ...
f2cmap_default = ...
def load_f2cmap_file(f2cmap_file): # -> None:
    ...

cformat_map = ...
def getctype(var): # -> str:
    """
    Determines C type
    """
    ...

def getstrlength(var): # -> Literal['-1', '1']:
    ...

def getarrdims(a, var, verbose=...): # -> dict[Unknown, Unknown]:
    ...

def getpydocsign(a, var): # -> tuple[Literal[''], Literal['']] | tuple[str | Unknown, str | Unknown]:
    ...

def getarrdocsign(a, var): # -> str:
    ...

def getinit(a, var): # -> tuple[str | Unknown, Unknown | str]:
    ...

def sign2map(a, var): # -> dict[str, Unknown | str]:
    """
    varname,ctype,atype
    init,init.r,init.i,pytype
    vardebuginfo,vardebugshowvalue,varshowvalue
    varrfromat
    intent
    """
    ...

def routsign2map(rout): # -> dict[str, Unknown | str]:
    """
    name,NAME,begintitle,endtitle
    rname,ctype,rformat
    routdebugshowvalue
    """
    ...

def modsign2map(m): # -> dict[str, Unknown]:
    """
    modulename
    """
    ...

def cb_sign2map(a, var, index=...): # -> dict[str, Unknown]:
    ...

def cb_routsign2map(rout, um): # -> dict[str, str]:
    """
    name,begintitle,endtitle,argname
    ctype,rctype,maxnofargs,nofoptargs,returncptr
    """
    ...

def common_sign2map(a, var): # -> dict[str, Unknown | str]:
    ...
