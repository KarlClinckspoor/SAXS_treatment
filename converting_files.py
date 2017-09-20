# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 15:58:32 2017

@author: Karl Jan Clinckspoor
karl970@gmail.com karlclinckspoor@protonmail.com
Made at iNANO at Aarhus University
In a collaboration project with the University of Campinas.
Last modified: 15/09/2017
"""

import glob


def convert_file(list_contents, dest_filename, multiple=True):
    """Gets the file contents as a list and writes two dummy headers, the number of points and then closes the \
    destination file. By default it will do a series of files and not ask the the comment lines."""
    fdest = open(dest_filename, 'w', encoding='utf-8')
    if multiple:
        comm1 = 'nothing special'
        comm2 = 'nothing special'
    else:
        comm1 = input('What is the first line of comments?')
        comm2 = input('What is the second line of comments?')

    length = len(list_contents)
    fdest.write(comm1 + '\n')
    fdest.write(comm2 + '\n')
    fdest.write(str(length) + '\n')
    for line in list_contents:
        fdest.write(line + '\n')
    fdest.close()
    return


# todo: find out the max length of the list and warn the user. Is it 59?
if __name__ == '__main__':
    choice = input('Do you want to convert a series of experiments [1, def] or a single one [2]?'
                   + '\nYou can also [list] all files in the directory'
                   + '\nAnd create a list file to [batch] treatment\nChoice: ')
    if choice == 'list:':
        files = glob.glob('*.*')
        print(*files)
    if choice == 'batch':  # todo: do not insert directories into the input.lis
        append = input('Do you want to [1] create a new list or [2] append to a new one?')
        fname = input('What is the file name of the file/series you want to batch treat? ')
        files = glob.glob('*{}*'.format(fname))
        if append == '1':
            newlist = open('INPUT.LIS', 'w')
            newlist.write(' ' + str(len(files)) + '\n')
            for file in files:
                newlist.write(' ' + file + '\n')
            newlist.close()
            quit()

        elif append == '2':
            oldlist = open('INPUT.LIS', 'r')  # todo: check for file missing
            contents = [line.strip() for line in oldlist]
            oldlength = int(contents[0])
            del (contents[0]) # removes the counter at the beginning of the file.
            newlength = oldlength + len(files)
            oldlist.close()

            newlist = open('INPUT.LIS', 'w')
            newlist.write(' ' + str(newlength) + '\n')
            for line in contents:
                newlist.write(' ' + line + '\n')
            for file in files:
                newlist.write(' ' + file + '\n')
            newlist.close()
            quit()
        else:
            print('I did not understand.')
            quit()

    if choice == '2':
        fname = input('What is the file name of the file/series you want to convert? ')
        try:
            file = open(fname, 'r')
        except FileNotFoundError:
            print('File not found. Try again.')
            quit()
        content_list = list(line.rstrip() for line in file)[1:]  # Ignores the q int err line of the file.
        file.close()
        dest_filename = input('What will the destination filename be? No extension, it will be saved to .dat.' +
                              'Only 8 characters, please!').strip()
        dest_filename = dest_filename[:8] + '.dat'  # Trims to 8 characters
        convert_file(content_list, dest_filename, multiple=False)
    else:
        fname = input('What is the file name of the file/series you want to convert? ')
        files = glob.glob('*{}*'.format(fname))
        counter = 1
        filename = input('What will the destination filename be? Must have space for 2 numerals' +
                         ' (6 chars total): ').strip()
        filename = filename[:7]
        for file in files:
            dest_filename = filename + str(counter).zfill(2) + '.dat'
            fhand = open(file, 'r')
            content_list = list(line.rstrip() for line in fhand)[1:]  # Ignores the first line.
            convert_file(content_list, dest_filename)
            print('Converted {} to {}'.format(file, dest_filename))
            counter += 1
    print('Done!')

