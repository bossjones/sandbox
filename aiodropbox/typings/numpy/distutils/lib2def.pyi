"""
This type stub file was generated by pyright.
"""

__doc__ = ...
__version__ = ...
py_ver = ...
DEFAULT_NM = ...
DEF_HEADER = ...
FUNC_RE = ...
DATA_RE = ...
def parse_cmd(): # -> tuple[str | Unbound, str | Unbound | None]:
    """Parses the command-line arguments.

libfile, deffile = parse_cmd()"""
    ...

def getnm(nm_cmd=..., shell=...): # -> str:
    """Returns the output of nm_cmd via a pipe.

nm_output = getnm(nm_cmd = 'nm -Cs py_lib')"""
    ...

def parse_nm(nm_output): # -> tuple[list[Unknown], list[Unknown]]:
    """Returns a tuple of lists: dlist for the list of data
symbols and flist for the list of function symbols.

dlist, flist = parse_nm(nm_output)"""
    ...

def output_def(dlist, flist, header, file=...): # -> None:
    """Outputs the final DEF file to a file defaulting to stdout.

output_def(dlist, flist, header, file = sys.stdout)"""
    ...

if __name__ == '__main__':
    nm_cmd = ...
    nm_output = ...
