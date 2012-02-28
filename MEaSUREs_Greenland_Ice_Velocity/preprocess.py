#!/usr/bin/env python

from PISMNC import PISMDataset as NC
import subprocess
import numpy as np
import os

ex_filename  = "greenland_vel_mosaic500_2006_2007.ex"
ey_filename  = "greenland_vel_mosaic500_2006_2007.ey"
vx_filename  = "greenland_vel_mosaic500_2006_2007.vx"
vy_filename  = "greenland_vel_mosaic500_2006_2007.vy"
ftp_url = "ftp://anonymous@sidads.colorado.edu/pub/DATASETS/nsidc0478_MEASURES_greenland_V01/2006/"

def download(url, filename):
    try:
        os.stat(filename)
        print "File '%s' already exists." % filename
    except:
        print "Downloading '%s'..." % filename
        subprocess.call(["wget", "-nc", url + filename])
        subprocess.call(["wget", "-nc", url + filename + ".geodat"])

download(ftp_url, vx_filename)
download(ftp_url, vy_filename)
# download(ftp_url, ex_filename)
# download(ftp_url, ey_filename)

grid = np.loadtxt(vx_filename + ".geodat", skiprows=1, comments="&")

shape = (int(grid[0,1]), int(grid[0,0]))
x0 = grid[2,0] * 1e3
y0 = grid[2,1] * 1e3
dx = grid[1,0]
dy = grid[1,1]
x1 = x0 + (shape[1] - 1) * dx
y1 = y0 + (shape[0] - 1) * dx
x = np.linspace(x0, x1, shape[1])
y = np.linspace(y0, y1, shape[0])

nc = NC("MEASUREs_Greenland_2006_2007.nc", 'w')
nc.create_dimensions(x, y)

for (filename, short_name, long_name) in [(vx_filename, "vx", "ice surface velocity in the X direction"),
                                          (vy_filename, "vy", "ice surface velocity in the Y direction")]:

    nc.define_2d_field(short_name, time_dependent = False, nc_type='f4',
                       attrs = {"long_name"   : long_name,
                                "comment"     : "Downloaded from %s" % (ftp_url + vx_filename),
                                "units"       : "m / year",
                                "mapping"     : "mapping",
                                "_FillValue"  : -2e+9})

    var = np.fromfile(filename, dtype=">f4", count=-1)

    nc.write_2d_field(short_name, var)

mapping = nc.createVariable("mapping", 'c')
mapping.grid_mapping_name = "polar_stereographic"
mapping.standard_parallel = 70.0
mapping.latitude_of_projection_origin = 90.0
mapping.straight_vertical_longitude_from_pole = -45.0
mapping.ellipsoid = "WGS84"

nc.Conventions = "CF-1.4"
nc.projection = "+proj=stere +ellps=WGS84 +datum=WGS84 +lon_0=-45 +lat_0=90 +lat_ts=70 +units=m"

from time import asctime
import sys
separator = ' '
historystr = "%s: %s\n" % (asctime(), separator.join(sys.argv))
nc.history = historystr

nc.close()


