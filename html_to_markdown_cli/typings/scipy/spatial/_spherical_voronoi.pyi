"""
This type stub file was generated by pyright.
"""

"""
Spherical Voronoi Code

.. versionadded:: 0.18.0

"""
def calculate_solid_angles(R):
    """Calculates the solid angles of plane triangles. Implements the method of
    Van Oosterom and Strackee [VanOosterom]_ with some modifications. Assumes
    that input points have unit norm."""
    ...

class SphericalVoronoi:
    """ Voronoi diagrams on the surface of a sphere.

    .. versionadded:: 0.18.0

    Parameters
    ----------
    points : ndarray of floats, shape (npoints, ndim)
        Coordinates of points from which to construct a spherical
        Voronoi diagram.
    radius : float, optional
        Radius of the sphere (Default: 1)
    center : ndarray of floats, shape (ndim,)
        Center of sphere (Default: origin)
    threshold : float
        Threshold for detecting duplicate points and
        mismatches between points and sphere parameters.
        (Default: 1e-06)

    Attributes
    ----------
    points : double array of shape (npoints, ndim)
        the points in `ndim` dimensions to generate the Voronoi diagram from
    radius : double
        radius of the sphere
    center : double array of shape (ndim,)
        center of the sphere
    vertices : double array of shape (nvertices, ndim)
        Voronoi vertices corresponding to points
    regions : list of list of integers of shape (npoints, _ )
        the n-th entry is a list consisting of the indices
        of the vertices belonging to the n-th point in points

    Methods
    -------
    calculate_areas
        Calculates the areas of the Voronoi regions. For 2D point sets, the
        regions are circular arcs. The sum of the areas is `2 * pi * radius`.
        For 3D point sets, the regions are spherical polygons. The sum of the
        areas is `4 * pi * radius**2`.

    Raises
    ------
    ValueError
        If there are duplicates in `points`.
        If the provided `radius` is not consistent with `points`.

    Notes
    -----
    The spherical Voronoi diagram algorithm proceeds as follows. The Convex
    Hull of the input points (generators) is calculated, and is equivalent to
    their Delaunay triangulation on the surface of the sphere [Caroli]_.
    The Convex Hull neighbour information is then used to
    order the Voronoi region vertices around each generator. The latter
    approach is substantially less sensitive to floating point issues than
    angle-based methods of Voronoi region vertex sorting.

    Empirical assessment of spherical Voronoi algorithm performance suggests
    quadratic time complexity (loglinear is optimal, but algorithms are more
    challenging to implement).

    References
    ----------
    .. [Caroli] Caroli et al. Robust and Efficient Delaunay triangulations of
                points on or close to a sphere. Research Report RR-7004, 2009.

    .. [VanOosterom] Van Oosterom and Strackee. The solid angle of a plane
                     triangle. IEEE Transactions on Biomedical Engineering,
                     2, 1983, pp 125--126.

    See Also
    --------
    Voronoi : Conventional Voronoi diagrams in N dimensions.

    Examples
    --------
    Do some imports and take some points on a cube:

    >>> import matplotlib.pyplot as plt
    >>> from scipy.spatial import SphericalVoronoi, geometric_slerp
    >>> from mpl_toolkits.mplot3d import proj3d
    >>> # set input data
    >>> points = np.array([[0, 0, 1], [0, 0, -1], [1, 0, 0],
    ...                    [0, 1, 0], [0, -1, 0], [-1, 0, 0], ])

    Calculate the spherical Voronoi diagram:

    >>> radius = 1
    >>> center = np.array([0, 0, 0])
    >>> sv = SphericalVoronoi(points, radius, center)

    Generate plot:

    >>> # sort vertices (optional, helpful for plotting)
    >>> sv.sort_vertices_of_regions()
    >>> t_vals = np.linspace(0, 1, 2000)
    >>> fig = plt.figure()
    >>> ax = fig.add_subplot(111, projection='3d')
    >>> # plot the unit sphere for reference (optional)
    >>> u = np.linspace(0, 2 * np.pi, 100)
    >>> v = np.linspace(0, np.pi, 100)
    >>> x = np.outer(np.cos(u), np.sin(v))
    >>> y = np.outer(np.sin(u), np.sin(v))
    >>> z = np.outer(np.ones(np.size(u)), np.cos(v))
    >>> ax.plot_surface(x, y, z, color='y', alpha=0.1)
    >>> # plot generator points
    >>> ax.scatter(points[:, 0], points[:, 1], points[:, 2], c='b')
    >>> # plot Voronoi vertices
    >>> ax.scatter(sv.vertices[:, 0], sv.vertices[:, 1], sv.vertices[:, 2],
    ...                    c='g')
    >>> # indicate Voronoi regions (as Euclidean polygons)
    >>> for region in sv.regions:
    ...    n = len(region)
    ...    for i in range(n):
    ...        start = sv.vertices[region][i]
    ...        end = sv.vertices[region][(i + 1) % n]
    ...        result = geometric_slerp(start, end, t_vals)
    ...        ax.plot(result[..., 0],
    ...                result[..., 1],
    ...                result[..., 2],
    ...                c='k')
    >>> ax.azim = 10
    >>> ax.elev = 40
    >>> _ = ax.set_xticks([])
    >>> _ = ax.set_yticks([])
    >>> _ = ax.set_zticks([])
    >>> fig.set_size_inches(4, 4)
    >>> plt.show()

    """
    def __init__(self, points, radius=..., center=..., threshold=...) -> None:
        ...
    
    def sort_vertices_of_regions(self): # -> None:
        """Sort indices of the vertices to be (counter-)clockwise ordered.

        Raises
        ------
        TypeError
            If the points are not three-dimensional.

        Notes
        -----
        For each region in regions, it sorts the indices of the Voronoi
        vertices such that the resulting points are in a clockwise or
        counterclockwise order around the generator point.

        This is done as follows: Recall that the n-th region in regions
        surrounds the n-th generator in points and that the k-th
        Voronoi vertex in vertices is the circumcenter of the k-th triangle
        in self._simplices.  For each region n, we choose the first triangle
        (=Voronoi vertex) in self._simplices and a vertex of that triangle
        not equal to the center n. These determine a unique neighbor of that
        triangle, which is then chosen as the second triangle. The second
        triangle will have a unique vertex not equal to the current vertex or
        the center. This determines a unique neighbor of the second triangle,
        which is then chosen as the third triangle and so forth. We proceed
        through all the triangles (=Voronoi vertices) belonging to the
        generator in points and obtain a sorted version of the vertices
        of its surrounding region.
        """
        ...
    
    def calculate_areas(self):
        """Calculates the areas of the Voronoi regions.

        For 2D point sets, the regions are circular arcs. The sum of the areas
        is `2 * pi * radius`.

        For 3D point sets, the regions are spherical polygons. The sum of the
        areas is `4 * pi * radius**2`.

        .. versionadded:: 1.5.0

        Returns
        -------
        areas : double array of shape (npoints,)
            The areas of the Voronoi regions.
        """
        ...
    

