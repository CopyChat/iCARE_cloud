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
import Project_cloud


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
            # this file is saved on CCuR as: ct.S_NWC_CT_MSG1_globeI-VISIR_20190101T000000Z.lonlat.reu.yearly.nc

        if cfg.job.data.missing_reu:
            # read nc in UTC00
            reu_da = GEO_PLOT.read_to_standard_da(cfg.file.reu_nc, 'ct')

            # remove maps with only nan values
            reu_da_nan_maps = reu_da.where(np.isnan(reu_da).all(dim={'x', 'y'}), drop=True)
            if len(reu_da_nan_maps):
                print(f'{len(reu_da_nan_maps):g} maps are found with only nan @:', reu_da_nan_maps.time.values)
                reu_da = reu_da.where(np.invert(np.isnan(reu_da).all(dim={'x', 'y'})), drop=True)
                # save it:
                reu_da.to_netcdf(cfg.file.reu_nc)

            # save local time file:
            reu_da = GEO_PLOT.read_to_standard_da(cfg.file.reu_nc, 'ct')
            reu_da_local_time = GEO_PLOT.convert_da_shifttime(da=reu_da, second=3600 * 4)
            reu_da_local_time.to_netcdf(cfg.file.reu_local_time_nc)

            # check missing for each year
            freq = '15min'
            start = '2019-01-01 00:00'
            end = '2019-12-31 23:45'

            mon_hour_matrix = GEO_PLOT.check_missing_da(
                start=start, end=end, freq=freq,
                da=reu_da, plot=True)
            print(mon_hour_matrix)

        if cfg.job.data.select_moufia:
            # read utc reu nc:
            reu = GEO_PLOT.read_to_standard_da(cfg.file.reu_nc, 'ct')

            moufia_raw: xr.DataArray = GEO_PLOT.select_pixel_da(da=reu, lon=55.45, lat=-21.0, n_pixel=1)

            new_da = xr.DataArray(data=moufia_raw.data, dims=('time',),
                                  coords={'time': moufia_raw.time}, name='ct')
            new_da = new_da.assign_attrs({'units': '', 'long_name': 'cloud_type'})
            new_da.to_netcdf(cfg.file.moufia_nc)  # UTC not local time

            df_utc = new_da.to_dataframe()
            df_local = GEO_PLOT.convert_df_shifttime(df_utc, 3600 * 4)
            df_local.to_pickle(cfg.file.moufia_local_time)

    # ==================================================================== moufia

    if any(GEO_PLOT.get_values_multilevel_dict(dict(cfg.job.moufia))):

        if cfg.job.moufia.reallocation:
            #  Reallocated pixels covered by fractional clouds, i.e., sub-pixel water clouds.
            #  These pixels were reprocessed and reallocated so that they fall into the cloud type
            #  most frequently observed among the 8 neighbouring pixels.

            # ----------------------------------------- data

            # local time data:
            moufia_raw = pd.read_pickle(cfg.file.moufia_local_time)

            reu = GEO_PLOT.read_to_standard_da(cfg.file.reu_local_time_nc, 'ct')

            # select moufia with the neighbour 8 pixels:
            moufia_9p = GEO_PLOT.select_pixel_da(da=reu, lon=55.45, lat=-21.0, n_pixel=9)

            # ----------------------------------------- statistics
            # reallocation:
            count = pd.DataFrame(moufia_raw.value_counts()).sort_index()
            print(f'{count.loc[[10.0]].values.ravel()[0]:g} time steps with fraction cloud in Moufia pixel')
            # tag: selecting groupby index DataFrame

            # 9 pixels with central one == 10:
            frac_cld_9p = moufia_9p.sel(time=moufia_raw[moufia_raw == 10].dropna().index)
            # tag: selecting DataArray by index from DataFrame: fraction cloud at Moufia

            # make the center moufia pixel nan:
            frac_cld_9p[:, 1, 1] = np.nan

            # remove all fraction cloud pixels, ct==10, from the 8 neighbours
            frac_cld_9p_no10 = frac_cld_9p.where(frac_cld_9p != 10)

            # ------------------------------------------ plot:
            frac_cld_df = frac_cld_9p.to_dataframe()

            # see the spatial concurrency: monthly
            Project_cloud.plot_monthly_hourly_bar_unstack(df=frac_cld_df,
                                                          title=f'ct in 2019, 8 moufia nearby pixels, '
                                                                f'when center = 10, @15min',
                                                          output_tag=f'8 pixels around moufia')

            # ------------------------------------------ do the reallocation

            # make a loop
            reallocated = []     # reallocated moufia pixel CT:
            all_9p_frac_cloud = []   # index where all pixels are 10

            # use data before regroup
            moufia_reallocated = moufia_raw.copy()     # initialize
            for i in range(len(frac_cld_9p_no10)):
                # just for save and check
                if np.isnan(frac_cld_9p_no10[i, 1, 1]):
                    data = frac_cld_9p_no10[i].data.ravel()
                    # int, and remove nan
                    data_na = np.int32(data[~np.isnan(data)])

                    # if all pixels are fraction cloud:
                    if len(data_na) == 0:
                        all_9p_frac_cloud.append(i)
                        # use the value 1 timestep before:
                        reallocated.append(reallocated[-1])
                    else:
                        dominate = np.bincount(data_na)
                        reallocated.append(dominate.argmax())
                        # print(i, len(data_na), data_na, dominate)

                # write reallocated value to moufia:
                moufia_reallocated.loc[frac_cld_9p_no10[i].time.values] = reallocated[i]

            reallocated_df = moufia_reallocated.loc[frac_cld_9p_no10.time.values]

            print(moufia_raw[moufia_raw==10].dropna().size, 1)
            Project_cloud.plot_monthly_hourly_bar_unstack(df=reallocated_df,
                                                          title=f'after reallocation fractional cloud day only',
                                                          output_tag=f'after_reallocation_moufia')

            Project_cloud.plot_monthly_hourly_bar_unstack(df=moufia_raw[moufia_raw == 10].dropna(),
                                                          title=f'before reallocation fractional cloud day only',
                                                          output_tag=f'before_reallocation_moufia')

            # save:
            moufia_reallocated.to_pickle(cfg.file.moufia_reallocation)

            Project_cloud.plot_monthly_hourly_bar_unstack(df=moufia_reallocated,
                                                          title=f'after reallocation fractional cloud #10',
                                                          output_tag=f'after_reallocation_moufia')

            Project_cloud.plot_monthly_hourly_bar_unstack(df=moufia_raw,
                                                          title=f'before reallocation fractional cloud #10',
                                                          output_tag=f'before_reallocation_moufia')

        if cfg.job.moufia.regroup:
            # regroup the cloud types:
            # using reallocated data:
            moufia_reallocated = pd.read_pickle(cfg.file.moufia_reallocation)

            # remove the #2 cloud-free sea:
            da1 = moufia_reallocated[moufia_reallocated != 2].dropna()
            print(f'cloud free sea = {len(moufia_reallocated[moufia_reallocated == 2].dropna()):g} days')
            print(f'snow over land = {len(moufia_reallocated[moufia_reallocated == 3].dropna()):g} days')

            # remove snow over land, since wrong detections, since moufia nearly never has snow.
            da1 = da1[da1 != 3].dropna()

            # make #11-15 to #11 as high semitransparent cloud
            da1[da1 >= 11] = 11

            # only: #1 clearsky, #5 very-low, #6 low, #7 Mid-level #8 High Opaque,
            # #9 Very-high opaque, #10 fractional #11 high semitransparent cloud

            da1.to_pickle(cfg.file.moufia_reallocation_regroup)  # still local time

            # make some statistics before reallocation fractional could to its dominate neighbours
            moufia_regroup = pd.read_pickle(cfg.file.moufia_reallocation_regroup)
            Project_cloud.plot_monthly_hourly_bar_unstack(df=moufia_regroup,
                                                          title=f'ct in 2019, moufia pixel after reallocation @15min',
                                                          output_tag=f'reallocation regroup pixel at moufia')

        if any(GEO_PLOT.get_values_multilevel_dict(dict(cfg.job.moufia.statistics))):
            # load data for analysis:
            df = pd.read_pickle(cfg.file.moufia_reallocation_regroup)

            if cfg.job.moufia.statistics.temporal:
                df19 = df[df.index.year == 2019]

                Project_cloud.plot_monthly_hourly_bar_unstack(df=df19,
                                                              title=f'moufia after reallocation regroup',
                                                              output_tag=f'moufia_reallocated_regroup')
            # statistics:
            raw = pd.read_pickle(cfg.file.moufia_local_time)
            reallocated = pd.read_pickle(cfg.file.moufia_reallocation)
            regrouped = pd.read_pickle(cfg.file.moufia_reallocation_regroup)

            size = len(raw)
            for ct in range(1, 16):
                print(f'{ct:g}, {raw[raw == ct].dropna().size:g} \t'
                      f'{reallocated[reallocated == ct].dropna().size:g} \t'
                      f'{regrouped[regrouped == ct].dropna().size:g}')


if __name__ == "__main__":
    sys.exit(cloud())
