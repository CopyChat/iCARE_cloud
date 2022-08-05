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
import matplotlib.pyplot as plt
import xarray as xr
from omegaconf import DictConfig
from importlib import reload
import pandas as pd

import DATA
import GEO_PLOT
import subprocess


def renew():
    reload(GEO_PLOT)


@hydra.main(config_path="configs", config_name="cloud")
def cloud(cfg: DictConfig) -> None:
    """
    - to analysis iCARE cloud product
    - this project is connected to CCuR now

    attention: this code could be run by (python cloud.py) on CCuR in the right Python env
        is better to use disown -h % to make it run in background, the way of "()" doesn't work.

    """

    # calculate necessary data and save it for analysis:
    # ==================================================================== data:
    if any(GEO_PLOT.get_values_multilevel_dict(dict(cfg.job.data))):

        # -------------------------------------- SAF_NWC ---------------------
        if any(GEO_PLOT.get_values_multilevel_dict(dict(cfg.job.data.add_coords_to_raw))):
            # before all: prepare the raw data to be processed by this code
            # at least these two steps are obligate:
            # 1) move to target dir (this code is working on all files, filtering my name, in the dir)
            # 2) select a var, since this code can NOT process multivariables Dataset, and it's not necessary
            # * code is below:

            print(f'deal with SAF_NWC data ...')
            print(f'this code should be run in CCuR')

            if cfg.job.data.add_coords_to_raw.prepare_data_ccur:
                # get data ready for processing
                # to select a single variable
                subprocess.call(["./src/Data.sh"], shell=False)
                # attention: if module do not work, just run the code directly on CCuR.

            if cfg.job.data.add_coords_to_raw.add_coords_to_raw_nc:
                # add_coords_to_raw_nc:
                # this piece of code could be used to add coords information to the downloaded
                # non-coordinated raw netCDF files.

                # all files to be processed:
                # change the dir in config/cloud.yami if needed
                list_file: list = glob.glob(f'{cfg.dir.icare_data_ccur:s}/raw/ct.*Z.nc')

                # resort by DateTime in the name file
                list_file.sort()

                # -------------------- test local MacBook ------------------------

                # when develop or debug:
                # use the ct_conditions file for local test, since it has the land-sea diff.
                # list_file: list = sorted(glob.glob(f'{cfg.dir.icare_data_local:}/ct_conditions.*Z.nc'))
                # raw_nc_file = f'./local_data/icare_dir_ccur/ct_conditions.S_NWC_CT_MSG1_globeI-VISIR_20190101T000000Z.nc'

                # when testing code with multi files locally:
                # read a list_file to test locally:
                # list_file: list = sorted(glob.glob(f'{cfg.dir.icare_data_local:}/ct.*Z.nc'))

                # -------------------- test local MacBook ------------------------

                for raw_file in list_file:
                    print(raw_file)
                    DATA.add_lon_lat_to_raw_nc(
                        raw_nc_file=raw_file,
                        var='ct',
                        lon_file=cfg.file.icare_3km_lon_MSG0415,
                        lat_file=cfg.file.icare_3km_lat_MSG0415,
                        save=True
                    )
                    # return da just for test

        if cfg.job.data.select_reunion:
            # try to select reunion:
            # reu_box = GEO_PLOT.value_lonlatbox_from_area('reu')
            # or a smaller domain:
            reu_box = [55.05, 56, -21.55, -20.7]

            list_lonlat_file: list = glob.glob(f'{cfg.dir.icare_data_ccur:s}/raw/ct.*Z.lonlat.nc')

            # resort by DateTime in the name file
            list_lonlat_file.sort()

            for raw_file in list_lonlat_file:
                print(raw_file)
                DATA.select_area_by_lon_lat_2D_dim(raw_nc_file=raw_file, var='ct',
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
                    list_file: list = glob.glob(f'{cfg.dir.icare_data_ccur:s}/swio/'
                                                f'ct.*_2019{month:s}{day:s}T*Z.lonlat.nc')
                    list_file.sort()
                    GEO_PLOT.nc_mergetime(list_file, 'ct', output_tag='daily')

                # for swio (monthly):
                list_file: list = glob.glob(f'{cfg.dir.icare_data_ccur:s}/reu/'
                                            f'ct.*_2019{month:s}??T*Z.lonlat.swio.nc')
                list_file.sort()
                GEO_PLOT.nc_mergetime(list_file, 'ct', output_tag='monthly')

        if cfg.job.data.mergetime_reu:
            # for reu (yearly)
            list_file: list = glob.glob(f'{cfg.dir.icare_data_ccur:s}/reu/'
                                        f'ct.*_2019????T*Z.lonlat.reu.nc')
            list_file.sort()
            GEO_PLOT.nc_mergetime(list_file, 'ct', output_tag='year.ly')

        if cfg.job.data.missing_reu:

            reu_da = GEO_PLOT.read_to_standard_da(cfg.file.reu_nc, 'ct')

            # remove maps with only nan values
            reu_da_nan_maps = reu_da.where(np.isnan(reu_da).all(dim={'x', 'y'}), drop=True)
            if len(reu_da_nan_maps):
                print(f'{len(reu_da_nan_maps):g} maps are found with only nan @:', reu_da_nan_maps.time.values)
                reu_da = reu_da.where(np.invert(np.isnan(reu_da).all(dim={'x', 'y'})), drop=True)
                # save it:
                reu_da.to_netcdf(cfg.file.reu_nc)

            # check missing for each year
            freq = '15min'
            start = '2019-01-01 00:00'
            end = '2019-12-31 23:45'

            mon_hour_matrix = GEO_PLOT.check_missing_da(
                start=start, end=end, freq=freq,
                da=reu_da, plot=True)
            print(mon_hour_matrix)

        if cfg.job.data.select_moufia:
            reu = GEO_PLOT.read_to_standard_da(cfg.file.reu_nc, 'ct')

            moufia: xr.DataArray = GEO_PLOT.select_pixel_da(da=reu, lon=55.45, lat=-21.0, n_pixel=1)

            new_da = xr.DataArray(data=moufia.data, dims=('time',),
                                  coords={'time': moufia.time}, name='ct')
            new_da = new_da.assign_attrs({'units': '', 'long_name': 'cloud_type'})
            new_da.to_netcdf(cfg.file.moufia_nc)  # UTC not local time

            df_utc = new_da.to_dataframe()
            df_local = GEO_PLOT.convert_df_shifttime(df_utc, 3600 * 4)
            df_local.to_pickle(cfg.file.moufia_local_time)

    # ==================================================================== moufia

    if any(GEO_PLOT.get_values_multilevel_dict(dict(cfg.job.moufia))):
        # moufia in local time:
        moufia = pd.read_pickle(cfg.file.moufia_local_time)

        if cfg.job.moufia.regroup:
            # regroup the cloud types:

            # remove the #2 cloud-free sea:
            da1 = moufia[moufia != 2].dropna()
            print(f'cloud free sea = {len(moufia[moufia == 2].dropna()):g} days')
            print(f'snow over land = {len(moufia[moufia == 3].dropna()):g} days')

            # remove snow over land, since wrong detections, since moufia nearly never has snow.
            da1 = da1[da1 != 3].dropna()

            # make #11-15 to #11 as high semitransparent cloud
            da1[da1 >= 11] = 11

            # only: #1 clearsky, #5 very-low, #6 low, #7 Mid-level #8 High Opaque,
            # #9 Very-high opaque, #10 fractional #11 high semitransparent cloud

            da1.to_pickle(cfg.file.moufia_regroup)

        if any(GEO_PLOT.get_values_multilevel_dict(dict(cfg.job.moufia.statistics))):
            df = moufia
            df = pd.read_pickle(cfg.file.moufia_regroup)

            if cfg.job.moufia.statistics.monthly:

                df19 = df[df.index.year == 2019]
                # monthly:
                df19_count = df19.groupby([df19.index.month, 'ct']).size().unstack()

                df19_count.plot(kind='bar', stacked=False)
                df19_count.plot(kind='bar', stacked=True, legend=True)
                plt.xlabel('month (2019)')
                plt.ylabel('occurrence')
                plt.xlim(-1, 14)
                plt.savefig(cfg.file.ct_monthly_occurrence_plot, dpi=300)
                plt.show()

            if cfg.job.moufia.statistics.hourly:
                # hourly:
                df19_count = df19.groupby([df19.index.hour, 'ct']).size().unstack()
                df19_count.plot(kind='bar', stacked=True, legend=True)
                plt.xlabel('Hour (2019)')
                plt.ylabel('occurrence')
                plt.xlim(-1, 30)
                plt.savefig(cfg.file.ct_hourly_occurrence_plot, dpi=300)
                plt.show()



if __name__ == "__main__":
    sys.exit(cloud())
