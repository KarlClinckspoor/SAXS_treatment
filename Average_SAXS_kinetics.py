# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 09:12:11 2017

@author: Karl Jan Clinckspoor
karl970@gmail.com karlclinckspoor@protonmail.com
Made at iNANO at Aarhus University
In a collaboration project with the University of Campinas.
Last date of modification: 30/08/2017
"""

import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#==============================================================================
# Todo:
#       Deal with experiments with different lengths
#		Check the precise number to obtain the necessary error bar (n or n-1?)
#==============================================================================
    
#%%
print ('This script is to average several kinetic runs that are well behaved.')
print ('Please place this on the folder together with the kinetic data.')
print ('At this time, this does not deal well with experiments with different numbers of frames. Please remove the extra tailing frames for it to work properly.')

#%%
experiments = []
experiment_lengths = []
count = 1
while True:
    expnumber = input("What is the experimental number of run number %d?\n(quit to end program, enter nothing to continue): " % (count)) 
    if expnumber == '':
        break
    if expnumber.lower == 'quit':
        quit()
    if not expnumber.isdecimal:
        print('invalid experiment number: ', expnumber)
        continue
    expnumber = expnumber.zfill(5)
    if expnumber in experiments:
        print('You already selected this experiment!')
        continue
    experiments.append(expnumber)
    
    length = len(glob.glob('*%s*'%expnumber))
    experiment_lengths.append(length)
    print('Found',length,'files for that experiment.')
    count += 1

for item in experiment_lengths:
    all_same_lengths = all(item == rest for rest in experiment_lengths)

if not all_same_lengths:
    print('Warning, Not all experiments have the same length!')
    do_quit = input('Do you want to quit? (Y/n) ')
    if do_quit == 'Y':
        quit()
else:
    print('Good, all seem to be the same length.')
    
#%%
ordered_experiment = []
counter = 1
for step in range(1,length+1,1):
    multiple_exp = []
    for experiment in experiments:
        counter_str = str(counter).zfill(4)
        match = list(glob.glob('*%s*%s*'%(experiment,counter_str)))
        if match != []:
            multiple_exp.append(match[0])
        if match == []:
            multiple_exp.append(experiment)
    counter += 1
    ordered_experiment.append(multiple_exp)
        #print(glob)
#%%
pdas_allfiles = []

for step in ordered_experiment:
    pda_group = []
    for experiment in step:
        pda_group.append(pd.read_table(experiment,names=['q','int','err'],dtype=np.float64, header=0))
    pdas_allfiles.append(pda_group)

#%%

checkq = input('Do you want to see if the q values are the same for all experiments?(Y/n) ')
Q_equals = True
if checkq == 'Y':
    print('Too bad, this is not implemented yet.')
    
#==============================================================================
#     for group in pdas_allfiles:
#         for experiment in range(0,len(group)-1):
#             if group[experiment]['q'].all() != group[experiment+1]['q'].all():
#                 Q_equals = False
#     if Q_equals == False:
#         print('Q ranges are not all the same!')
#     else:
#         print('Q ranges seem to be fine.')
#==============================================================================

#%%

subtract_water = input('Do you want to subtract buffer/water from the average?\n If you have done that previously, then it is not necessary (Y/n) ')

if subtract_water == 'Y':
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
        print('Successfully subtracted')
    
#%%
print('\n\n'+'-'*10+'Averaging'+'-'*10)

filename = input('What will the destination filename be?')
want_to_plot = input('Do you want to show a plot of all averaged curves? (Y/n) ')

for counter, groups in enumerate(pdas_allfiles):
    temp_ave = groups[0][:]
    temp_ave['int'] = (sum(item['int'] for item in groups)/len(groups))
    temp_ave['err'] = ((sum(item['err']**2 for item in groups)/len(groups))**(1/2))
    temp_ave.to_csv( (filename+'_'+str(counter+1).zfill(4)+'.csv'), sep='\t')
    
    if subtract_water == 'Y':
        temp_ave['int'] = temp_ave['int'] - water_file_pd['int']
        temp_ave['err'] = (temp_ave['err']**2+water_file_pd['err']**2)**(1/2)
    
    if want_to_plot == 'Y':
        plt.errorbar(temp_ave['q'],temp_ave['int'], yerr=temp_ave['err'])

if want_to_plot == 'Y':
    plt.xscale('log')
    plt.yscale('log')
    plt.show()

print('-'*10+'Done. Bye!'+'-'*10)

