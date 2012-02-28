#!/usr/bin/env python

from PISMNC import PISMDataset as NC
import subprocess
import numpy as np
import os
import optparse

## Set up the option parser
parser = optparse.OptionParser()
parser.usage = """usage: %prog start_year
Here start_year is one of '2000', '2005', '2006'."""
parser.description = "This script downloads and preprocesses MEaSUREs Greenland Ice Velocity data"

(options, args) = parser.parse_args()


if len(args) == 1 and args[0] in ["2000", "2005", "2006"]:
    start_year = int(args[0])
else:
    parser.print_help()
    exit(0)

years = "%d_%d" % (start_year, start_year + 1)
ex_filename  = "greenland_vel_mosaic500_%s.ex" % years
ey_filename  = "greenland_vel_mosaic500_%s.ey" % years
vx_filename  = "greenland_vel_mosaic500_%s.vx" % years
vy_filename  = "greenland_vel_mosaic500_%s.vy" % years
ftp_url = "ftp://anonymous@sidads.colorado.edu/pub/DATASETS/nsidc0478_MEASURES_greenland_V01/%d/" % start_year

def download_and_unpack(url, filename):
    try:
        os.stat(filename)
        print "File '%s' already exists." % filename
    except:
        try:
            os.stat(filename + ".gz")
        except:
            print "Downloading '%s'..." % (filename + '.gz')
            subprocess.call(["wget", "-nc", url + filename + ".gz"])

        print "Unpacking %s..." % filename
        subprocess.call(["gunzip", filename + ".gz"])

download_and_unpack(ftp_url, vx_filename)
download_and_unpack(ftp_url, vx_filename + ".geodat")
download_and_unpack(ftp_url, vy_filename)
download_and_unpack(ftp_url, ex_filename)
download_and_unpack(ftp_url, ey_filename)

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
                                          (vy_filename, "vy", "ice surface velocity in the Y direction"),
                                          (ex_filename, "ex",
                                           "error estimates for the X-component of the ice surface velocity"),
                                          (ey_filename, "ey",
                                           "error estimates for the Y-component of the ice surface velocity"),
                                          ]:

    nc.define_2d_field(short_name, time_dependent = False, nc_type='f4',
                       attrs = {"long_name"   : long_name,
                                "comment"     : "Downloaded from %s" % (ftp_url + filename),
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
nc.reference  = "Joughin, I., B. Smith, I. Howat, and T. Scambos. 2010. MEaSUREs Greenland Ice Velocity Map from InSAR Data. Boulder, Colorado, USA: National Snow and Ice Data Center. Digital media."
nc.title      = "MEaSUREs Greenland Ice Velocity Map from InSAR Data"

from time import asctime
import sys
separator = ' '
historystr = "%s: %s\n" % (asctime(), separator.join(sys.argv))
nc.history = historystr

nc.close()


