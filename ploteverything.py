# Script to plot everything
import pandas as pd
import matplotlib.pyplot as plt
import glob

cut = glob.glob('*.cut')
fit = glob.glob('*.fit')
names = [file[:-4] for file in cut]

cut_pd = [pd.read_table(file,header=3, names = ['q', 'int', 'err', 'trash'], sep=' ') for file in cut]
fit_pd = [pd.read_table(file,header=3, names = ['q', 'int', 'err', 'trash'], sep=' ') for file in fit]

counter = 1
for cut_, fit_, name in zip(cut_pd, fit_pd, names):
    plt.xscale('log')
    plt.yscale('log')
    plt.plot(cut_['q'], cut_['int'], label='cut')
    plt.plot(fit_['q'], fit_['int'], label='fit')
    plt.legend()
    plt.title(name)
    plt.savefig(name+'.png')
    counter += 1
    plt.clf()