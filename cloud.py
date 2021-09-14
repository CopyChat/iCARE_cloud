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

    era5 = GEO_PLOT.read_to_standard_da('/Users/ctang/local_data/era5/rsds.era5.1999-2016.day.swio.nc', 'ssrd')
    if cfg.job.data_prepare.add_lon_lat:
        # reading HDF lonlat data:
        lon_1D = GEO_PLOT.read_binary_file(cfg.input.icare_3km_lon_MSG0000)
        lon = lon_1D.reshape((int(np.sqrt(lon_1D.shape[0])), -1))

        lat_1D = GEO_PLOT.read_binary_file(cfg.input.icare_3km_lat_MSG0000)
        lat = lat_1D.reshape((int(np.sqrt(lat_1D.shape[0])), -1))

        ct: xr.DataArray = GEO_PLOT.read_to_standard_da(cfg.input.icare_CT_MSG0000, 'ct')

        time = pd.date_range("2000-01-01", periods=1)
        da = xr.DataArray(np.expand_dims(ct.values, axis=0), dims=('time', 'x', 'y'), name=ct.name,
                          coords={
                              'time': ('time', time),
                              'lon': (['x', 'y'], lon),
                              'lat': (['x', 'y'], lat)
                          }
                          )
        # test = da.where(lon > 30, drop=True).where(lon < 40, drop=True)

        print(f'good')

    print('done')


if __name__ == "__main__":
    sys.exit(cloud())
