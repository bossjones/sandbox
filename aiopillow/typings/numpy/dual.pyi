"""
This type stub file was generated by pyright.
"""

"""
Aliases for functions which may be accelerated by Scipy.

Scipy_ can be built to use accelerated or otherwise improved libraries
for FFTs, linear algebra, and special functions. This module allows
developers to transparently support these accelerated functions when
scipy is available but still support users who have only installed
NumPy.

.. _Scipy : https://www.scipy.org

"""
fft = ...
ifft = ...
fftn = ...
ifftn = ...
fft2 = ...
ifft2 = ...
norm = ...
inv = ...
svd = ...
solve = ...
det = ...
eig = ...
eigvals = ...
eigh = ...
eigvalsh = ...
lstsq = ...
pinv = ...
cholesky = ...
_restore_dict = ...
def register_func(name, func): # -> None:
    ...

def restore_func(name): # -> None:
    ...

def restore_all(): # -> None:
    ...

