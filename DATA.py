"""
data processing file
"""

__version__ = f'Version 2.0  \nTime-stamp: <2022-04-30>'
__author__ = "ChaoTANG@univ-reunion.fr"

import os
import sys
import hydra
import scipy
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from omegaconf import DictConfig
import GEO_PLOT


# ----------------------------- functions -----------------------------
def get_date():
    """
    to get date range for the NDJF from 1979-2018
    :return: list of DateTimeIndex
    """
    import datetime as dt
    dates = []
    for start_year in range(1979, 2018):
        date_time_str = f'{start_year:g}-11-01'
        date_time_obj = dt.datetime.strptime(date_time_str, '%Y-%m-%d')
        winter = pd.date_range(start=date_time_obj, periods=120, freq='24H')

        dates.append(winter)
    dates = [y for x in dates for y in x]

    return dates


def add_lon_lat_to_raw_nc(raw_nc: xr.DataArray, lon, lat, save: bool = True):
    """
    since the data is without any coords, with only dim numbers. this function adds the coords
     to the raw nc file, even if it may not be in a regular projection.
    :param raw_nc:
    :type raw_nc:
    :param lon:
    :type lon:
    :return:
    :rtype: xr.DataArray
    """
    # reading HDF lonlat data:
    lon_1D = GEO_PLOT.read_binary_file(lon)
    lon = lon_1D.reshape((int(np.sqrt(lon_1D.shape[0])), -1))

    lat_1D = GEO_PLOT.read_binary_file(lat)
    lat = lat_1D.reshape((int(np.sqrt(lat_1D.shape[0])), -1))

    # read raw data into xr.Dataset first, since icare has multiple variables.
    # time is in this Dataset, not in the DataArray with a single variable

    raw_da: xr.Dataset = xr.open_dataset(raw_nc)['ct']

    # now, create a new DataArray, using timestamp in the file name.
    # attention: that's the nominal_product_time, when the ~ 12 minutes obs starts

    # get time from file name:
    timestamp = raw_nc.split('_')[-1].split('Z')[0]
    # with code above, remove the UTC timezone info, and add it to the attributes of output nc file,
    # otherwise, the time in output nc will be in object format, not the DateTimeIndex.
    time = pd.date_range(timestamp, periods=1)  # only 1 timestep per file

    # then find the lon et lat corresponding to our selection of domain when downloading data: 632*855.
    # name it as global, even it's not global
    global_raw_nc = f'/Users/ctang/Microsoft_OneDrive/OneDrive/CODE/iCARE_cloud/local_data/' \
                  f'S_NWC_CT_MSG1_globeI-VISIR_20170827T120000Z.nc'
    global_raw_da = xr.open_dataset(global_raw_nc)['ct']

    global_nx = global_raw_da.nx
    global_ny = global_raw_da.ny

    local_nx = raw_da.nx
    local_ny = raw_da.ny

    # ================================== some test here
    # a = global_ny.values
    # b = local_ny.values
    #
    # total_len = a.max() - a.min()
    # b_start = b.min()
    #
    # offset_y = abs(a[-1] - b[-1])/total_len
    #
    # offset_x = abs(global_nx.values[0] - local_nx.values[0])/total_len
    # ================================== some test above

    # Note: the downloaded data has its own nx & nx, do a linear interpolation to get the coords:
    # define the interpolation on 2D:
    func_lon = scipy.interpolate.interp2d(global_nx, global_ny, lon, kind='linear')
    func_lat = scipy.interpolate.interp2d(global_nx, global_ny, lat, kind='linear')
    # attention: Unsupported interpolation type 'nearest', must be either of 'linear', 'cubic', 'quintic'

    local_lon = func_lon(local_nx, local_ny)
    local_lat = func_lat(local_nx, local_ny)

    # then create a new DataArray:
    da = xr.DataArray(np.expand_dims(raw_da.values, axis=0), dims=('time', 'y', 'x'), name=raw_da.name,
                      coords={
                          'time': ('time', time),
                          'lon': (['y', 'x'], local_lon),
                          'lat': (['y', 'x'], local_lat)
                      },
                      attrs=raw_da.attrs
                      )

    # indicate the timezone by global attribute
    da = da.assign_attrs({'timezone': 'UTC'})

    if save:
        # save it to NetCDF file with the lon and lat (2D).
        output_name = f'{Path(raw_nc).stem:s}.lonlat.nc'
        input_dir = os.path.split(raw_nc)[0]

        # output to the same dir:
        da.to_netcdf(f'{input_dir:s}/{output_name:s}')
        print(f'saved to {input_dir:s}/{output_name:s}')

    return da


@hydra.main(config_path="configs", config_name="scale_interaction")
def data_process(cfg: DictConfig) -> None:
    """
    put data process here and
    put data loading functions above for further use
    """

    if cfg.job.data.add_coords_to_raw_nc:
        print('good')

    print(f'done')


if __name__ == "__main__":
    sys.exit(data_process())
