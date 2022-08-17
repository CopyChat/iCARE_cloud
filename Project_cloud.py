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


def plot_annual_diurnal_cloudiness(df: pd.DataFrame, year: str = '2019'):

    # total cloudiness with the high semi-transparent clouds, i.e., cirrus
    tcl_cirrus = df.copy()
    tcl_cirrus[tcl_cirrus > 1] = 999

    # no cirrus:
    tcl_0_cirrus = df.copy()
    tcl_0_cirrus[tcl_0_cirrus > 10] = 1
    tcl_0_cirrus[tcl_0_cirrus > 1] = 999

    # annual:
    fig = plt.figure(figsize=(12, 8), dpi=200)
    for tcl, label in zip([tcl_cirrus, tcl_0_cirrus], ['total_cloudiness', 'total_cloudiness_without cirrus']):
        stack = tcl.groupby([tcl.index.get_level_values(0).month, 'ct']).size().unstack()
        tcl_plot = stack.apply(lambda x: x * 100 / np.sum(x), axis=1)[[999]]
        plt.plot(tcl_plot, label=label, linewidth=2, marker='o')

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

    # diurnal:
    fig = plt.figure(figsize=(12, 8), dpi=200)
    for tcl, label in zip([tcl_cirrus, tcl_0_cirrus], ['total_cloudiness', 'total_cloudiness_without cirrus']):
        stack = tcl.groupby([tcl.index.get_level_values(0).hour, 'ct']).size().unstack()
        tcl_plot = stack.apply(lambda x: x * 100 / np.sum(x), axis=1)[[999]]
        plt.plot(tcl_plot, label=label, linewidth=2, marker='o')

    fontsize = 16
    plt.legend(fontsize=fontsize)
    plt.xlabel(f'Hour', fontsize=fontsize)
    plt.ylabel(f'frequency', fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.title(f'total cloudiness', fontsize=fontsize)
    plt.grid()
    plt.savefig(f'./plot/diurnal.total_cloudiness.moufia.{year:s}.png', dpi=300)
    plt.show()


def plot_monthly_hourly_bar_unstack(df, output_tag='jjj', title='kkk', stack_full: bool = False):

    stacked = df.groupby(
        [df.index.get_level_values(0).month, 'ct']).size().unstack()

    y_label = 'occurrence'

    if stack_full:
        stacked = stacked.apply(lambda x: x*100/np.sum(x), axis=1)
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
        stacked = stacked.apply(lambda x: x*100/np.sum(x), axis=1)
        print(stacked)
        y_label = f'frequency (%)'

    stacked.plot(kind='bar', stacked=True, legend=True)
    plt.xlabel('Hour (2019)')
    plt.ylabel(y_label)
    plt.xlim(-1, 30)
    plt.title(title)
    plt.savefig(f'./plot/hourly{output_tag:s}.full_{stack_full:g}.png', dpi=300)
    plt.show()
