# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 17:10:46 2017

@author: Karl Jan Clinckspoor
karl970@gmail.com karlclinckspoor@protonmail.com
Made at iNANO at Aarhus University
In a collaboration project with the University of Campinas.
Last modified: 01/09/2017
"""


import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

#%%
def subtract_water():
    experiments = []
    all_experiments = []
    count = 1
    while True:
        expnumber = input("What is the experimental number of run number %d?\n(quit to end program, enter nothing to continue): " % (count)) 
        if expnumber == '':
            break
        if expnumber.lower() == 'quit':
            sys.exit()
        if not expnumber.isdecimal():
            print('invalid experiment number: ', expnumber)
            continue
        expnumber = expnumber.zfill(5)
        if expnumber in experiments:
            print('You already selected this experiment!')
            continue
    
        files = glob.glob('*%s*'%expnumber)
        length = len(files)
        print('Found',length,'files for that experiment')
        if length == 0:
            print ('Oops. No experiment found. Do you want to select another? If not, the program will quit.')
            do_select = input ('Y/n: ')
            if do_select == 'Y':
                continue
            elif do_select != 'Y':
                sys.exit()
        if length > 1:
            selectedfile = input('More than one file was found. Which one to select? (number, beginning from 0)')
            try:
                all_experiments.append(files[selectedfile])
            except:
                print('Are you sure this was a correct command? Adding the first file.')
                all_experiments.append(files[0])
        elif length == 1:
            all_experiments.append(files[0])
        experiments.append(expnumber)
        count += 1
        
    pdas_allfiles = []
    for experiment in all_experiments:
        pdas_allfiles.append(pd.read_table(experiment,names=['q','int','err'],dtype=np.float64, header=0))
    water_file_number = input('What is the file number for water?')
    water_file_name = glob.glob('*%s*'%water_file_number)
    if water_file_name == []:
        print('No file found')
    print ('Found file(s): ', water_file_name)
    
    if len(water_file_name) > 1:
        selectedfile = input('More than one file was found. Which one to select? (number, beginning from 0)')
        try:
            water_file_pd = pd.read_table(water_file_name[int(selectedfile)],names=['q','int','err'],dtype=np.float64, header=0)
        except:
            print('Could this file file. Opening the first one')
            water_file_pd = pd.read_table(water_file_name[0],names=['q','int','err'],dtype=np.float64, header=0)
    
    elif len(water_file_name) == 1:
        water_file_pd = pd.read_table(water_file_name[0],names=['q','int','err'],dtype=np.float64, header=0)
        print('Successfully found')
#%%
    print('Subtracting')
#filename = input('What will the destination filename be?')
    want_to_plot = input('Do you want to show a plot of all subtracted curves? (Y/(n)) ')
    
    for file,name in zip(pdas_allfiles, all_experiments):
        file['int'] = file['int'] - water_file_pd['int']
        file['err'] = (file['err']**2+water_file_pd['err']**2)**(1/2)
        file.to_csv( (name[:-4]+'_minus_water.csv'),sep='\t', index=False)
        if want_to_plot == 'Y':
            plt.errorbar(file['q'],file['int'], yerr=file['err'])
        
    if want_to_plot == 'Y':
        plt.xscale('log')
        plt.yscale('log')
        plt.show()

print ('This script is to subtract water from SAXS scattering curves')
if __name__ == '__main__':
    while True:
        do_want = input('Do you want to subtract water from SAXS scattering curves? (y)/n\n')
        if do_want == 'n':
            break
        else:
            subtract_water()
    print('-'*10+'Done. Bye!'+'-'*10)
    
    