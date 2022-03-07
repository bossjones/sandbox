"""
This type stub file was generated by pyright.
"""

from numpy.ma import MaskedArray

""":mod:`numpy.ma..mrecords`

Defines the equivalent of :class:`numpy.recarrays` for masked arrays,
where fields can be accessed as attributes.
Note that :class:`numpy.ma.MaskedArray` already supports structured datatypes
and the masking of individual fields.

.. moduleauthor:: Pierre Gerard-Marchant

"""
_byteorderconv = ...
_check_fill_value = ...
reserved_fields = ...
class MaskedRecords(MaskedArray):
    """

    Attributes
    ----------
    _data : recarray
        Underlying data, as a record array.
    _mask : boolean array
        Mask of the records. A record is masked when all its fields are
        masked.
    _fieldmask : boolean recarray
        Record array of booleans, setting the mask of each individual field
        of each record.
    _fill_value : record
        Filling values for each field.

    """
    def __new__(cls, shape, dtype=..., buf=..., offset=..., strides=..., formats=..., names=..., titles=..., byteorder=..., aligned=..., mask=..., hard_mask=..., fill_value=..., keep_mask=..., copy=..., **options):
        ...
    
    def __array_finalize__(self, obj): # -> None:
        ...
    
    def __len__(self): # -> int:
        """
        Returns the length

        """
        ...
    
    def __getattribute__(self, attr): # -> Any:
        ...
    
    def __setattr__(self, attr, val): # -> None:
        """
        Sets the attribute attr to the value val.

        """
        ...
    
    def __getitem__(self, indx): # -> MaskedConstant:
        """
        Returns all the fields sharing the same fieldname base.

        The fieldname base is either `_data` or `_mask`.

        """
        ...
    
    def __setitem__(self, indx, value): # -> None:
        """
        Sets the given record to value.

        """
        ...
    
    def __str__(self) -> str:
        """
        Calculates the string representation.

        """
        ...
    
    def __repr__(self): # -> str:
        """
        Calculates the repr representation.

        """
        ...
    
    def view(self, dtype=..., type=...):
        """
        Returns a view of the mrecarray.

        """
        ...
    
    def harden_mask(self): # -> None:
        """
        Forces the mask to hard.

        """
        ...
    
    def soften_mask(self): # -> None:
        """
        Forces the mask to soft

        """
        ...
    
    def copy(self):
        """
        Returns a copy of the masked record.

        """
        ...
    
    def tolist(self, fill_value=...): # -> Any:
        """
        Return the data portion of the array as a list.

        Data items are converted to the nearest compatible Python type.
        Masked values are converted to fill_value. If fill_value is None,
        the corresponding entries in the output list will be ``None``.

        """
        ...
    
    def __getstate__(self): # -> tuple[Literal[1], Unknown, Unknown, Unknown, Unknown, Unknown | Any, Unknown]:
        """Return the internal state of the masked array.

        This is for pickling.

        """
        ...
    
    def __setstate__(self, state): # -> None:
        """
        Restore the internal state of the masked array.

        This is for pickling.  ``state`` is typically the output of the
        ``__getstate__`` output, and is a 5-tuple:

        - class name
        - a tuple giving the shape of the data
        - a typecode for the data
        - a binary string for the data
        - a binary string for the mask.

        """
        ...
    
    def __reduce__(self): # -> tuple[(subtype: Unknown, baseclass: Unknown, baseshape: Unknown, basetype: Unknown) -> Unknown, tuple[Type[MaskedRecords], Unknown, tuple[Literal[0]], Literal['b']], tuple[Literal[1], Unknown, Unknown, Unknown, Unknown, Unknown | Any, Unknown]]:
        """
        Return a 3-tuple for pickling a MaskedArray.

        """
        ...
    


mrecarray = MaskedRecords
def fromarrays(arraylist, dtype=..., shape=..., formats=..., names=..., titles=..., aligned=..., byteorder=..., fill_value=...): # -> Any:
    """
    Creates a mrecarray from a (flat) list of masked arrays.

    Parameters
    ----------
    arraylist : sequence
        A list of (masked) arrays. Each element of the sequence is first converted
        to a masked array if needed. If a 2D array is passed as argument, it is
        processed line by line
    dtype : {None, dtype}, optional
        Data type descriptor.
    shape : {None, integer}, optional
        Number of records. If None, shape is defined from the shape of the
        first array in the list.
    formats : {None, sequence}, optional
        Sequence of formats for each individual field. If None, the formats will
        be autodetected by inspecting the fields and selecting the highest dtype
        possible.
    names : {None, sequence}, optional
        Sequence of the names of each field.
    fill_value : {None, sequence}, optional
        Sequence of data to be used as filling values.

    Notes
    -----
    Lists of tuples should be preferred over lists of lists for faster processing.

    """
    ...

def fromrecords(reclist, dtype=..., shape=..., formats=..., names=..., titles=..., aligned=..., byteorder=..., fill_value=..., mask=...): # -> Any:
    """
    Creates a MaskedRecords from a list of records.

    Parameters
    ----------
    reclist : sequence
        A list of records. Each element of the sequence is first converted
        to a masked array if needed. If a 2D array is passed as argument, it is
        processed line by line
    dtype : {None, dtype}, optional
        Data type descriptor.
    shape : {None,int}, optional
        Number of records. If None, ``shape`` is defined from the shape of the
        first array in the list.
    formats : {None, sequence}, optional
        Sequence of formats for each individual field. If None, the formats will
        be autodetected by inspecting the fields and selecting the highest dtype
        possible.
    names : {None, sequence}, optional
        Sequence of the names of each field.
    fill_value : {None, sequence}, optional
        Sequence of data to be used as filling values.
    mask : {nomask, sequence}, optional.
        External mask to apply on the data.

    Notes
    -----
    Lists of tuples should be preferred over lists of lists for faster processing.

    """
    ...

def openfile(fname): # -> TextIOWrapper:
    """
    Opens the file handle of file `fname`.

    """
    ...

def fromtextfile(fname, delimitor=..., commentchar=..., missingchar=..., varnames=..., vartypes=...): # -> Any:
    """
    Creates a mrecarray from data stored in the file `filename`.

    Parameters
    ----------
    fname : {file name/handle}
        Handle of an opened file.
    delimitor : {None, string}, optional
        Alphanumeric character used to separate columns in the file.
        If None, any (group of) white spacestring(s) will be used.
    commentchar : {'#', string}, optional
        Alphanumeric character used to mark the start of a comment.
    missingchar : {'', string}, optional
        String indicating missing data, and used to create the masks.
    varnames : {None, sequence}, optional
        Sequence of the variable names. If None, a list will be created from
        the first non empty line of the file.
    vartypes : {None, sequence}, optional
        Sequence of the variables dtypes. If None, it will be estimated from
        the first non-commented line.


    Ultra simple: the varnames are in the header, one line"""
    ...

def addfield(mrecord, newfield, newfieldname=...):
    """Adds a new field to the masked record array

    Uses `newfield` as data and `newfieldname` as name. If `newfieldname`
    is None, the new field name is set to 'fi', where `i` is the number of
    existing fields.

    """
    ...

