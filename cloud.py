"""
to find the physical link between the SSR classification and the large-scale variability
over la reunion island and it's extended area
"""

__version__ = f'Version 2.0  \nTime-stamp: <2021-05-15>'
__author__ = "ChaoTANG@univ-reunion.fr"

import sys
import hydra
import numpy as np
import pandas as pd
import xarray as xr
from omegaconf import DictConfig
import GEO_PLOT


@hydra.main(config_path="configs", config_name="cloud")
def cloud(cfg: DictConfig) -> None:
    """
    to analysis iCARE cloud product
    :param cfg:
    :type cfg:
    :return:
    :rtype:
    """

    print('starting ...')

    # this piece of code could be used to add coords information to the downloaded non-coordinated raw netCDF files.
    # even the test is done for MSG0000 projection, it could be the same for MSG0415.

    if cfg.job.data_prepare.add_lon_lat:
        # reading HDF lonlat data:
        lon_1D = GEO_PLOT.read_binary_file(cfg.input.icare_3km_lon_MSG0000)
        lon = lon_1D.reshape((int(np.sqrt(lon_1D.shape[0])), -1))

        lat_1D = GEO_PLOT.read_binary_file(cfg.input.icare_3km_lat_MSG0000)
        lat = lat_1D.reshape((int(np.sqrt(lat_1D.shape[0])), -1))

        # read raw data:
        ct: xr.DataArray = xr.open_dataset(cfg.input.icare_CT_MSG0000)['ct']

        # now, create a new DataArray, using an attribute timestamp
        # with lon and lat in two dims (x and y)
        time = pd.date_range("2000-01-01", periods=1)
        da = xr.DataArray(np.expand_dims(ct.values, axis=0), dims=('time', 'y', 'x'), name=ct.name,
                          coords={
                              'time': ('time', time),
                              'lon': (['y', 'x'], lon),
                              'lat': (['y', 'x'], lat)
                          },
                          attrs=ct.attrs
                          )

        # save it to NetCDF file with the lon and lat (2D).
        da.to_netcdf('./icare.lonlat.nc')

        # now check if it's still 2D:
        a = GEO_PLOT.read_to_standard_da('icare.lonlat.nc', 'ct')
        # this function of read_to_standard_da will check randomly if the dim is static
        # (not changing with other dims). if not, this function will return a 2D coords and
        # print out some randomly selected differences to show, for example,
        # the array of lon is changing with lat.

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
