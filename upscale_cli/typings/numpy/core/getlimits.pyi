"""
This type stub file was generated by pyright.
"""

from .overrides import set_module

"""Machine limits for Float32 and Float64 and (long double) if available...

"""
class MachArLike:
    """ Object to simulate MachAr instance """
    def __init__(self, ftype, *, eps, epsneg, huge, tiny, ibeta, **kwargs) -> None:
        ...
    


_convert_to_float = ...
_title_fmt = ...
_MACHAR_PARAMS = ...
_KNOWN_TYPES = ...
_float_ma = ...
@set_module('numpy')
class finfo:
    """
    finfo(dtype)

    Machine limits for floating point types.

    Attributes
    ----------
    bits : int
        The number of bits occupied by the type.
    eps : float
        The difference between 1.0 and the next smallest representable float
        larger than 1.0. For example, for 64-bit binary floats in the IEEE-754
        standard, ``eps = 2**-52``, approximately 2.22e-16.
    epsneg : float
        The difference between 1.0 and the next smallest representable float
        less than 1.0. For example, for 64-bit binary floats in the IEEE-754
        standard, ``epsneg = 2**-53``, approximately 1.11e-16.
    iexp : int
        The number of bits in the exponent portion of the floating point
        representation.
    machar : MachAr
        The object which calculated these parameters and holds more
        detailed information.
    machep : int
        The exponent that yields `eps`.
    max : floating point number of the appropriate type
        The largest representable number.
    maxexp : int
        The smallest positive power of the base (2) that causes overflow.
    min : floating point number of the appropriate type
        The smallest representable number, typically ``-max``.
    minexp : int
        The most negative power of the base (2) consistent with there
        being no leading 0's in the mantissa.
    negep : int
        The exponent that yields `epsneg`.
    nexp : int
        The number of bits in the exponent including its sign and bias.
    nmant : int
        The number of bits in the mantissa.
    precision : int
        The approximate number of decimal digits to which this kind of
        float is precise.
    resolution : floating point number of the appropriate type
        The approximate decimal resolution of this type, i.e.,
        ``10**-precision``.
    tiny : float
        The smallest positive usable number.  Type of `tiny` is an
        appropriate floating point type.

    Parameters
    ----------
    dtype : float, dtype, or instance
        Kind of floating point data-type about which to get information.

    See Also
    --------
    MachAr : The implementation of the tests that produce this information.
    iinfo : The equivalent for integer data types.
    spacing : The distance between a value and the nearest adjacent number
    nextafter : The next floating point value after x1 towards x2

    Notes
    -----
    For developers of NumPy: do not instantiate this at the module level.
    The initial calculation of these parameters is expensive and negatively
    impacts import times.  These objects are cached, so calling ``finfo()``
    repeatedly inside your functions is not a problem.

    """
    _finfo_cache = ...
    def __new__(cls, dtype): # -> finfo:
        ...
    
    def __str__(self) -> str:
        ...
    
    def __repr__(self): # -> str:
        ...
    


@set_module('numpy')
class iinfo:
    """
    iinfo(type)

    Machine limits for integer types.

    Attributes
    ----------
    bits : int
        The number of bits occupied by the type.
    min : int
        The smallest integer expressible by the type.
    max : int
        The largest integer expressible by the type.

    Parameters
    ----------
    int_type : integer type, dtype, or instance
        The kind of integer data type to get information about.

    See Also
    --------
    finfo : The equivalent for floating point data types.

    Examples
    --------
    With types:

    >>> ii16 = np.iinfo(np.int16)
    >>> ii16.min
    -32768
    >>> ii16.max
    32767
    >>> ii32 = np.iinfo(np.int32)
    >>> ii32.min
    -2147483648
    >>> ii32.max
    2147483647

    With instances:

    >>> ii32 = np.iinfo(np.int32(10))
    >>> ii32.min
    -2147483648
    >>> ii32.max
    2147483647

    """
    _min_vals = ...
    _max_vals = ...
    def __init__(self, int_type) -> None:
        ...
    
    @property
    def min(self): # -> int:
        """Minimum value of given dtype."""
        ...
    
    @property
    def max(self): # -> int:
        """Maximum value of given dtype."""
        ...
    
    def __str__(self) -> str:
        """String representation."""
        ...
    
    def __repr__(self): # -> str:
        ...
    


