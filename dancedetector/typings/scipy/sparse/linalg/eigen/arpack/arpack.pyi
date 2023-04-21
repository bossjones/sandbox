"""
This type stub file was generated by pyright.
"""

from . import _arpack
from scipy.sparse.linalg.interface import LinearOperator

"""
Find a few eigenvectors and eigenvalues of a matrix.


Uses ARPACK: http://www.caam.rice.edu/software/ARPACK/

"""
__docformat__ = ...
arpack_int = _arpack.timing.nbx.dtype
_type_conv = ...
_ndigits = ...
DNAUPD_ERRORS = ...
SNAUPD_ERRORS = ...
ZNAUPD_ERRORS = ...
CNAUPD_ERRORS = ...
DSAUPD_ERRORS = ...
SSAUPD_ERRORS = ...
DNEUPD_ERRORS = ...
SNEUPD_ERRORS = ...
ZNEUPD_ERRORS = ...
CNEUPD_ERRORS = ...
DSEUPD_ERRORS = ...
SSEUPD_ERRORS = ...
_SAUPD_ERRORS = ...
_NAUPD_ERRORS = ...
_SEUPD_ERRORS = ...
_NEUPD_ERRORS = ...
_SEUPD_WHICH = ...
_NEUPD_WHICH = ...
class ArpackError(RuntimeError):
    """
    ARPACK error
    """
    def __init__(self, info, infodict=...) -> None:
        ...
    


class ArpackNoConvergence(ArpackError):
    """
    ARPACK iteration did not converge

    Attributes
    ----------
    eigenvalues : ndarray
        Partial result. Converged eigenvalues.
    eigenvectors : ndarray
        Partial result. Converged eigenvectors.

    """
    def __init__(self, msg, eigenvalues, eigenvectors) -> None:
        ...
    


def choose_ncv(k): # -> int:
    """
    Choose number of lanczos vectors based on target number
    of singular/eigen values and vectors to compute, k.
    """
    ...

class _ArpackParams:
    def __init__(self, n, k, tp, mode=..., sigma=..., ncv=..., v0=..., maxiter=..., which=..., tol=...) -> None:
        ...
    


class _SymmetricArpackParams(_ArpackParams):
    def __init__(self, n, k, tp, matvec, mode=..., M_matvec=..., Minv_matvec=..., sigma=..., ncv=..., v0=..., maxiter=..., which=..., tol=...) -> None:
        ...
    
    def iterate(self): # -> None:
        ...
    
    def extract(self, return_eigenvectors): # -> tuple[Any, Any] | Any:
        ...
    


class _UnsymmetricArpackParams(_ArpackParams):
    def __init__(self, n, k, tp, matvec, mode=..., M_matvec=..., Minv_matvec=..., sigma=..., ncv=..., v0=..., maxiter=..., which=..., tol=...) -> None:
        ...
    
    def iterate(self): # -> None:
        ...
    
    def extract(self, return_eigenvectors): # -> tuple[Any, Any] | Any:
        ...
    


class SpLuInv(LinearOperator):
    """
    SpLuInv:
       helper class to repeatedly solve M*x=b
       using a sparse LU-decomposition of M
    """
    def __init__(self, M) -> None:
        ...
    


class LuInv(LinearOperator):
    """
    LuInv:
       helper class to repeatedly solve M*x=b
       using an LU-decomposition of M
    """
    def __init__(self, M) -> None:
        ...
    


def gmres_loose(A, b, tol):
    """
    gmres with looser termination condition.
    """
    ...

class IterInv(LinearOperator):
    """
    IterInv:
       helper class to repeatedly solve M*x=b
       using an iterative method.
    """
    def __init__(self, M, ifunc=..., tol=...) -> None:
        ...
    


class IterOpInv(LinearOperator):
    """
    IterOpInv:
       helper class to repeatedly solve [A-sigma*M]*x = b
       using an iterative method
    """
    def __init__(self, A, M, sigma, ifunc=..., tol=...) -> None:
        ...
    
    @property
    def dtype(self):
        ...
    


def get_inv_matvec(M, hermitian=..., tol=...): # -> (x: Unknown) -> Unknown:
    ...

def get_OPinv_matvec(A, M, sigma, hermitian=..., tol=...): # -> (x: Unknown) -> Unknown:
    ...

_ARPACK_LOCK = ...
def eigs(A, k=..., M=..., sigma=..., which=..., v0=..., ncv=..., maxiter=..., tol=..., return_eigenvectors=..., Minv=..., OPinv=..., OPpart=...): # -> tuple[Unknown, Unknown, Unknown] | tuple[Unknown, Unknown] | tuple[Any, Any] | Any:
    """
    Find k eigenvalues and eigenvectors of the square matrix A.

    Solves ``A * x[i] = w[i] * x[i]``, the standard eigenvalue problem
    for w[i] eigenvalues with corresponding eigenvectors x[i].

    If M is specified, solves ``A * x[i] = w[i] * M * x[i]``, the
    generalized eigenvalue problem for w[i] eigenvalues
    with corresponding eigenvectors x[i]

    Parameters
    ----------
    A : ndarray, sparse matrix or LinearOperator
        An array, sparse matrix, or LinearOperator representing
        the operation ``A * x``, where A is a real or complex square matrix.
    k : int, optional
        The number of eigenvalues and eigenvectors desired.
        `k` must be smaller than N-1. It is not possible to compute all
        eigenvectors of a matrix.
    M : ndarray, sparse matrix or LinearOperator, optional
        An array, sparse matrix, or LinearOperator representing
        the operation M*x for the generalized eigenvalue problem

            A * x = w * M * x.

        M must represent a real symmetric matrix if A is real, and must
        represent a complex Hermitian matrix if A is complex. For best
        results, the data type of M should be the same as that of A.
        Additionally:

            If `sigma` is None, M is positive definite

            If sigma is specified, M is positive semi-definite

        If sigma is None, eigs requires an operator to compute the solution
        of the linear equation ``M * x = b``.  This is done internally via a
        (sparse) LU decomposition for an explicit matrix M, or via an
        iterative solver for a general linear operator.  Alternatively,
        the user can supply the matrix or operator Minv, which gives
        ``x = Minv * b = M^-1 * b``.
    sigma : real or complex, optional
        Find eigenvalues near sigma using shift-invert mode.  This requires
        an operator to compute the solution of the linear system
        ``[A - sigma * M] * x = b``, where M is the identity matrix if
        unspecified. This is computed internally via a (sparse) LU
        decomposition for explicit matrices A & M, or via an iterative
        solver if either A or M is a general linear operator.
        Alternatively, the user can supply the matrix or operator OPinv,
        which gives ``x = OPinv * b = [A - sigma * M]^-1 * b``.
        For a real matrix A, shift-invert can either be done in imaginary
        mode or real mode, specified by the parameter OPpart ('r' or 'i').
        Note that when sigma is specified, the keyword 'which' (below)
        refers to the shifted eigenvalues ``w'[i]`` where:

            If A is real and OPpart == 'r' (default),
              ``w'[i] = 1/2 * [1/(w[i]-sigma) + 1/(w[i]-conj(sigma))]``.

            If A is real and OPpart == 'i',
              ``w'[i] = 1/2i * [1/(w[i]-sigma) - 1/(w[i]-conj(sigma))]``.

            If A is complex, ``w'[i] = 1/(w[i]-sigma)``.

    v0 : ndarray, optional
        Starting vector for iteration.
        Default: random
    ncv : int, optional
        The number of Lanczos vectors generated
        `ncv` must be greater than `k`; it is recommended that ``ncv > 2*k``.
        Default: ``min(n, max(2*k + 1, 20))``
    which : str, ['LM' | 'SM' | 'LR' | 'SR' | 'LI' | 'SI'], optional
        Which `k` eigenvectors and eigenvalues to find:

            'LM' : largest magnitude

            'SM' : smallest magnitude

            'LR' : largest real part

            'SR' : smallest real part

            'LI' : largest imaginary part

            'SI' : smallest imaginary part

        When sigma != None, 'which' refers to the shifted eigenvalues w'[i]
        (see discussion in 'sigma', above).  ARPACK is generally better
        at finding large values than small values.  If small eigenvalues are
        desired, consider using shift-invert mode for better performance.
    maxiter : int, optional
        Maximum number of Arnoldi update iterations allowed
        Default: ``n*10``
    tol : float, optional
        Relative accuracy for eigenvalues (stopping criterion)
        The default value of 0 implies machine precision.
    return_eigenvectors : bool, optional
        Return eigenvectors (True) in addition to eigenvalues
    Minv : ndarray, sparse matrix or LinearOperator, optional
        See notes in M, above.
    OPinv : ndarray, sparse matrix or LinearOperator, optional
        See notes in sigma, above.
    OPpart : {'r' or 'i'}, optional
        See notes in sigma, above

    Returns
    -------
    w : ndarray
        Array of k eigenvalues.
    v : ndarray
        An array of `k` eigenvectors.
        ``v[:, i]`` is the eigenvector corresponding to the eigenvalue w[i].

    Raises
    ------
    ArpackNoConvergence
        When the requested convergence is not obtained.
        The currently converged eigenvalues and eigenvectors can be found
        as ``eigenvalues`` and ``eigenvectors`` attributes of the exception
        object.

    See Also
    --------
    eigsh : eigenvalues and eigenvectors for symmetric matrix A
    svds : singular value decomposition for a matrix A

    Notes
    -----
    This function is a wrapper to the ARPACK [1]_ SNEUPD, DNEUPD, CNEUPD,
    ZNEUPD, functions which use the Implicitly Restarted Arnoldi Method to
    find the eigenvalues and eigenvectors [2]_.

    References
    ----------
    .. [1] ARPACK Software, http://www.caam.rice.edu/software/ARPACK/
    .. [2] R. B. Lehoucq, D. C. Sorensen, and C. Yang,  ARPACK USERS GUIDE:
       Solution of Large Scale Eigenvalue Problems by Implicitly Restarted
       Arnoldi Methods. SIAM, Philadelphia, PA, 1998.

    Examples
    --------
    Find 6 eigenvectors of the identity matrix:

    >>> from scipy.sparse.linalg import eigs
    >>> id = np.eye(13)
    >>> vals, vecs = eigs(id, k=6)
    >>> vals
    array([ 1.+0.j,  1.+0.j,  1.+0.j,  1.+0.j,  1.+0.j,  1.+0.j])
    >>> vecs.shape
    (13, 6)

    """
    ...

def eigsh(A, k=..., M=..., sigma=..., which=..., v0=..., ncv=..., maxiter=..., tol=..., return_eigenvectors=..., Minv=..., OPinv=..., mode=...): # -> tuple[Unknown | Any, Unknown | Any] | Any | tuple[Unknown, Unknown] | tuple[Any, Any]:
    """
    Find k eigenvalues and eigenvectors of the real symmetric square matrix
    or complex Hermitian matrix A.

    Solves ``A * x[i] = w[i] * x[i]``, the standard eigenvalue problem for
    w[i] eigenvalues with corresponding eigenvectors x[i].

    If M is specified, solves ``A * x[i] = w[i] * M * x[i]``, the
    generalized eigenvalue problem for w[i] eigenvalues
    with corresponding eigenvectors x[i].

    Note that there is no specialized routine for the case when A is a complex
    Hermitian matrix. In this case, ``eigsh()`` will call ``eigs()`` and return the
    real parts of the eigenvalues thus obtained.

    Parameters
    ----------
    A : ndarray, sparse matrix or LinearOperator
        A square operator representing the operation ``A * x``, where ``A`` is
        real symmetric or complex Hermitian. For buckling mode (see below)
        ``A`` must additionally be positive-definite.
    k : int, optional
        The number of eigenvalues and eigenvectors desired.
        `k` must be smaller than N. It is not possible to compute all
        eigenvectors of a matrix.

    Returns
    -------
    w : array
        Array of k eigenvalues.
    v : array
        An array representing the `k` eigenvectors.  The column ``v[:, i]`` is
        the eigenvector corresponding to the eigenvalue ``w[i]``.

    Other Parameters
    ----------------
    M : An N x N matrix, array, sparse matrix, or linear operator representing
        the operation ``M @ x`` for the generalized eigenvalue problem

            A @ x = w * M @ x.

        M must represent a real symmetric matrix if A is real, and must
        represent a complex Hermitian matrix if A is complex. For best
        results, the data type of M should be the same as that of A.
        Additionally:

            If sigma is None, M is symmetric positive definite.

            If sigma is specified, M is symmetric positive semi-definite.

            In buckling mode, M is symmetric indefinite.

        If sigma is None, eigsh requires an operator to compute the solution
        of the linear equation ``M @ x = b``. This is done internally via a
        (sparse) LU decomposition for an explicit matrix M, or via an
        iterative solver for a general linear operator.  Alternatively,
        the user can supply the matrix or operator Minv, which gives
        ``x = Minv @ b = M^-1 @ b``.
    sigma : real
        Find eigenvalues near sigma using shift-invert mode.  This requires
        an operator to compute the solution of the linear system
        ``[A - sigma * M] x = b``, where M is the identity matrix if
        unspecified.  This is computed internally via a (sparse) LU
        decomposition for explicit matrices A & M, or via an iterative
        solver if either A or M is a general linear operator.
        Alternatively, the user can supply the matrix or operator OPinv,
        which gives ``x = OPinv @ b = [A - sigma * M]^-1 @ b``.
        Note that when sigma is specified, the keyword 'which' refers to
        the shifted eigenvalues ``w'[i]`` where:

            if mode == 'normal', ``w'[i] = 1 / (w[i] - sigma)``.

            if mode == 'cayley', ``w'[i] = (w[i] + sigma) / (w[i] - sigma)``.

            if mode == 'buckling', ``w'[i] = w[i] / (w[i] - sigma)``.

        (see further discussion in 'mode' below)
    v0 : ndarray, optional
        Starting vector for iteration.
        Default: random
    ncv : int, optional
        The number of Lanczos vectors generated ncv must be greater than k and
        smaller than n; it is recommended that ``ncv > 2*k``.
        Default: ``min(n, max(2*k + 1, 20))``
    which : str ['LM' | 'SM' | 'LA' | 'SA' | 'BE']
        If A is a complex Hermitian matrix, 'BE' is invalid.
        Which `k` eigenvectors and eigenvalues to find:

            'LM' : Largest (in magnitude) eigenvalues.

            'SM' : Smallest (in magnitude) eigenvalues.

            'LA' : Largest (algebraic) eigenvalues.

            'SA' : Smallest (algebraic) eigenvalues.

            'BE' : Half (k/2) from each end of the spectrum.

        When k is odd, return one more (k/2+1) from the high end.
        When sigma != None, 'which' refers to the shifted eigenvalues ``w'[i]``
        (see discussion in 'sigma', above).  ARPACK is generally better
        at finding large values than small values.  If small eigenvalues are
        desired, consider using shift-invert mode for better performance.
    maxiter : int, optional
        Maximum number of Arnoldi update iterations allowed.
        Default: ``n*10``
    tol : float
        Relative accuracy for eigenvalues (stopping criterion).
        The default value of 0 implies machine precision.
    Minv : N x N matrix, array, sparse matrix, or LinearOperator
        See notes in M, above.
    OPinv : N x N matrix, array, sparse matrix, or LinearOperator
        See notes in sigma, above.
    return_eigenvectors : bool
        Return eigenvectors (True) in addition to eigenvalues.
        This value determines the order in which eigenvalues are sorted.
        The sort order is also dependent on the `which` variable.

            For which = 'LM' or 'SA':
                If `return_eigenvectors` is True, eigenvalues are sorted by
                algebraic value.

                If `return_eigenvectors` is False, eigenvalues are sorted by
                absolute value.

            For which = 'BE' or 'LA':
                eigenvalues are always sorted by algebraic value.

            For which = 'SM':
                If `return_eigenvectors` is True, eigenvalues are sorted by
                algebraic value.

                If `return_eigenvectors` is False, eigenvalues are sorted by
                decreasing absolute value.

    mode : string ['normal' | 'buckling' | 'cayley']
        Specify strategy to use for shift-invert mode.  This argument applies
        only for real-valued A and sigma != None.  For shift-invert mode,
        ARPACK internally solves the eigenvalue problem
        ``OP * x'[i] = w'[i] * B * x'[i]``
        and transforms the resulting Ritz vectors x'[i] and Ritz values w'[i]
        into the desired eigenvectors and eigenvalues of the problem
        ``A * x[i] = w[i] * M * x[i]``.
        The modes are as follows:

            'normal' :
                OP = [A - sigma * M]^-1 @ M,
                B = M,
                w'[i] = 1 / (w[i] - sigma)

            'buckling' :
                OP = [A - sigma * M]^-1 @ A,
                B = A,
                w'[i] = w[i] / (w[i] - sigma)

            'cayley' :
                OP = [A - sigma * M]^-1 @ [A + sigma * M],
                B = M,
                w'[i] = (w[i] + sigma) / (w[i] - sigma)

        The choice of mode will affect which eigenvalues are selected by
        the keyword 'which', and can also impact the stability of
        convergence (see [2] for a discussion).

    Raises
    ------
    ArpackNoConvergence
        When the requested convergence is not obtained.

        The currently converged eigenvalues and eigenvectors can be found
        as ``eigenvalues`` and ``eigenvectors`` attributes of the exception
        object.

    See Also
    --------
    eigs : eigenvalues and eigenvectors for a general (nonsymmetric) matrix A
    svds : singular value decomposition for a matrix A

    Notes
    -----
    This function is a wrapper to the ARPACK [1]_ SSEUPD and DSEUPD
    functions which use the Implicitly Restarted Lanczos Method to
    find the eigenvalues and eigenvectors [2]_.

    References
    ----------
    .. [1] ARPACK Software, http://www.caam.rice.edu/software/ARPACK/
    .. [2] R. B. Lehoucq, D. C. Sorensen, and C. Yang,  ARPACK USERS GUIDE:
       Solution of Large Scale Eigenvalue Problems by Implicitly Restarted
       Arnoldi Methods. SIAM, Philadelphia, PA, 1998.

    Examples
    --------
    >>> from scipy.sparse.linalg import eigsh
    >>> identity = np.eye(13)
    >>> eigenvalues, eigenvectors = eigsh(identity, k=6)
    >>> eigenvalues
    array([1., 1., 1., 1., 1., 1.])
    >>> eigenvectors.shape
    (13, 6)

    """
    ...

def svds(A, k=..., ncv=..., tol=..., which=..., v0=..., maxiter=..., return_singular_vectors=..., solver=...): # -> tuple[Unknown | None, Unknown, Unknown | None]:
    """Compute the largest or smallest k singular values/vectors for a sparse matrix. The order of the singular values is not guaranteed.

    Parameters
    ----------
    A : {sparse matrix, LinearOperator}
        Array to compute the SVD on, of shape (M, N)
    k : int, optional
        Number of singular values and vectors to compute.
        Must be 1 <= k < min(A.shape).
    ncv : int, optional
        The number of Lanczos vectors generated
        ncv must be greater than k+1 and smaller than n;
        it is recommended that ncv > 2*k
        Default: ``min(n, max(2*k + 1, 20))``
    tol : float, optional
        Tolerance for singular values. Zero (default) means machine precision.
    which : str, ['LM' | 'SM'], optional
        Which `k` singular values to find:

            - 'LM' : largest singular values
            - 'SM' : smallest singular values

        .. versionadded:: 0.12.0
    v0 : ndarray, optional
        Starting vector for iteration, of length min(A.shape). Should be an
        (approximate) left singular vector if N > M and a right singular
        vector otherwise.
        Default: random

        .. versionadded:: 0.12.0
    maxiter : int, optional
        Maximum number of iterations.

        .. versionadded:: 0.12.0
    return_singular_vectors : bool or str, optional
        - True: return singular vectors (True) in addition to singular values.

        .. versionadded:: 0.12.0

        - "u": only return the u matrix, without computing vh (if N > M).
        - "vh": only return the vh matrix, without computing u (if N <= M).

        .. versionadded:: 0.16.0
    solver : str, optional
            Eigenvalue solver to use. Should be 'arpack' or 'lobpcg'.
            Default: 'arpack'

    Returns
    -------
    u : ndarray, shape=(M, k)
        Unitary matrix having left singular vectors as columns.
        If `return_singular_vectors` is "vh", this variable is not computed,
        and None is returned instead.
    s : ndarray, shape=(k,)
        The singular values.
    vt : ndarray, shape=(k, N)
        Unitary matrix having right singular vectors as rows.
        If `return_singular_vectors` is "u", this variable is not computed,
        and None is returned instead.


    Notes
    -----
    This is a naive implementation using ARPACK or LOBPCG as an eigensolver
    on A.H * A or A * A.H, depending on which one is more efficient.

    Examples
    --------
    >>> from scipy.sparse import csc_matrix
    >>> from scipy.sparse.linalg import svds, eigs
    >>> A = csc_matrix([[1, 0, 0], [5, 0, 2], [0, -1, 0], [0, 0, 3]], dtype=float)
    >>> u, s, vt = svds(A, k=2)
    >>> s
    array([ 2.75193379,  5.6059665 ])
    >>> np.sqrt(eigs(A.dot(A.T), k=2)[0]).real
    array([ 5.6059665 ,  2.75193379])
    """
    ...
