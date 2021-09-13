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
from omegaconf import DictConfig
import GEO_PLOT
import MIALHE_2020


@hydra.main(config_path="configs", config_name="scale_interaction")
def interaction(cfg: DictConfig) -> None:
    """
    to find the physical link between the SSR classification and the large-scale variability
    over la reunion island
    """
    # ---------- clustering SARAH-E daily SSR (by Pauline Mialhe) -----------------------------
    ssr_cluster = GEO_PLOT.read_csv_into_df_with_header(cfg.input.ssr_clusters)

    if cfg.job.ssr.classification.monthly_distribution:
        MIALHE_2020.histogram_classification(ssr_cluster)
        # MIALHE_2020.matrix_classification_at_year_and_month(pclass_ssr)
        MIALHE_2020.table_classification_at_month(ssr_cluster)

        print(f'good')

    if cfg.job.ssr.cyclone_in_ssr_class:
        ssr_classif = ssr_cluster['C9']
        GEO_PLOT.plot_cyclone_in_classif(classif=ssr_classif,
                                         radius=3,
                                         suptitle_add_word='1981-2016 SSR clusters NDJF')
    if cfg.job.ssr.cyclone_property_ssr:
        cyc_df = GEO_PLOT.read_csv_into_df_with_header(cfg.input.cyclone_all)
        # todo: local time or UTC ? assuming local time to be confirmed.
        nearby_cyc: pd.DataFrame = GEO_PLOT.select_nearby_cyclone(
            cyc_df=cyc_df, lon_name='LON', lat_name='LAT', radius=3,
            cen_lat=-21.1, cen_lon=55.5)

        # nearby_cyc_index = nearby_cyc.index.tz_localize(None).sort_values()
        nearby_cyc['date'] = nearby_cyc.index.date
        # ssr_cluster_index = ssr_cluster.index.tz_localize(None)
        ssr_cluster['date'] = ssr_cluster.index.date
        #
        # merge_df = pd.merge_asof(nearby_cyc[['date', 'NOM_CYC', 'LON', 'LAT']],
        #                          ssr_cluster[['date', 'C9']], on='date')


        print(f'done')

    # ----------------------------- OLR regimes pattern class (Benjamin Pohl)-----------------------------
    if cfg.ttt.loading_ttt:
        olr_regime: pd.DataFrame = MIALHE_2020.read_ttr_classification(
            cfg.input.ttt_class_file, classif=cfg.param.ttt_classif)
        # days(NDJF, 29 Feb suppressed for leap yrs) x 39 seasons (1979-80 to 2017-18) x 10 members.

    if cfg.job.ttt.plot_ttt_regimes:
        print(f'loading')
        ttr_swio = GEO_PLOT.read_to_standard_da(f'{cfg.input.ttr_ens_file:s}', 'ttr')
        # In ERA - 5, the variable used to compute the clusters is called Top Net Thermal Radiation.It is given in J
        # / m2 so it needs to be multiplied by 10800, i.e.the nb of seconds between two analyses (3 hours),
        # to obtain W / m2.

        ttr = MIALHE_2020.prepare_ttr_data(ttr_swio)
        # pre-process of ensemble data
        olr = GEO_PLOT.convert_ttr_era5_2_olr(ttr=ttr.squeeze(drop=True), is_reanalysis=False)
        # change unit, etc
        GEO_PLOT.plot_ttt_regimes(olr_regimes=olr_regime, olr=olr, only_significant_points=0)

    if cfg.job.ttt.statistics:
        GEO_PLOT.plot_matrix_classification_at_year_and_month(class_df=olr_regime,
                                                              output_plot=cfg.output.ttt_class_monthly)

    if cfg.job.ttt.field_in_ttt.large_scale:
        print(f'loading ssr era5')
        ssr = GEO_PLOT.read_to_standard_da(cfg.input.ssr_era5, var='ssrd')
        ssr = GEO_PLOT.convert_unit_era5_flux(ssr, is_ensemble=False)
        ssr_anomaly = GEO_PLOT.anomaly_daily(ssr)

        GEO_PLOT.plot_field_in_classif(
            field=ssr_anomaly, classif=olr_regime, area='SA_swio',
            suptitle_add_word=f'era5, only_robust_class={cfg.param.remove_uncertain_days:g}',
            vmax=40, vmin=-40, plot_wind=False, bias=False, only_significant_points=False)

    if cfg.job.ttt.field_in_ttt.local_scale:
        print(f'loading ssr sarah_e')
        ssr = GEO_PLOT.read_to_standard_da(cfg.input.ssr_sarah_e, var='SIS')

        GEO_PLOT.plot_field_in_classif(
            field=ssr, classif=olr_regime, area='bigreu',
            suptitle_add_word=f'SARAH-E, only_robust_class={cfg.param.remove_uncertain_days:g}',
            vmax=40, vmin=-40, plot_wind=False, bias=False, only_significant_points=False)

    if cfg.job.ttt.ssr_olr_class_matrix:
        n_ssr_class = 'C9'
        ssr_class = ssr_cluster[[n_ssr_class]].rename(columns={n_ssr_class: 'SSR_cluster'})
        olr_class = olr_regime.rename(columns={'class': 'OLR_regime'})

        GEO_PLOT.plot_matrix_class_vs_class(class_x=olr_class, class_y=ssr_class,
                                            occurrence=1,
                                            suptitle_add_word=f'(N_SSR_class={n_ssr_class:s})',
                                            output_plot=f'plot/{n_ssr_class:s}_matrix_ssr_ttt.png')

    if cfg.job.ttt.temporal_correlation:
        print(f'loading ssr sarah_e')
        ssr_anomaly = GEO_PLOT.read_to_standard_da(cfg.input.ssr_sarah_e, var='SIS')
        season_reu_mean_ssr: np.ndarray = MIALHE_2020.get_spatial_mean_series_each_ttt_season(
            da=ssr_anomaly, season='NDJF', year_start=cfg.param.sarah_e_start_year,
            year_end=cfg.param.sarah_e_end_year, remove_29_feb=True)

        class_name = [5, 6, 7]

        print(f'class in each season')

        freq_df: pd.DataFrame = MIALHE_2020.get_class_occurrence_ttt_seasonal_series(
            class_name=class_name, ttt_classif=olr_regime, year_start=cfg.param.sarah_e_start_year,
            year_end=cfg.param.sarah_e_end_year)

        GEO_PLOT.plot_class_occurrence_and_anomaly_time_series(classif=freq_df, anomaly=season_reu_mean_ssr)

        print(f'good')

    if cfg.job.ttt.diurnal_cycle:

        # this is a test:
        # b = GEO_PLOT.read_to_standard_da(
        #     '/Users/ctang/Downloads/S_NWC_CMA_MSG1_globeI-VISIR_20200101T000000Z_4db7170ae2474f0462f76c12f3b136fc.nc',
        #     'ct')

        ssr = GEO_PLOT.read_to_standard_da(cfg.input.ssr_sarah_e_hour_reu, 'SIS')
        ssr = ssr.where(np.logical_or(ssr.time.dt.month >= 11, ssr.time.dt.month <= 2), drop=True)
        ssr = GEO_PLOT.convert_da_shifttime(ssr, second=4 * 3600)
        ssr = ssr.where(np.logical_and(ssr.time.dt.hour >= 8, ssr.time.dt.hour <= 17), drop=True)

        if cfg.param.plot_big_data_test:
            ssr = ssr.sel(time=slice('19990101', '20001201'))

        if cfg.job.ttt.diurnal_cycle.plot_diurnal_cycle_boxplot:
            ssr_spatial_mean = ssr.mean('lon', keep_attrs=True).mean('lat', keep_attrs=True)

            ssr_hour_anomaly = GEO_PLOT.anomaly_hourly(da=ssr_spatial_mean, percent=0)

            GEO_PLOT.plot_diurnal_boxplot_in_classif(
                classif=olr_regime, field_1D=ssr_hour_anomaly,
                anomaly=1, percent=0,
                suptitle_add_word='OLR bigreu sarah_e',
                plot_big_data_test=cfg.param.plot_big_data_test
            )

        if cfg.job.ttt.diurnal_cycle.plot_diurnal_cycle_map:
            ssr_hourly_anomaly = GEO_PLOT.anomaly_hourly(ssr)

            GEO_PLOT.plot_diurnal_cycle_field_in_classif(
                classif=olr_regime, field=ssr_hourly_anomaly,
                area='bigreu', vmax=80, vmin=-80,
                bias=True,
                only_significant_points=False,
                plot_wind=True,
                suptitle_add_word='sarah_e test run',
                plot_big_data_test=cfg.param.plot_big_data_test)

        print(f'dd')

    if cfg.job.ttt.cyclone_in_ttt:
        GEO_PLOT.plot_cyclone_in_classif(classif=olr_regime,
                                         radius=3,
                                         suptitle_add_word='1981-2016 OLR regimes NDJF'
                                         )



# #     mjo: pd.DataFrame = GEO_PLOT.read_mjo(match_ssr_avail_day=1)
# #     mjo: pd.DataFrame = GEO_PLOT.filter_by_season_name(data=mjo, season_name='austral_summer')
# #
# #     ttr_reu = xr.open_dataset(f'{WORKING_DIR:s}/local_data/era5/ttr.era5.1999-2016.day.reu.nc')['ttr']
# #     olr_reu = GEO_PLOT.convert_ttr_era5_2_olr(ttr=ttr_reu, is_reanalysis=1)
# #
# #     ssr_reu = xr.open_dataset(f'{WORKING_DIR:s}/data/sarah_e'
# #                          f'/SIS.sarah-e.1999-2016.hour.reu.anomaly.daytime.DJF.nc')['SIS']
# #
# #     MIALHE_2020.plot_diurnal_cycle_field_in_mjo_phase(mjo_phase=mjo, field=ssr_reu, var='SIS',
# #                                                       statistic='anomaly_mean', only_significant_points=1,
# #                                                       season='austral_summer', area='bigreu', plot_wind=0)
# #


#
# # ----------------------------- clustering SARAH-E daily SSR (Pauline Mialhe) -----------------------------
# # clusters = f'{WORKING_DIR:s}/data/classification/classif.csv'
# # ssr_class = MIALHE_2020.read_ssr_class(clusters)
#
# if test:
#     print('this is a test')
# # ----------------------------- monthly distribution of ssr class -----------------------------
# # if ttt_monthly_distribution:
# #
# #     MIALHE_2020.histogram_classification(olr_regimes)
# #     MIALHE_2020.matrix_classification_at_year_and_month(olr_regimes)
# #     MIALHE_2020.table_classification_at_month(olr_regimes)
# #
# # # ----------------------------- SSR field vs OLR patterns -----------------------------
# #
# # # ================================== SSR class vs OLR class ==================================
# #
# # if ssr_class_vs_olr_regime:
# #
# #     MIALHE_2020.classification_vs_classification(cls1=pclass_olr, cls2=pclass_ssr)
# #
# # # ==================================SSR class link with circulation ==================================
# #
# #
# # if plot_daily_mean_field_in_ttt_regimes:
# #
# #     mjo: pd.DataFrame = GEO_PLOT.read_mjo(match_ssr_avail_day=1)
# #
# #     w500_reu = xr.open_dataset(f'{WORKING_DIR:s}/data/mjo/w500.era5.1999-2016.daily.anomaly.reu.nc')['w']
# #     w500_sa_swio =
# xr.open_dataset(f'{WORKING_DIR:s}/data/mjo/w500.era5.1999-2016.daily.anomaly.sa-swio.nc')['w']
# #
# #     olr_reu = xr.open_dataset(f'{WORKING_DIR:s}/data/era5/ttr.era5.1999-2016.day.anomaly.nc.reu.nc')['ttr']
# #     olr_swio = xr.open_dataset(f'{WORKING_DIR:s}/data/era5/ttr.era5.1999-2016.day.anomaly.nc.swio.nc')['ttr']
# #     ssr_reu = xr.open_dataset(f'{WORKING_DIR:s}/data/sarah_e/SIS.sarah_e.daily.1999-2016.reu.anomaly.nc')['SIS']
# #
# #     for season in ["austral_summer", "winter", "all_year"]:
# #         # OLR
# #         MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=olr_swio, area='swio', season=season,
# #                                               only_significant_points=0, consistency=0)
# #         MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=olr_reu, area='bigreu',
# #                                               season=season, consistency=1)
# #
# #         # SSR
# #         MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=ssr_reu, area='bigreu',
# #         season=season, consistency=1)
# #         MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=ssr_reu, area='bigreu',
# #         season=season, consistency=0)
# #
# #         MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=olr_swio, area='SA_swio', season=season,
# #                                                  only_significant_points=1)
# #         MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=olr_swio,
# #               area='SA_swio', season=season, only_significant_points=1, consistency=1)
# #
# #         MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=olr_swio, area='SA_swio', season=season,
# #                                               percentage=1)
# #
# #
# #         # MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=w500_reu, area='reu', season=season)
# #         # MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=w500_reu, area='reu', season=season,
# #                   percentage=1)
# #         # MIALHE_2020.plot_fields_in_mjo_phases(
# mjo_phase=mjo, field=w500_sa_swio, area='SA_swio', season=season)
# #         # MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=w500_sa_swio, area='SA_swio',
# #                   season=season, percentage=1)
# #
# #     w500 = xr.open_dataset(f'{WORKING_DIR:s}/data/mjo/w500.era5.1999-2016.daily.anomaly.d01.nc')['w']
# #     MIALHE_2020.plot_fields_in_mjo_phases(mjo_phase=mjo, field=w500)
# #
#     print('good')
# #
# # if ttt_in_ssr_class:
# #
# #     mjo: pd.DataFrame = GEO_PLOT.read_mjo(match_ssr_avail_day=1)
# #
# #     mjo_dec_feb = mjo[(mjo.index.month == 1) |
# #                       (mjo.index.month == 12) |
# #                       (mjo.index.month == 2)]
# #
# #     mjo_may_jun = mjo[(mjo.index.month == 6) |
# #                       (mjo.index.month == 7) |
# #                       (mjo.index.month == 8)]
# #
# #     MIALHE_2020.plot_classification_vs_mjo(class_ssr=pclass_ssr, mjo=mjo_dec_feb, tag='DJF')
# #     MIALHE_2020.plot_classification_vs_mjo(class_ssr=pclass_ssr, mjo=mjo_may_jun, tag='JJA')
# #
# #     MIALHE_2020.plot_distribution_a_in_b(df_ab=mjo_and_ssr[{'ssr_class', 'phase', 'amplitude'}],
# #                                          column_a='phase', column_b='ssr_class')
# #
# # if ttt_monthly_distribution:
# #
# #     MIALHE_2020.plot_mjo_monthly_distribution(GEO_PLOT.read_mjo(match_ssr_avail_day=1))


if __name__ == "__main__":
    sys.exit(interaction())
