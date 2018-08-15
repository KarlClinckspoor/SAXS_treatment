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

# todo: check the actual necessity of using sys.exit or quit() in the code.
# todo: debug A LOT. Different lengths of kinetics, subtract water
# todo: incorporate the time calculating functions into this and warn the user if there are discrepancies in the
#       timing of the different runs.


def getExperiments():
    """Looks at the directory where the script is and tries to find files with a filename with a 5 digit number.
    The files must end with either .csv or .dat.
    Will cause some problems if other unrelated files with the experiment number on the name
    So be sure to make the directory relatively clean.
    It will ignore all other files and won't change the content of anything it reads."""
    experiment_numbers = []
    experiment_files = []
    count = 1

    while True:
        extension = input('What is the extension of the file you want to choose? .dat or .csv? ')
        if extension == 'quit':
            sys.exit()
        if extension != '.dat' and extension != '.csv':
            print('Please select one of the two! Do not forget the "."!')
        if extension == '.dat' or extension == '.csv':
            break

    while True:
        expnumber = input("What is the experimental number of run number %d?\n"
                          "(quit to end program, enter nothing to continue): " % count)

        if expnumber.lower() == 'quit':
            sys.exit()  # or should this be quit?
        if expnumber == '' and len(experiment_numbers) == 0:
            print("You didn't select anything! Try again.")
            continue
        if expnumber == '':
            break
        if not expnumber.isdecimal():
            print('invalid experiment number: ', expnumber)
            continue
        expnumber = expnumber.zfill(5)
        if expnumber in experiment_numbers:
            print('You already selected this experiment!')
            continue

        experiments = glob.glob('*%s*%s' % (expnumber, extension))  # added extension. Test!
        length = len(experiments)

        print('Found', length, 'files for that experiment.')

        if length == 0:
            print('Oops. No experiment found. Do you want to select another?')
            do_select = input('Y/n: ')
            if do_select == 'Y':
                continue
            elif do_select != 'Y':
                sys.exit()  # should this be quit?

        experiment_numbers.append(expnumber)
        experiment_files.append(experiments)
        count += 1

    return experiment_numbers, experiment_files


# todo: finish this.
def getExpNumbersInFolder():
    print('Attempting to find data containing "saxs" in the name')
    exps = glob.glob('*saxs*')
    if len(exps) != 0:
        print('This is the name of the first file. Does')

    return True


def check_lengths(experiment_files):
    """Sometimes it is possible to run multiple experiments with the same spacing but less curves at higher times.
    This function will check if all the experiments are all of the same lengths and return a Boolean."""
    for item in experiment_files:
        if not all(len(item) == len(rest) for rest in experiment_files):
            return False
        else:
            return True


def fix_lengths(experiment_numbers, experiment_files):
    """Asks the user which file they want to trim down so all files have the same lengths.
    Superseded by the quiet version, which is smarter."""

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

    index = 0  # index of the file to trim
    for i, number in enumerate(experiment_numbers):
        if choice == number:
            index = i

    minimum_length = min(len(i) for i in experiment_files)

    print('Will trim experiment %s to %d' % (choice, minimum_length))
    experiment_files[index] = experiment_files[index][:minimum_length]
    return experiment_files


def fix_lengths_quiet(experiment_files):
    """Finds the minimum length of all the experiment runs and trims the long experiments down to the minimum length"""
    print('The experiments have different lengths. We will attempt to trim them down to the shortest length')
    minimum_length = min(len(i) for i in experiment_files)
    print('The shortest length is', minimum_length)
    for index, group in enumerate(experiment_files):
        group = group[:minimum_length]
        # experiment_files[index] = experiment_files[index][:minimum_length]
    print('Trimmed.')
    return experiment_files


def orderExperiments(experiment_files):
    """Orders the files from a list containing lists with each file sequentially to another list with smaller groups.
    Each smaller group contains all the n numbers of runs of that number. For example:

    input: experiment_files = [[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5]
    output: ordered_experiments = [[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5]]

    Makes it easier to average the files later on.
    """
    ordered_experiments = []
    for counter in range(len(experiment_files[0])):  # Since they are guaranteed to have the same lengths
        group = []
        for exp in range(0, len(experiment_files)):
            group.append(experiment_files[exp][counter])
        ordered_experiments.append(group)
    return ordered_experiments


# This still needs testing to check if it will actually work, but this saves much time and code.
def orderExperimentsAndConvert(experiment_files):
    """Orders the files from a list containing lists with each file sequentially to another list with smaller groups.
    Each smaller group contains all the n numbers of runs of that number. For example:

    input: experiment_files = [[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5]
    output: ordered_experiments = [[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5]]

    As it reorders the experiments into the new list, converts them into pandas dataframes with 3 column names.
    ['q','int','err'] and uses delim_whitespace = True to avoid errors with multiple whitespace in files.
    """

    ordered_experiments = []
    for counter in range(len(experiment_files[0])):  # Since they are guaranteed to have the same lengths
        group = []
        for exp in range(0, len(experiment_files)):
            file = experiment_files[exp][counter]
            names_sub = ['q', 'int', 'err']
            temp_pda = pd.read_table(file, names=names_sub, delim_whitespace=True, dtype=np.float64, header=0)
            group.append(temp_pda)
        ordered_experiments.append(group)
    return ordered_experiments


# todo
def checkQ(ordered_experiments_pd):
    qs = []
    for expgroup in ordered_experiments_pd:  # only checks the q for the first file, for all should be the same.
        qs.append(expgroup[0]['q'])
    for item, q in enumerate(qs):
        pass
    return True


def openWater():
    """Asks the user for the run number of water and returns a pandas dataframe of the file.
    Used when the user wants to subtract water/buffer from previously unsubtracted files."""
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
                                          dtype=np.float64, header=0, delim_whitespace=True)
        except:
            print('Could this file file. Opening the first one')
            water_file_pd = pd.read_table(water_file_name[0], names=['q', 'int', 'err'], dtype=np.float64, header=0,
                                          delim_whitespace=True)

    elif len(water_file_name) == 1:
        water_file_pd = pd.read_table(water_file_name[0], names=['q', 'int', 'err'], dtype=np.float64, header=0,
                                      delim_whitespace=True)
        print('Successfully opened the file')
    return water_file_pd


def averageCurvesAndWrite(ordered_experiments_pd, subtract_water, water_file):
    """The main function of this script.
    Asks for a filename, averages the column 'int' in the dataframes, propagates the error and saves into .csv
    Uses a temporary pandas dataframe to collect the data in order to save time from having to build one from zero."""

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
        temp_ave.to_csv((filename + '_' + str(counter + 1).zfill(4) + '.csv'), sep=' ', index=False)
        # separator has to be a space to be compatible with SAXSutilities.
        averaged_curves.append(temp_ave)
    return averaged_curves


def plotCurves(averaged_files):
    """Just a small function used to plot the resulting curves in a double logarithmic plot with errorbars"""
    for item in averaged_files:
        plt.errorbar(item['q'], item['int'], yerr = item['err'])
    plt.xscale('log')
    plt.yscale('log')
    plt.show()
    return


def mainmenu():
    """The function that binds together all other functions in this script."""
    experiment_number, experiment_files = getExperiments()
    all_same_length = check_lengths(experiment_files)

    while not all_same_length:
        experiment_files = fix_lengths_quiet(experiment_files)  # changed for the quiet version
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
    do_plot = input('Do you want to plot the averaged curves? Y/n ')
    if do_plot == 'Y':
        plotCurves(averaged_curves)

    do_continue = input('Do you want to continue? Y/n ')
    if do_continue == 'Y':
        return True
    else:
        return False


if __name__ == '__main__':
    """Just the starting area of the script, giving warnings before starting the main program loop."""
    print('This script is to average several SAXS kinetic runs that are well behaved.')
    print('Please place this on the folder together with the kinetic data.')
    print('It is better to have subtracted your data before doing this.')
    do_continue = True
    while do_continue:
        do_continue = mainmenu()
    print('Bye!')
    quit(False)
