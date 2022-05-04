"""
to find the physical link between the SSR classification and the large-scale variability
over la reunion island and it's extended area
"""

__version__ = f'Version 2.0  \nTime-stamp: <2021-05-15>'
__author__ = "ChaoTANG@univ-reunion.fr"

import sys
import glob
import hydra
import numpy as np
import pandas as pd
import xarray as xr
from omegaconf import DictConfig
import matplotlib.pyplot as plt

import DATA
import GEO_PLOT


@hydra.main(config_path="configs", config_name="cloud")
def cloud(cfg: DictConfig) -> None:
    """
    to analysis iCARE cloud product
    """

    print('starting ...')

    if cfg.job.data.add_coords_to_raw_nc:
        # this piece of code could be used to add coords information to the downloaded
        # non-coordinated raw netCDF files.

        # all files to be processed:
        list_file: list = glob.glob(f'{cfg.dir.icare_data:s}/ct.*Z.nc')

        for raw_file in list_file:
            print(raw_file)
            da = DATA.add_lon_lat_to_raw_nc(raw_nc=raw_file,
                                            lon=cfg.input.icare_3km_lon_MSG0415,
                                            lat=cfg.input.icare_3km_lat_MSG0415,
                                            save=True)

        # return da just for test, not necessary when dealing with a large dataset.

        da.to_netcdf('./icare.lonlat.nc')
        # now check if it's still 2D:
        a = GEO_PLOT.read_to_standard_da('./icare.lonlat.nc', 'ct')
        # this function of read_to_standard_da will check randomly if the dim is static
        # (not changing with other dims). if not, this function will return a 2D coords and
        # print out some randomly selected differences to show, for example,
        # the array of lon is changing with lat.

        # try to select reunion:

        reu_box = GEO_PLOT.value_lonlatbox_from_area('reu')
        reu_box = [55.2, 55.9, -21.5, -20.8]
        b = a.where(
            np.logical_and((a.lon > reu_box[0]), (a.lon < reu_box[1])),
            drop=True)
        c = b.where(
            np.logical_and((b.lat > reu_box[2]), (b.lat < reu_box[-1])),
            drop=True)
        d = c.where(
            np.logical_and((c.lon > reu_box[0]), (c.lon < reu_box[1])),
            drop=True)

        d.to_netcdf('./reu.nc')


        # select a domain small enough, so that we get a nc file with regular projection.
        da2 = da[:, 890:900, 690:700]
        da2.to_netcdf('./icare.lonlat.reg.nc')

        # now, let's read da2 to see if we get a 1D coords:
        b = GEO_PLOT.read_to_standard_da('icare.lonlat.reg.nc', 'ct')

        # print out the coords, we will see that in a square of 10*10 pixel, we get a reguler projection.
        # while it depends on the distance to the centre point of the observation domain, which is 41.5 East.
        print(b.coords)

        print(f'good')

    print('done')


if __name__ == "__main__":
    sys.exit(cloud())
