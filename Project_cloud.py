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


def plot_monthly_hourly_bar_unstack(df, output_tag='jjj', title='kkk'):

    moufia_9p_count = df.groupby(
        [df.index.get_level_values(0).month, 'ct']).size().unstack()

    moufia_9p_count.plot(kind='bar', stacked=False)
    moufia_9p_count.plot(kind='bar', stacked=True, legend=True)
    plt.xlabel('month (2019)')
    plt.ylabel('occurrence')
    plt.xlim(-1, 14)
    plt.title(title)
    plt.savefig(f'./plot/monthly_{output_tag:s}', dpi=300)

    plt.show()

    # hourly:
    moufia_9p_count = df.groupby([df.index.get_level_values(0).hour, 'ct']).size().unstack()

    moufia_9p_count.plot(kind='bar', stacked=True, legend=True)
    plt.xlabel('Hour (2019)')
    plt.ylabel('occurrence')
    plt.xlim(-1, 30)
    plt.title(title)
    plt.savefig(f'./plot/hourly_{output_tag:s}', dpi=300)
    plt.show()
