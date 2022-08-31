"""
to analyis cloud type classification from SAFNWC
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

import GEO_PLOT


def test_plot_reu_grid(da):
    # plot reu grid:
    lat = da.lat.values
    lon = da.lon.values

    for i in range(lat.shape[0]):
        for j in range(lat.shape[1]):
            plt.plot(lon[i, j], lat[i, j], marker='o', markersize=1)
            print(lon[i, j], lat[i, j])

    min_lat_dif = lat[0, 0] - lat[1, 0]
    max_lat_dif = lat[-1, -1] - lat[-2, -1]

    min_lon_dif = lon[0, 0] - lon[0, 1]
    max_lon_dif = lon[-1, -1] - lon[-1, -2]

    print(f'min grid lat: {min_lon_dif: 4.4f}, {min_lat_dif:4.4f}\n'
          f'max grid lat: {max_lon_dif: 4.4f}, {max_lat_dif:4.4f}')

    plt.title(f'lon and lat in Reunion S_NWC')

    plt.grid()

    plt.show()


def diurnal_cycle_cloudiness(df: pd.DataFrame, year: str = '2019'):

    # annual cycle of all CTs:
    stack = df.groupby([df.index.hour, 'ct']).size().unstack()
    ct_diurnal = stack.apply(lambda x: x * 100 / np.sum(x), axis=1)

    # total cloudiness with the high semi-transparent clouds, i.e., cirrus

    total_cld = df.loc[df['ct'] > 1].dropna()
    total_cld_monmean = total_cld.groupby(total_cld.index.hour).size().to_frame('total_cld')
    cf_total = total_cld_monmean * 100 / df.groupby(df.index.hour).size().to_frame('total_cld')

    # no cirrus:
    total_cld_0_cirrus = df.loc[(df['ct'] < 11) & (df['ct'] > 1)]
    total_cld_0_cirrus_monmean = total_cld_0_cirrus.groupby(total_cld_0_cirrus.index.hour).size().to_frame(
        'total_cld_no_cirrus')
    cf_total_0_cirrus = total_cld_0_cirrus_monmean * 100 / df.groupby(df.index.hour).size().to_frame('total_cld_no_cirrus')

    output = pd.concat([ct_diurnal, cf_total, cf_total_0_cirrus], axis=1)
    output = output.rename(columns={1: 'clearsky', 5: 'vLow', 6: 'Low', 7: 'Med',
                                    8: 'HOp', 9: 'vHOp', 11: 'sTp'})
    # plot annual:
    fig = plt.figure(figsize=(12, 8), dpi=200)
    for tcl, label in zip([output['total_cld'], output['total_cld_no_cirrus']],
                          ['total_cloudiness', 'total_cloudiness_without_cirrus']):
        plt.plot(tcl, label=label, linewidth=2, marker='o')

    fontsize = 16
    plt.legend(fontsize=fontsize)
    plt.xlabel(f'hour', fontsize=fontsize)
    plt.ylabel(f'frequency', fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.title(f'total cloudiness', fontsize=fontsize)
    plt.grid()
    plt.savefig(f'./plot/diurnal.total_cloudiness.moufia.{year:s}.png', dpi=300)
    plt.show()

    return output


def annual_cycle_cloudiness(df: pd.DataFrame, year: str = '2019'):

    # annual cycle of all CTs:
    stack = df.groupby([df.index.month, 'ct']).size().unstack()
    ct_annual = stack.apply(lambda x: x * 100 / np.sum(x), axis=1)

    # total cloudiness with the high semi-transparent clouds, i.e., cirrus

    total_cld = df.loc[df['ct'] > 1].dropna()
    total_cld_monmean = total_cld.groupby(total_cld.index.month).size().to_frame('clt')
    cf_total = total_cld_monmean * 100 / df.groupby(df.index.month).size().to_frame('clt')

    # no cirrus:
    total_cld_0_cirrus = df.loc[(df['ct'] < 11) & (df['ct'] > 1)]
    total_cld_0_cirrus_monmean = total_cld_0_cirrus.groupby(total_cld_0_cirrus.index.month).size().to_frame(
        'clt_no_cirrus')
    cf_total_0_cirrus = total_cld_0_cirrus_monmean * 100 / df.groupby(df.index.month).size().to_frame('clt_no_cirrus')

    output = pd.concat([ct_annual, cf_total, cf_total_0_cirrus], axis=1)
    output = output.rename(columns={1: 'clearsky', 5: 'vLow', 6: 'Low', 7: 'Med',
                                    8: 'HOp', 9: 'vHOp', 11: 'sTp'})
    # plot annual:
    fig = plt.figure(figsize=(12, 8), dpi=200)
    for tcl, label in zip([output['clt'], output['clt_no_cirrus']],
                          ['total_cloudiness', 'total_cloudiness_without_cirrus']):
        plt.plot(tcl, label=label, linewidth=2, marker='o')

    fontsize = 16
    plt.legend(fontsize=fontsize)
    plt.xlabel(f'month', fontsize=fontsize)
    plt.ylabel(f'frequency', fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.title(f'total cloudiness', fontsize=fontsize)
    plt.grid()
    plt.savefig(f'./plot/annual.total_cloudiness.moufia.{year:s}.png', dpi=300)
    plt.show()

    # return only annual cycle data
    return output


def plot_monthly_hourly_bar_unstack(df, output_tag='jjj', title='kkk', stack_full: bool = False):
    stacked = df.groupby(
        [df.index.get_level_values(0).month, 'ct']).size().unstack()

    y_label = 'occurrence'

    if stack_full:
        stacked = stacked.apply(lambda x: x * 100 / np.sum(x), axis=1)
        print(stacked)
        y_label = f'frequency (%)'

    stacked.plot(kind='bar', stacked=True, legend=True)

    plt.xlabel('month (2019)')
    plt.ylabel(y_label)
    plt.xlim(-1, 14)
    plt.title(title)
    plt.savefig(f'./plot/monthly_{output_tag:s}.full_{stack_full:g}.png', dpi=300)

    plt.show()

    # hourly:
    stacked = df.groupby([df.index.get_level_values(0).hour, 'ct']).size().unstack()

    if stack_full:
        stacked = stacked.apply(lambda x: x * 100 / np.sum(x), axis=1)
        print(stacked)
        y_label = f'frequency (%)'

    stacked.plot(kind='bar', stacked=True, legend=True)
    plt.xlabel('Hour (2019)')
    plt.ylabel(y_label)
    plt.xlim(-1, 30)
    plt.title(title)
    plt.savefig(f'./plot/hourly{output_tag:s}.full_{stack_full:g}.png', dpi=300)
    plt.show()
