"""
This type stub file was generated by pyright.
"""

"""

f2py2e - Fortran to Python C/API generator. 2nd Edition.
         See __usage__ below.

Copyright 1999--2011 Pearu Peterson all rights reserved,
Pearu Peterson <pearu@cens.ioc.ee>
Permission to use, modify, and distribute this software is given under the
terms of the NumPy License.

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
$Date: 2005/05/06 08:31:19 $
Pearu Peterson

"""
f2py_version = ...
errmess = ...
show = ...
outmess = ...
__usage__ = ...
def scaninputline(inputline): # -> tuple[list[Unknown], dict[str, str | None]]:
    ...

def callcrackfortran(files, options):
    ...

def buildmodules(lst): # -> dict[Unknown, Unknown]:
    ...

def dict_append(d_out, d_in): # -> None:
    ...

def run_main(comline_list): # -> dict[Unknown, Unknown] | None:
    """
    Equivalent to running::

        f2py <args>

    where ``<args>=string.join(<list>,' ')``, but in Python.  Unless
    ``-h`` is used, this function returns a dictionary containing
    information on generated modules and their dependencies on source
    files.  For example, the command ``f2py -m scalar scalar.f`` can be
    executed from Python as follows

    You cannot build extension modules with this function, that is,
    using ``-c`` is not allowed. Use ``compile`` command instead

    Examples
    --------
    .. include:: run_main_session.dat
        :literal:

    """
    ...

def filter_files(prefix, suffix, files, remove_prefix=...): # -> tuple[list[Unknown], list[Unknown]]:
    """
    Filter files by prefix and suffix.
    """
    ...

def get_prefix(module):
    ...

def run_compile(): # -> None:
    """
    Do it all in one call!
    """
    ...

def main(): # -> None:
    ...
