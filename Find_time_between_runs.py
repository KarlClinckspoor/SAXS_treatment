# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 09:57:40 2017

@author: Karl Jan Clinckspoor
karl970@gmail.com karlclinckspoor@protonmail.com
Made at iNANO at Aarhus University
In a collaboration project with the University of Campinas.
Last modified: 31/08/2017
"""


import glob
import sys
import re
import matplotlib.pyplot as plt
    
#%%

def FindAllTimes(do_change_times):
    initial_frames = glob.glob('*_0001_var.dat')
    if len(initial_frames) == '0':
        print ('No experiments found.')
        return
    print(len(initial_frames), 'found')
    initial_deadtime = 0
    
    for experiment in initial_frames:
        #expnumber = re.findall('\d\d\d\d\d', experiment)[0]
        trash1, trash2, expnumber, *trash3 = experiment.split('_')
        del (trash1, trash2, trash3)
        
        expnumber = int(expnumber)
        selected_experiments = glob.glob('*%s*.dat'%expnumber)
        print('Found',len(selected_experiments),'files for',expnumber)
        if initial_deadtime == 0:
            initial_deadtime = float(input('What is the initial deadtime? (in seconds)\n'))
        elif initial_deadtime != 0 and do_change_times == 'Y':
            initial_deadtime = float(input('What is the initial deadtime used for this experiment? (in seconds)\n'))
        
        times = []
        for item, file in enumerate(selected_experiments):
           wholefile = open(file, 'r').read()
           time = re.findall('time=\S+T\d\d:(\d\d):(\S+)\+', wholefile)
           if len(time) == 0:
               print('Something is wrong with file:', file)
               break
           minutes, seconds = float(time[0][0]), float(time[0][1])
           if item == 0:
               initial_minutes = minutes
               initial_seconds = seconds
           totalseconds = (minutes-initial_minutes)*60 + (seconds-initial_seconds) + initial_deadtime
           #print (file, str(totalseconds) + 's')
           times.append(totalseconds)
        with open(str(expnumber)+'.tim', 'w') as fhand:
            for time in times:
                fhand.write(str(round(time,4)*1000)+'\n')
            fhand.write(str(round(times[-1],4)*1000))
'''
        steps = []
        item = 0
        print ('----Times----')
        for item, time in enumerate(times):
            print ('Frame:',item+1, round(time*1000,4), 'ms')
            if item != 0:
                step = round(times[item]-times[item-1],4)
                steps.append(step)
                print('  Step = ', step)
'''

def FindTimes():
    expnumber = input("What is the experimental number of the run you wish to find the times between each curve? (number, all or quit) \n")
    #expnumber = '3607'
    
    if expnumber.lower() == 'quit' or expnumber == '':
        sys.exit()
    if not expnumber.isdecimal() and expnumber != 'all':
        print('invalid experiment number: ', expnumber)
        return
    if expnumber.isdecimal():
        expnumber = expnumber.zfill(5)
        experiments = glob.glob('*%s*.dat'%expnumber)
        length = len(experiments)
        print('Found',length,'files for that experiment.')
    if length == 0:
        print ('Oops. No experiment found.')
        return
    
    initial_deadtime = float(input('What is the initial deadtime used for this experiment? (in seconds)\n'))
    #initial_deadtime = 0.02
    
    times = []
    
    
    for item, file in enumerate(experiments):
       wholefile = open(file, 'r').read()
       time = re.findall('time=\S+T\d\d:(\d\d):(\S+)\+', wholefile)
       minutes, seconds = float(time[0][0]), float(time[0][1])
       if item == 0:
           initial_minutes = minutes
           initial_seconds = seconds
       totalseconds = (minutes-initial_minutes)*60 + (seconds-initial_seconds) + initial_deadtime
       #print (file, str(totalseconds) + 's')
       times.append(totalseconds)
    
    steps = []
    item = 0
    print ('----Times----')
    for item, time in enumerate(times):
        print ('Frame:',item+1, round(time*1000,4), 'ms')
        if item != 0:
            step = round(times[item]-times[item-1],4)
            steps.append(step)
            print('  Step = ', step)
    
    do_file = input('Do you want to write these times to a file? (Y/n)\n')
    if do_file == 'Y':
        with open (expnumber+'.tim', 'w') as fhand:
            for time, step in zip(times, steps):
                fhand.write(str(round(time,4)*1000)+' '+str(round(step,4)*1000)+'\n')
            fhand.write(str(round(times[-1],4)*1000))
    
    do_graph = input('Do you want to graph the times of this experiment? (Y/(n)) \n')
    if do_graph == 'Y':
        plt.plot(times)
        plt.show()

if __name__ == '__main__':
    print('This script is used to find the times between each experiment')
    print('You can choose to do one by one, or do everything, automatically.')
    while True:
        choice = input ('What do you want to do? (i)ndividual, (all), (quit)?\n')
        if choice == 'i':
            FindTimes()
        elif choice == 'all':
            '''
            do_change = input('Will you want to change the deadtimes of the experiments? (Y/(n))\n')
            FindAllTimes(do_change)
            '''
            print('In development!')
        else:
            sys.exit()    
        do_continue = input('Do you want to continue? ((y)/n)')
        if do_continue == 'n':
            break
        
print('End')

