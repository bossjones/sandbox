"""
This type stub file was generated by pyright.
"""

def get_fcompiler_ilp64_flags(): # -> dict[str, list[str]]:
    """
    Dictionary of compiler flags for switching to 8-byte default integer
    size.
    """
    ...

def get_fcompiler_macro_include_flags(path): # -> dict[str, list[str | Unknown]]:
    """
    Dictionary of compiler flags for cpp-style preprocessing, with
    an #include search path, and safety options necessary for macro
    expansion.
    """
    ...

def uses_mkl(info): # -> bool:
    ...

def needs_g77_abi_wrapper(info): # -> bool:
    """Returns True if g77 ABI wrapper must be used."""
    ...

def get_g77_abi_wrappers(info): # -> list[Unknown]:
    """
    Returns file names of source files containing Fortran ABI wrapper
    routines.
    """
    ...

def gfortran_legacy_flag_hook(cmd, ext): # -> None:
    """
    Pre-build hook to add dd gfortran legacy flag -fallow-argument-mismatch
    """
    ...

def get_f2py_int64_options(): # -> list[str]:
    ...

def ilp64_pre_build_hook(cmd, ext): # -> None:
    """
    Pre-build hook for adding Fortran compiler flags that change
    default integer size to 64-bit.
    """
    ...

def blas_ilp64_pre_build_hook(blas_info): # -> (cmd: Unknown, ext: Unknown) -> None:
    """
    Pre-build hook for adding ILP64 BLAS compilation flags, and
    mangling Fortran source files to rename BLAS/LAPACK symbols when
    there are symbol suffixes.

    Examples
    --------
    ::

        from scipy._build_utils import blas_ilp64_pre_build_hook
        ext = config.add_extension(...)
        ext._pre_build_hook = blas_ilp64_pre_build_hook(blas_info)

    """
    ...

def generic_pre_build_hook(cmd, ext, fcompiler_flags, patch_source_func=..., source_fnpart=...): # -> None:
    """
    Pre-build hook for adding compiler flags and patching sources.

    Parameters
    ----------
    cmd : distutils.core.Command
        Hook input. Current distutils command (build_clib or build_ext).
    ext : dict or numpy.distutils.extension.Extension
        Hook input. Configuration information for library (dict, build_clib)
        or extension (numpy.distutils.extension.Extension, build_ext).
    fcompiler_flags : dict
        Dictionary of ``{'compiler_name': ['-flag1', ...]}`` containing
        compiler flags to set.
    patch_source_func : callable, optional
        Function patching sources, see `_generic_patch_sources` below.
    source_fnpart : str, optional
        String to append to the modified file basename before extension.

    """
    ...

def write_file_content(filename, content): # -> None:
    """
    Write content to file, but only if it differs from the current one.
    """
    ...

def get_blas_lapack_symbols(): # -> Any | tuple[Unknown, ...]:
    ...

