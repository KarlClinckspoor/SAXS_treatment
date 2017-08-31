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

#==============================================================================
# Todo:
#       Deal with experiments with different lengths
#		Check the precise number to obtain the necessary error bar (n or n-1?)
#		Use timestamps to obtain the spacing between each curve
#==============================================================================
    
#%%
print('This script is used to find the times between each experiment')

#%%
#expnumber = input("What is the experimental number of the run you wish to find the times between each curve? (number or quit) \n")
expnumber = '3607'

if expnumber.lower() == 'quit' or expnumber == '':
    sys.exit()
if not expnumber.isdecimal():
    print('invalid experiment number: ', expnumber)
    print('Quitting')
    sys.exit()
expnumber = expnumber.zfill(5)
experiments = glob.glob('*%s*'%expnumber)
length = len(experiments)
print('Found',length,'files for that experiment.')
if length == 0:
    print ('Oops. No experiment found. Quitting.')
    sys.exit()

#initial_deadtime = float(input('What is the initial deadtime used for this experiment? (in seconds)\n'))
initial_deadtime = 0.02
times = []


for item, file in enumerate(experiments):
   wholefile = open(file, 'r').read()
   time = re.findall('time=\S+T[0-9][0-9]:([0-9][0-9]):(\S+)\+', wholefile)
   minutes, seconds = float(time[0][0]), float(time[0][1])
   if item == 0:
       initial_minutes = minutes
       initial_seconds = seconds
   totalseconds = (minutes-initial_minutes)*60 + (seconds-initial_seconds) + initial_deadtime
   #print (file, str(totalseconds) + 's')
   times.append(totalseconds)

item = 0
print ('----Times----')
for item, time in enumerate(times):
    print ('Frame:',item+1, round(time*1000,4), 'ms')
    if item != 0:
        print('  Step = ', round(times[item]-times[item-1],4))

do_graph = input('Do you want to graph the times of this experiment? (Y/n) \n')
if do_graph == 'Y':
    plt.plot(times)
    plt.show()
print('End')

