"""
This type stub file was generated by pyright.
"""

from numpy.core.overrides import set_module

"""
Various richly-typed exceptions, that also help us deal with string formatting
in python where it's easier.

By putting the formatting in `__str__`, we also avoid paying the cost for
users who silence the exceptions.
"""
class UFuncTypeError(TypeError):
    """ Base class for all ufunc exceptions """
    def __init__(self, ufunc) -> None:
        ...
    


@_display_as_base
class _UFuncBinaryResolutionError(UFuncTypeError):
    """ Thrown when a binary resolution fails """
    def __init__(self, ufunc, dtypes) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


@_display_as_base
class _UFuncNoLoopError(UFuncTypeError):
    """ Thrown when a ufunc loop cannot be found """
    def __init__(self, ufunc, dtypes) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


@_display_as_base
class _UFuncCastingError(UFuncTypeError):
    def __init__(self, ufunc, casting, from_, to) -> None:
        ...
    


@_display_as_base
class _UFuncInputCastingError(_UFuncCastingError):
    """ Thrown when a ufunc input cannot be casted """
    def __init__(self, ufunc, casting, from_, to, i) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


@_display_as_base
class _UFuncOutputCastingError(_UFuncCastingError):
    """ Thrown when a ufunc output cannot be casted """
    def __init__(self, ufunc, casting, from_, to, i) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


@set_module('numpy')
class TooHardError(RuntimeError):
    ...


@set_module('numpy')
class AxisError(ValueError, IndexError):
    """ Axis supplied was invalid. """
    def __init__(self, axis, ndim=..., msg_prefix=...) -> None:
        ...
    


@_display_as_base
class _ArrayMemoryError(MemoryError):
    """ Thrown when an array cannot be allocated"""
    def __init__(self, shape, dtype) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


