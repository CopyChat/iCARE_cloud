"""
to find the physical link between the SSR classification and the large-scale variability
over la reunion island and it's extended area
"""

__version__ = f'Version 2.0  \nTime-stamp: <2021-05-15>'
__author__ = "ChaoTANG@univ-reunion.fr"

import sys
import glob
import hydra
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
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

                # list_file: list = glob.glob(f'{cfg.dir.icare_data_ccur:s}/ct.*Z.nc')
                list_file: list = glob.glob(f'/gpfs/scratch/le2p/OBS_DATA/icare/ctang/ct.*Z.nc')

                # resort by DateTime in the name file
                list_file.sort()

                # -------------------- test local MacBook ------------------------

                # when develop or debug:
                # use the ct_conditions file for local test, since it has the land-sea diff.
                # list_file: list = sorted(glob.glob(f'{cfg.dir.icare_data_local:}/ct_conditions.*Z.nc'))
                # raw_nc_file = f'./local_data/icare_dir_ccur/
                # ct_conditions.S_NWC_CT_MSG1_globeI-VISIR_20190101T000000Z.nc'

                # when testing code with multi files locally:
                # read a list_file to test locally:
                # list_file: list = sorted(glob.glob(f'{cfg.dir.icare_data_local:}/ct.*Z.nc'))

                # -------------------- test local MacBook ------------------------

                for raw_file in list_file:
                    print(raw_file)
                    output_file = f'{Path(raw_file).stem:s}.lonlat.nc'
                    output_path = f'{cfg.dir.icare_data_ccur:s}/{output_file:s}'
                    output_list = glob.glob(output_path)

                    if len(output_list):
                        print(f'this is done: {output_file:s}')
                    else:
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

            for year in [2017, 2018, 2019, 2020, 2021, 2022]:
                path = f'/gpfs/scratch/le2p/OBS_DATA/icare/ctang/{str(year):s}'
                list_lonlat_file: list = glob.glob(f'{path:s}/ct.*_{str(year):s}*T*Z.lonlat.nc')

                # resort by DateTime in the name file
                list_lonlat_file.sort()

                for raw_file in list_lonlat_file:
                    print(raw_file)
                    # to skip processed file:
                    output_file = f'{Path(raw_file).stem:s}.reu.nc'
                    output_path = f'{path:s}/{output_file:s}'
                    output_list = glob.glob(output_path)

                    if len(output_list):
                        print(f'this is done: {output_file:s}')
                    else:
                        DATA.select_area_by_lon_lat_2D_dim(raw_nc_file=raw_file, var='ct',
                                                           box=reu_box, area='reu', save=True)

                # after selection the Reunion domain still in general projection.
                # see plots of latitude and longitude in ./plot

                # merge all reu file
                list_reu_file: list = glob.glob(f'{path:s}/'
                                                f'ct.*_????????T*Z.lonlat.reu.nc')

                # lat become to 31 values from 30, since this file:
                # ct.S_NWC_CT_MSG1_globeI-VISIR_20180911T110000Z.lonlat.reu.nc

                list_reu_file.sort()
                GEO_PLOT.nc_mergetime(list_reu_file, 'ct', output_tag='yearly')
                # this file is saved on CCuR as: ct.S_NWC_CT_MSG1_globeI-VISIR_20190101T000000Z.lonlat.reu.yearly.nc

        if cfg.job.data.merge_reu:
            # download "yearly" file from CCuR, then merge them:
            # file after selecting reu on CCuR, got these in local_data/reu_ccur:

            # group 1:
            a = f'{cfg.dir.local_data:s}/reu_ccur/ct.S_NWC_CT_MSG1_globeI-VISIR_20170601T080000Z.lonlat.reu.yearly.nc'
            # 20170601 - 20180911, 34*30 (x*y) grid

            # group 2:
            b = f'{cfg.dir.local_data:s}/reu_ccur/ct.S_NWC_CT_MSG1_globeI-VISIR_20180911T110000Z.lonlat.reu.yearly.nc'
            # 20180911 - 20181231, 34*31 grid
            c = f'{cfg.dir.local_data:s}/reu_ccur/ct.S_NWC_CT_MSG1_globeI-VISIR_20190101T000000Z.lonlat.reu.yearly.nc'
            # 20190101-20191231, 34*31 grid, lon/lat same with b
            d = f'{cfg.dir.local_data:s}/reu_ccur/ct.S_NWC_CT_MSG1_globeI-VISIR_20200101T000000Z.lonlat.reu.yearly.nc'
            # 20200101 - 20200630, 34*31 grid, lon/lat same with c

            # group 3:
            e = f'{cfg.dir.local_data:s}/reu_ccur/ct.S_NWC_CT_MSG1_globeI-VISIR_20200701T000000Z.lonlat.reu.yearly.nc'
            # 20200701-20201231, 34*31 grid, lon/lat diff from file above, i.e. df, dif ~ 0.08 < reso = 0.03
            f = f'{cfg.dir.local_data:s}/reu_ccur/ct.S_NWC_CT_MSG1_globeI-VISIR_20210101T000000Z.lonlat.reu.yearly.nc'
            # 20210101-20211231, 34*31 grid, lon/lat same as above, ef.
            g = f'{cfg.dir.local_data:s}/reu_ccur/ct.S_NWC_CT_MSG1_globeI-VISIR_20220101T000000Z.lonlat.reu.yearly.nc'
            # 20220101-20220623, 34*31 grid, lon/lat same as above, ef.

            gp1 = GEO_PLOT.read_to_standard_da(a, 'ct')
            gp2 = GEO_PLOT.nc_mergetime(list_file=[b, c, d], var='ct', output_tag='mergetime', save=False)
            gp3 = GEO_PLOT.nc_mergetime(list_file=[e, f, g], var='ct', output_tag='mergetime', save=False)

            # merge 1: gp4 = gp2 + gp3, using coords from gp3:

            # check if da1819 and da2122 has similar coords: << 0.5 * resolution
            reso = 0.03

            lon_max = np.abs((gp2.lon - gp3.lon).max())
            lat_max = np.abs((gp2.lat - gp3.lat).max())
            print(lon_max, lat_max)

            if np.logical_and(lon_max < reso, lat_max < reso):
                new_coords_param = {
                    "time": gp2.time, "lat": (['y', 'x'], gp3.lat.values), "lon": (['y', 'x'], gp3.lon.values)}
                new_gp2 = xr.DataArray(gp2.data, dims=list(gp3.dims), coords=new_coords_param, name=gp3.name,
                                       attrs=gp3.attrs)

            # merge gp4:
            gp4 = xr.concat([new_gp2, gp3], dim='time')

            # merge: gp5 = gp1 + gp4

            # gp1 has less in lat, so select less lat from gp4  as new_gp4

            # check lat/lon:
            dif_max_lat = np.abs((gp4[:, 1:, :].lat - gp1.lat)).max()
            dif_max_lon = np.abs((gp4[:, 1:, :].lon - gp1.lon)).max()

            if np.logical_and(dif_max_lat < reso, dif_max_lon < reso):
                new_gp4 = gp4[:, 1:, :]

                # then give gp1 the coords of new_gp4, as new_gp1
                new_coords_param = {
                    "time": gp1.time,
                    "lat": (['y', 'x'], new_gp4.lat.values),
                    "lon": (['y', 'x'], new_gp4.lon.values)}

                new_gp1 = xr.DataArray(gp1.data, dims=list(new_gp4.dims), coords=new_coords_param,
                                       name=new_gp4.name, attrs=new_gp4.attrs)

                # merge:
                gp5 = xr.concat([new_gp1, new_gp4], dim='time')
                gp5 = gp5.assign_attrs({'units': 'unitless'})

                # shift time
                gp5_local = GEO_PLOT.convert_da_shifttime(gp5, 3600 * 4)

                # save it to dataset
                gp5_local.to_netcdf(cfg.file.reu_localtime_2017_2022)

            print(f'done')

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

        if cfg.job.data.missing_reu:
            # read nc in UTC00
            reu_da = GEO_PLOT.read_to_standard_da(cfg.file.reu_localtime_2017_2022, 'ct')

            # remove maps with only nan values
            reu_da_nan_maps = reu_da.where(np.isnan(reu_da).all(dim={'x', 'y'}), drop=True)
            if len(reu_da_nan_maps):
                print(f'{len(reu_da_nan_maps):g} maps are found with only nan @:', reu_da_nan_maps.time.values)
                reu_da = reu_da.where(np.invert(np.isnan(reu_da).all(dim={'x', 'y'})), drop=True)
                # save it:
                reu_da.to_netcdf(cfg.file.reu_nc)

            # check missing for each year
            freq = '15min'
            start = '2017-06-01 12:00'
            end = '2022-06-23 11:30'

            mon_hour_matrix = GEO_PLOT.check_missing_da_df(
                start=start, end=end, freq=freq,
                data=reu_da, plot=True)

        if cfg.job.data.select_moufia:
            # read utc reu nc:
            reu = GEO_PLOT.read_to_standard_da(cfg.file.reu_localtime_2017_2022, 'ct')

            Project_cloud.test_plot_reu_grid(reu)

            moufia_raw: xr.DataArray = GEO_PLOT.select_pixel_da(da=reu, lon=55.45, lat=-21.0, n_pixel=1)

            new_da = xr.DataArray(data=moufia_raw.data, dims=('time',),
                                  coords={'time': moufia_raw.time}, name='ct')
            new_da = new_da.assign_attrs({'units': '', 'long_name': 'cloud_type'})
            new_da.to_netcdf(cfg.file.moufia_nc)  # UTC not local time

            df_local = new_da.to_dataframe()
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

            reu = GEO_PLOT.read_to_standard_da(cfg.file.reu_localtime_2017_2022, 'ct')

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
                                                          title=f'ct 201706 - 202206, 8 moufia nearby pixels, '
                                                                f'when center = 10, @15min',
                                                          output_tag=f'8 pixels around moufia')

            # ------------------------------------------ do the reallocation

            # make a loop
            reallocated = []  # reallocated moufia pixel CT:
            all_9p_frac_cloud = []  # index where all pixels are 10

            # use data before regroup
            moufia_reallocated = moufia_raw.copy()  # initialize
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

            # remove snow over land, since wrong detections, since moufia nearly never has snow. while 83 found
            da1 = da1[da1 != 3].dropna()

            # make #11-15 to #11 as high semitransparent cloud
            da1[da1 >= 11] = 11

            # only: #1 clearsky, #5 very-low, #6 low, #7 Mid-level #8 High Opaque,
            # #9 Very-high opaque, #10 fractional #11 high semitransparent cloud

            da1.to_pickle(cfg.file.moufia_reallocation_regroup)  # still local time

        if cfg.job.moufia.statistics:
            # load data for analysis:
            df = pd.read_pickle(cfg.file.moufia_reallocation_regroup)

            Project_cloud.plot_monthly_hourly_bar_unstack(df=df,
                                                          title=f'moufia after reallocation regroup',
                                                          output_tag=f'moufia_reallocated_regroup')

            # plot all cloud types without clearsky:
            df_cld = df[df != 1].dropna()

            Project_cloud.plot_monthly_hourly_bar_unstack(df=df_cld, stack_full=True,
                                                          title=f'moufia after reallocation regroup 201706-202206',
                                                          output_tag=f'moufia_reallocated_regroup_only_cloudy')

            # statistics:
            raw = pd.read_pickle(cfg.file.moufia_local_time)
            reallocated = pd.read_pickle(cfg.file.moufia_reallocation)
            regrouped = pd.read_pickle(cfg.file.moufia_reallocation_regroup)

            size = len(raw)
            for ct in range(1, 16):
                print(
                    f'{ct:g}, {raw[raw == ct].dropna().size:g},'
                    f'{raw[raw == ct].dropna().size * 100 / size:4.2f},'
                    f'{reallocated[reallocated == ct].dropna().size:g},'
                    f'{reallocated[reallocated == ct].dropna().size * 100 / size:4.2f},'
                    f'{regrouped[regrouped == ct].dropna().size:g},'
                    f'{regrouped[regrouped == ct].dropna().size * 100 / size:4.2f}')

        if any(GEO_PLOT.get_values_multilevel_dict(dict(cfg.job.moufia.correlations))):

            df = pd.read_pickle(cfg.file.moufia_reallocation_regroup)

            if cfg.job.moufia.correlations.mean_annual_cycle:
                # mean SSR annual cycle:
                rg = GEO_PLOT.read_csv_into_df_with_header(cfg.file.gillot_rg_mf_2019)[{'GLO'}] * 10000 / 3600
                # unit of mf is J/m2 (accumulated in 1 hour)

                # rg = rg[~rg.index.duplicated(keep='first')]
                # keyword: remove duplicated

                # data complete:
                mon_hour_matrix = GEO_PLOT.check_missing_da_df(start='2019-01-01 00:00', end='2019-12-31 23:00',
                                                               freq='60min', data=rg, plot=True)

                ssr_day_night_monmean = rg.groupby(rg.index.month).mean()
                # correlation matrix:
                # df with all necessary columns in 12 months or 24 hours

                ct_annual = Project_cloud.annual_cycle_cloudiness(df, '201706-202206')
                cld_ssr_monmean = pd.concat([ct_annual, ssr_day_night_monmean], axis=1)

                # pearson:
                cor = cld_ssr_monmean.corr(method='pearson')

                # plot:
                fig = plt.figure(figsize=(10, 10), dpi=300)
                ax = plt.subplot()
                GEO_PLOT.plot_color_matrix(df=cor, cmap=plt.cm.get_cmap('PiYG').reversed(), plot_number=True, ax=ax,
                                           vmin=-1, vmax=1,
                                           cbar_label='jj')
                plt.savefig(f'./plot/annual_ct_ssr_cross_corr.png', dpi=300)
                plt.show()


if __name__ == "__main__":
    sys.exit(cloud())
