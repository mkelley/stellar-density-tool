"""Query a test star catalog."""

import numpy as np
from numpy.random import rand
from numpy import pi
import sqlite3
from astropy.io import ascii
from astropy.coordinates import Angle
import astropy.units as u
from astropy.table import Table

def sph2cart(ra, dec):
    """Spherical to Cartesian coordinate transformation."""
    return ((np.cos(dec) * np.cos(ra)).value,
            (np.cos(dec) * np.sin(ra)).value,
            np.sin(dec).value)

def nearest(ra, dec, rho, mlimit, db):
    """Find nearest catalog members.

    Parameters
    ----------
    ra, dec : Quantity or Angle
      Query coordinates.
    rho : Quantity
      Find stars within this distance.  Queries for angles outside of
      the small angle approximation will have an increased error.
    mlimit : float
      Find stars brighter than this magnitude.
    db : sqlite3.Cursor
      The cursor for the database to query.

    """

    x, y, z = sph2cart(ra, dec)

    # convert angular distance to Cartesian distance on the unit sphere.
    d = np.sin(rho).value

    r = db.execute('''SELECT m FROM catalog WHERE
      (x >= ?) AND (xx <= ?) AND
      (y >= ?) AND (yy <= ?) AND
      (z >= ?) AND (zz <= ?) AND
      (m <= ?)''', (x - d, x + d, y - d, y + d, z - d, z + d, mlimit))
    
    return r.fetchall()

eph = ascii.read('encke.eph')
rho = 5 * u.arcmin
mlimit = 14
with sqlite3.connect('bright-star.db') as conn:
    db = conn.cursor()

    nstars = []
    for row in eph:
        ra = Angle(row['ra'], unit=u.hourangle)
        dec = Angle(row['dec'], unit=u.deg)
        r = nearest(ra, dec, rho, mlimit, db)
        nstars.append(len(r))

eph['N stars'] = nstars
eph.pprint(max_lines=-1, max_width=-1)
