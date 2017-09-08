# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 09:12:11 2017

@author: Karl Jan Clinckspoor
karl970@gmail.com karlclinckspoor@protonmail.com
Made at iNANO at Aarhus University
In a collaboration project with the University of Campinas.
Last modified: 08/09/2017
"""

import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# warnings.simplefilter(action='ignore', category=ParserWarning)


def getExperiments():
    experiment_numbers = []
    experiment_files = []
    count = 1
    #extension = input('what is the extension of the file you want? .dat, .csv: ')
    extension = '.dat'
    while True:
        expnumber = input("What is the experimental number of run number %d?\n"
                          "(quit to end program, enter nothing to continue): " % count)

        if expnumber.lower() == 'quit':
            sys.exit()
        if expnumber == '' and len(experiment_numbers) == 0:
            print("You didn't select anything! Quitting.")
            sys.exit()
        if expnumber == '':
            break
        if not expnumber.isdecimal():
            print('invalid experiment number: ', expnumber)
            continue
        expnumber = expnumber.zfill(5)
        if expnumber in experiment_numbers:
            print('You already selected this experiment!')
            continue

        experiments = glob.glob('*%s*%s' % (expnumber, extension)) #added extension. Test!
        length = len(experiments)

        print('Found', length, 'files for that experiment.')

        if length == 0:
            print('Oops. No experiment found. Do you want to select another?')
            do_select = input('Y/n: ')
            if do_select == 'Y':
                continue
            elif do_select != 'Y':
                sys.exit()

        experiment_numbers.append(expnumber)
        experiment_files.append(experiments)
        count += 1

    return experiment_numbers, experiment_files


def check_lengths(experiment_files):
    for item in experiment_files:
        if not all(len(item) == len(rest) for rest in experiment_files):
            return False
        else:
            return True


# Think about changing this to something less verbose and just trim the excessive long files.
def fix_lengths(experiment_numbers, experiment_files):
    print('Error! The experiments have different lengths. Please select which one you want to trim down.')
    print('number', 'length')
    for number, exp_list in zip(experiment_files):
        print(number, len(exp_list))
    choice = input('Which one?').zfill(5)
    if choice == 'quit':
        sys.exit()
    if choice not in experiment_numbers:
        print('Invalid number')
        return False

    index = 0 # index of the file to trim
    for i, number in enumerate(experiment_numbers):
        if choice == number:
            index = i

    minimum_length = min(len(i) for i in experiment_files)

    print('Will trim experiment %s to %d' % (choice, minimum_length))
    experiment_files[index] = experiment_files[index][:minimum_length]
    return experiment_files



def orderExperiments(experiment_files):
    ordered_experiments = []
    for counter in range(len(experiment_files[0])): # Since they are guaranteed to have the same lengths
        group = []
        for exp in range(0, len(experiment_files)):
            group.append(experiment_files[exp][counter])
        ordered_experiments.append(group)
    return ordered_experiments


# This still needs testing to check if it will actually work, but this saves much time and code.
def orderExperimentsAndConvert(experiment_files):
    ordered_experiments = []
    for counter in range(len(experiment_files[0])): # Since they are guaranteed to have the same lengths
        group = []
        for exp in range(0, len(experiment_files)):
            file = experiment_files[exp][counter]
            names_sub = ['q', 'int', 'err', 'trash']
            temp_pda = pd.read_table(file, delimiter = ' ', names=names_sub,
                                     dtype=np.float64, header=0) #Add a check here to see if the trash column is needed.
            del(temp_pda['trash']) # File end in ' \n', so pandas read it as a blank column, had to remove.
            group.append(temp_pda)
        ordered_experiments.append(group)
    return ordered_experiments


# todo
def checkQ(ordered_experiments_pd):
    qs = []
    for expgroup in ordered_experiments_pd: #only checks the q for the first file, for all should be the same.
        qs.append(expgroup[0]['q'])
    for item, q in enumerate(qs):
        pass
    return True


def openWater():
    found_water_file = False
    while not found_water_file:
        water_file_number = input('What is the file number for water?')
        water_file_name = glob.glob('*%s*' % water_file_number)
        if water_file_name == []:
            print('File not found')
            do_continue = input('Do you want to try again? Y/n')
            if do_continue == 'Y':
                continue
            else:
                return False

    print('Found file(s): ', water_file_name)

    if len(water_file_name) > 1:
        selectedfile = input('More than one file was found. Which one to select? (number, beginning from 0)')
        try:
            water_file_pd = pd.read_table(water_file_name[int(selectedfile)], names=['q', 'int', 'err'],
                                          dtype=np.float64, header=0)
        except:
            print('Could this file file. Opening the first one')
            water_file_pd = pd.read_table(water_file_name[0], names=['q', 'int', 'err'], dtype=np.float64, header=0)

    elif len(water_file_name) == 1:
        water_file_pd = pd.read_table(water_file_name[0], names=['q', 'int', 'err'], dtype=np.float64, header=0)
        print('Successfully opened the file')
    return water_file_pd


def averageCurvesAndWrite(ordered_experiments_pd, subtract_water, water_file):
    print('-----Averaging-----')
    filename = input('What will the destination filename be? ')
    averaged_curves = []
    for counter, groups in enumerate(ordered_experiments_pd):
        temp_ave = groups[0][:]
        temp_ave['int'] = (sum(item['int'] for item in groups) / len(groups))
        temp_ave['err'] = ((sum(item['err'] ** 2 for item in groups) / len(groups)) ** (1 / 2))
        if subtract_water == 'Y' and water_file != '':
            temp_ave['int'] = temp_ave['int'] - water_file['int']
            temp_ave['err'] = (temp_ave['err'] ** 2 + water_file['err'] ** 2) ** (1 / 2)
        temp_ave.to_csv((filename + '_' + str(counter + 1).zfill(4) + '.csv'), sep=',', index=False)
        averaged_curves.append(temp_ave)
    return averaged_curves


def plotCurves(averaged_files):
    for item in averaged_files:
        plt.errorbar(item['q'], item['int'], yerr = item['err'])
    plt.xscale('log')
    plt.yscale('log')
    plt.show()
    return

def mainmenu():
    experiment_number, experiment_files = getExperiments()
    all_same_length = check_lengths(experiment_files)
    while not all_same_length:
        experiment_files = fix_lengths(experiment_number, experiment_files)
        all_same_length = check_lengths(experiment_files)
    print('Good! All have the same length. Continuing')
    ordered_experiments_pda = orderExperimentsAndConvert(experiment_files)
    do_subtract = input('Do you want to subtract water? Y/n ')
    water_file = ''
    if do_subtract == 'Y':
        water_file = openWater()
        if water_file == False:
            do_subtract = 'n'

    averaged_curves = averageCurvesAndWrite(ordered_experiments_pda, do_subtract, water_file)
    do_plot = input('Do you want to plot the averaged curves? Y/n')
    if do_plot == 'Y':
        plotCurves(averaged_curves)

    do_continue = 'Do you want to continue? Y/n'
    if do_continue == 'Y':
        return True
    else:
        return False

if __name__ == '__main__':
    print('This script is to average several SAXS kinetic runs that are well behaved.')
    print('Please place this on the folder together with the kinetic data.')
    print('It is better to have subtracted your data before doing this.')
    do_continue = True
    while do_continue:
        do_continue = mainmenu()
    print('Bye!')
    quit(False)