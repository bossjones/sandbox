"""
This type stub file was generated by pyright.
"""

"""

Auxiliary functions for f2py2e.

Copyright 1999,2000 Pearu Peterson all rights reserved,
Pearu Peterson <pearu@ioc.ee>
Permission to use, modify, and distribute this software is given under the
terms of the NumPy (BSD style) LICENSE.


NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
$Date: 2005/07/24 19:01:55 $
Pearu Peterson

"""
f2py_version = ...
errmess = ...
show = ...
options = ...
debugoptions = ...
wrapfuncs = ...
def outmess(t): # -> None:
    ...

def debugcapi(var): # -> bool:
    ...

def isstring(var): # -> bool:
    ...

def ischaracter(var): # -> bool:
    ...

def isstringarray(var): # -> bool:
    ...

def isarrayofstrings(var): # -> Literal[False]:
    ...

def isarray(var): # -> bool:
    ...

def isscalar(var): # -> bool:
    ...

def iscomplex(var): # -> bool:
    ...

def islogical(var): # -> Literal[False]:
    ...

def isinteger(var): # -> Literal[False]:
    ...

def isreal(var): # -> Literal[False]:
    ...

def get_kind(var): # -> None:
    ...

def islong_long(var): # -> Literal[0]:
    ...

def isunsigned_char(var): # -> Literal[0]:
    ...

def isunsigned_short(var): # -> Literal[0]:
    ...

def isunsigned(var): # -> Literal[0]:
    ...

def isunsigned_long_long(var): # -> Literal[0]:
    ...

def isdouble(var): # -> Literal[0]:
    ...

def islong_double(var): # -> Literal[0]:
    ...

def islong_complex(var): # -> Literal[0]:
    ...

def iscomplexarray(var): # -> bool:
    ...

def isint1array(var): # -> Literal[False]:
    ...

def isunsigned_chararray(var): # -> Literal[False]:
    ...

def isunsigned_shortarray(var): # -> Literal[False]:
    ...

def isunsignedarray(var): # -> Literal[False]:
    ...

def isunsigned_long_longarray(var): # -> Literal[False]:
    ...

def issigned_chararray(var): # -> Literal[False]:
    ...

def issigned_shortarray(var): # -> Literal[False]:
    ...

def issigned_array(var): # -> Literal[False]:
    ...

def issigned_long_longarray(var): # -> Literal[False]:
    ...

def isallocatable(var): # -> bool:
    ...

def ismutable(var): # -> bool:
    ...

def ismoduleroutine(rout): # -> bool:
    ...

def ismodule(rout): # -> Literal[False]:
    ...

def isfunction(rout): # -> Literal[False]:
    ...

def isfunction_wrap(rout): # -> int | bool:
    ...

def issubroutine(rout): # -> Literal[False]:
    ...

def issubroutine_wrap(rout): # -> bool | Literal[0]:
    ...

def hasassumedshape(rout): # -> bool:
    ...

def isroutine(rout): # -> Literal[False]:
    ...

def islogicalfunction(rout): # -> Literal[0, False]:
    ...

def islong_longfunction(rout): # -> Literal[0]:
    ...

def islong_doublefunction(rout): # -> Literal[0]:
    ...

def iscomplexfunction(rout): # -> bool | Literal[0]:
    ...

def iscomplexfunction_warn(rout): # -> Literal[1, 0]:
    ...

def isstringfunction(rout): # -> bool | Literal[0]:
    ...

def hasexternals(rout): # -> Literal[False]:
    ...

def isthreadsafe(rout): # -> bool:
    ...

def hasvariables(rout): # -> Literal[False]:
    ...

def isoptional(var): # -> bool:
    ...

def isexternal(var): # -> bool:
    ...

def isrequired(var): # -> bool:
    ...

def isintent_in(var): # -> Literal[1, 0]:
    ...

def isintent_inout(var): # -> bool:
    ...

def isintent_out(var): # -> bool:
    ...

def isintent_hide(var): # -> bool:
    ...

def isintent_nothide(var): # -> bool:
    ...

def isintent_c(var): # -> bool:
    ...

def isintent_cache(var): # -> bool:
    ...

def isintent_copy(var): # -> bool:
    ...

def isintent_overwrite(var): # -> bool:
    ...

def isintent_callback(var): # -> bool:
    ...

def isintent_inplace(var): # -> bool:
    ...

def isintent_aux(var): # -> bool:
    ...

def isintent_aligned4(var): # -> bool:
    ...

def isintent_aligned8(var): # -> bool:
    ...

def isintent_aligned16(var): # -> bool:
    ...

isintent_dict = ...
def isprivate(var): # -> bool:
    ...

def hasinitvalue(var): # -> bool:
    ...

def hasinitvalueasstring(var): # -> bool | Literal[0]:
    ...

def hasnote(var): # -> bool:
    ...

def hasresultnote(rout): # -> bool | Literal[0]:
    ...

def hascommon(rout): # -> bool:
    ...

def containscommon(rout): # -> Literal[1, 0]:
    ...

def containsmodule(block): # -> Literal[1, 0]:
    ...

def hasbody(rout): # -> bool:
    ...

def hascallstatement(rout): # -> bool:
    ...

def istrue(var): # -> Literal[1]:
    ...

def isfalse(var): # -> Literal[0]:
    ...

class F2PYError(Exception):
    ...


class throw_error:
    def __init__(self, mess) -> None:
        ...
    
    def __call__(self, var): # -> NoReturn:
        ...
    


def l_and(*f): # -> Any:
    ...

def l_or(*f): # -> Any:
    ...

def l_not(f): # -> Any:
    ...

def isdummyroutine(rout): # -> Literal[0]:
    ...

def getfortranname(rout):
    ...

def getmultilineblock(rout, blockname, comment=..., counter=...): # -> None:
    ...

def getcallstatement(rout): # -> None:
    ...

def getcallprotoargument(rout, cb_map=...): # -> str | None:
    ...

def getusercode(rout): # -> None:
    ...

def getusercode1(rout): # -> None:
    ...

def getpymethoddef(rout): # -> None:
    ...

def getargs(rout): # -> tuple[Unknown | list[Unknown], Unknown | list[Unknown]]:
    ...

def getargs2(rout): # -> tuple[Unknown, Unknown | list[Unknown]]:
    ...

def getrestdoc(rout): # -> None:
    ...

def gentitle(name): # -> str:
    ...

def flatlist(l): # -> list[Unknown]:
    ...

def stripcomma(s):
    ...

def replace(str, d, defaultsep=...): # -> list[Unknown]:
    ...

def dictappend(rd, ar):
    ...

def applyrules(rules, d, var=...): # -> dict[Unknown, Unknown]:
    ...

