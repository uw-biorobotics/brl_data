#!/usr/bin/python3
#
#   brl_data_min_example.py

#   How to read data from an existing brl_data file
#


##   we have an experiment which generates rows containing one int and three floats.
##  
##      We will get 100 of these and we want to store them in a datafile with associated 
##      metadata.

import brl_data as bd
import math as m
import os
 

#####################################################################
#
# ask user for a hint so they don't have to enter a long filename
#

hashstr = input('Enter first 4+ characters of the hash from the filename:')
if len(hashstr) < 4:
    print(' you like to live dangerously! (might match multiple files)')

#
#  the finder class looks through a list of directories
#     and finds matching file names
#
myfinder = bd.finder()  # a gadget to easily find your data files (or any files).
keys = [hashstr, '.csv']  # two sub-strings to look for in filename
dirs = ['.']      # a list of directories/folders you want it to look in
myfinder.set_dirs(dirs)
result = myfinder.findh(keys)
if len(result) > 1:
    bd.brl_error('multiple files match the keys: ',keys)
if len(result) < 1:
    bd.brl_error('No file(s) found for the keys: '+str(keys)+' in dirs: '+ str(dirs))
dfname   = result[0][1]
dffolder = result[0][0]

#
#  OK - now lets create a datafile instance and open it for reading
#

print('\n                         Opening ', dffolder+'/'+dfname,'\n')
df = bd.datafile('', '','')  # open it with blank title info
df.set_folders('','')        # set these to wherever you want to open datafiles
df.open('r',tname=dfname)
df.metadata.polish()  # convert metadata from strings to useful types
print(df.metadata)

print('')
print('first rows of data are:')
df.print_header()
n=0
for row in df.reader:  # this is set up by the line df.open('r',tname=dfname)
    df.print_row(row)  # automatically formats the row according to types in metadata
    n+=1
    if n>5:
        break



