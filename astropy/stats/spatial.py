# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This module implements functions and classes for spatial statistics.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import math

class RipleysKEstimate(object):
    """
    This class implements an estimator for Ripley's K function in a two
    dimensional space.

    Parameters
    ----------
    data : 2D array
        Set of observed points in as a n by 2 array which will be used to
        estimate Ripley's K function.
    area : float
        Area of study from which the points where observed.
    max_height, max_width : float, float
        Maximum rectangular dimensions of the area of study.

    Examples
    --------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from astropy.stats import RipleysKEstimate
    >>> x = np.random.uniform(low=5, high=10, size=100)
    >>> y = np.random.uniform(low=5, high=10, size=100)
    >>> z = np.array([x,y]).T
    >>> area = 25
    >>> Kest = RipleysKEstimate(data=z, area=area)
    >>> r = np.linspace(0, 2.5, 100)
    >>> plt.plot(r, Kest(r))

    References
    ----------
    .. [1] Spatial descriptive statistics.
       <https://en.wikipedia.org/wiki/Spatial_descriptive_statistics>
    .. [2] Package spatstat.
       <https://cran.r-project.org/web/packages/spatstat/spatstat.pdf>
    .. [3] Cressie, N.A.C. (1991). Statistics for Spatial Data,
       Wiley, New York.
    .. [4] Stoyan, D., Stoyan, H. (1992). Fractals, Random Shapes and
       Point Fields, Akademie Verlag GmbH, Chichester.
    """

    def __init__(self, data, area=None, max_height=None, max_width=None):
        self.data = data
        self.area = area
        self.max_height = max_height
        self.max_width = max_width

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        value = np.asarray(value)

        if value.shape[1] == 2:
            self._data = value
        else:
            raise ValueError('data must be an n by 2 array, where n is the '
                             'number of observed points.')

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, value):
        if not isinstance(value, (float, int)) or value < 0:
            raise ValueError('area is expected to be a positive number.'
                             'Got {}.'.format(value))
        else:
            self._area = value

    @property
    def max_height(self):
        return self._max_height

    @max_height.setter
    def max_height(self, value):
        if not isinstance(value, (float, int)) or value < 0:
            raise ValueError('max_height is expected to be a positive number.'
                             'Got {}.'.format(value))
        else:
            self._max_height = value

    @property
    def max_width(self):
        return self._max_width

    @max_width.setter
    def max_width(self, value):
        if not isinstance(value, (float, int)) or value < 0:
            raise ValueError('max_width is expected to be a positive number.'
                             'Got {}.'.format(value))
        else:
            self._max_width = value

    def __call__(self, radii, mode='none'):
        return self.evaluate(radii=radii, mode=mode)

    def evaluate(self, radii, mode='none'):
        """
        Evaluates the Ripley K estimator for a given set of values ``radii``.

        Parameters
        ----------
        radii : 1D array
            Set of distances in which Ripley's K estimator will be evaluated.
            Usually, it's common to consider max(radii) < (area/2)**0.5.
        mode : str
            Keyword which indicates the method for edge effects correction.

        Returns
        -------
        output : 1D array
            Ripley's K function estimator evaluated at ``radii``.
        """

        self.data = np.asarray(self.data)
        npts = len(self.data)
        ripley = np.zeros(len(radii))
        distances = np.zeros((npts * (npts - 1)) // 2, dtype=np.double)
        diff = np.zeros(shape=(npts * (npts - 1) // 2, 2), dtype=np.double)

        k = 0
        for i in range(npts - 1):
            for j in range(i + 1, npts):
                diff[k] = abs(self.data[i] - self.data[j])
                distances[k] = math.sqrt((diff[k] * diff[k]).sum())
                k = k + 1

        if mode == 'none':
            for idx in range(len(radii)):
                ripley[idx] = (distances < radii[idx]).sum()
            ripley = self.area * 2. * ripley / (npts * (npts - 1))
        elif mode == 'poisson':
            ripley = np.pi * radii * radii
        # eq. 15.11 Stoyan book
        elif mode == 'translation':
            height_diff, width_diff = diff[:][:, 0], diff[:][:, 1]
            for idx in range(len(radii)):
                dist_indicator = distances <  radii[idx]
                intersec_area = ((self.max_height - height_diff) *
                                 (self.max_width - width_diff))
                ripley[idx] = ((1 / intersec_area) * dist_indicator).sum()
            ripley = (self.area**2 / npts**2) * 2 * ripley
        else:
            raise ValueError('mode {} is not implemented'.format(mode))

        return ripley
