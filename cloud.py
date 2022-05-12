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
import subprocess
from pathlib import Path


@hydra.main(config_path="configs", config_name="cloud")
def cloud(cfg: DictConfig) -> None:
    """
    - to analysis iCARE cloud product
    - this project is connected to CCuR now

    attention: this code could be run by (python cloud.py) on CCuR in the right Python env
        is better to use disown -h % to make it run in background, the way of "()" doesn't work.

    """

    print('starting ...')

    # before all: prepare the raw data to be processed by this code
    # at least these two steps are obligate:
    # 1) move to target dir (this code is working on all files, filtering my name, on the dir)
    # 2) select a var, since this code can NOT process multivariables Dataset, and it's not necessary
    # * code is below:

    if cfg.job.data.prepare_data_ccur:
        # get data ready for processing
        # to select a single variable
        subprocess.call(["./src/Data.sh"], shell=False)
        # attention: if module do not works, just run the code directly on CCuR.

    if cfg.job.data.add_coords_to_raw_nc:
        # this piece of code could be used to add coords information to the downloaded
        # non-coordinated raw netCDF files.

        # all files to be processed:
        # change the dir in config/cloud.yami if needed
        list_file: list = glob.glob(f'{cfg.dir.icare_data:s}/raw/ct.*Z.nc')

        # resort by DateTime in the name file
        list_file.sort()

        for raw_file in list_file:
            print(raw_file)
            da = DATA.add_lon_lat_to_raw_nc(raw_nc_file=raw_file, var='ct',
                                            lon=cfg.input.icare_3km_lon_MSG0415,
                                            lat=cfg.input.icare_3km_lat_MSG0415,
                                            save=True)
            # return da just for test

    if cfg.job.data.select_reunion:
        # try to select reunion:
        reu_box = GEO_PLOT.value_lonlatbox_from_area('reu')
        # or a smaller domain:
        reu_box = [55.12, 55.9, -21.5, -20.8]

        list_lonlat_file: list = glob.glob(f'{cfg.dir.icare_data:s}/ct.*Z.lonlat.nc')

        # resort by DateTime in the name file
        list_lonlat_file.sort()

        for raw_file in list_lonlat_file:
            print(raw_file)
            da = DATA.select_area_by_lon_lat_2D_dim(raw_nc_file=raw_file, var='ct',
                                                    box=reu_box, area='reu', save=True)

        # after selection the Reunion domain still in general projection.
        # see plots of latitude and longitude in ./plot

    if cfg.job.data.mergetime_swio:
        # since CDO mergetime function will lose the lon/lat by unknown reason,
        # I make a function in Python.

        # example file: ct.S_NWC_CT_MSG1_globeI-VISIR_20190610T030000Z.lonlat.nc
        for j in range(1, 13):
            month = str(j).zfill(2)
            print(f'merge in month {month:s}')

            # for swio (daily):
            for d in range(1, 32):
                day = str(d).zfill(2)
                print(f'merge in month {month:s}, day {day:s}...')
                list_file: list = glob.glob(f'{cfg.dir.icare_data:s}/swio/'
                                            f'ct.*_2019{month:s}{day:s}T*Z.lonlat.nc')
                list_file.sort()
                da = GEO_PLOT.nc_mergetime(list_file, 'ct', output_tag='daily')

            # for swio (monthly):
            list_file: list = glob.glob(f'{cfg.dir.icare_data:s}/reu/'
                                        f'ct.*_2019{month:s}??T*Z.lonlat.swio.nc')
            list_file.sort()
            da2 = GEO_PLOT.nc_mergetime(list_file, 'ct', output_tag='monthly')

    if cfg.job.data.mergetime_reu:

        # for reu (yearly)
        list_file: list = glob.glob(f'{cfg.dir.icare_data:s}/reu/'
                                    f'ct.*_2019????T*Z.lonlat.reu.nc')
        list_file.sort()
        da2 = GEO_PLOT.nc_mergetime(list_file, 'ct', output_tag='year.ly')

    print('done')


if __name__ == "__main__":
    sys.exit(cloud())
