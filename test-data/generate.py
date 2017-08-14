"""Generate a test database of coordinates and apparent magnitudes"""

import numpy as np
from numpy.random import rand
from numpy import pi
import sqlite3

def rand_sign(n):
    """Random variate: -1 or 1.

    Parameters
    ----------
    n : int
      Number of samples.

    Returns
    -------
    x : ndarray
      The random variates.

    """
    return np.random.randint(0, 2, n) * 2 - 1

def rand_angle_uniform(n, a0=0, a1=pi / 2):
    """Random variate, uniformly distributed in angle.

    Does not work for `a0 < 0`.

    Parameters
    ----------
    n : int
      Number of samples.
    a0, a1 : float, optional
      Minimum and maximum values.  [radians]

    Returns
    -------
    x : ndarray
      The random variates.  [radians]

    """
    u = rand(n)
    u = np.arccos(np.sqrt((1 - u) * np.cos(a0) + u * np.cos(a1)))
    return u


with sqlite3.connect('bright-star.db') as conn:
    db = conn.cursor()

    # delete old table, if it exists, create a new one
    try:
        db.execute('DROP TABLE catalog')
        conn.commit()
    except sqlite3.OperationalError as e:
        pass

    # create R*tree used for tile searching, but use Cartesian
    # coordinates to avoid polar singularities and the discontinuity
    # at RA=0d=360d.  Include magnitude.  R*tree format allows for
    # objects to have widths, but stars are essentially points: let
    # xmin=xmax, etc.  Thanks to Brian Carcich for the Cartesian
    # coordinate idea.
    db.execute('''CREATE VIRTUAL TABLE catalog USING rtree(
      id INTEGER PRIMARY KEY ASC,
      x, xx, y, yy, z, zz, m, mm
    )''')

    N = 44e6
    step = 10000
    print()
    for i in range(int(N / step)):
        print('{}          \r'.format(np.log10(i * step)), end='')
        ra = rand(step) * 2 * pi
        sign = rand_sign(step)
        dec = sign * rand_angle_uniform(step)
        x, y, z = np.array((np.cos(dec) * np.cos(ra),
                            np.cos(dec) * np.sin(ra),
                            np.sin(dec)))

        m = rand(step) * 14

        for star in zip(x, x, y, y, z, z, m, m):
            r = db.execute('INSERT INTO catalog VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?)', star)

        conn.commit()


