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
files = os.listdir('.')
csvfiles = []
for f in files:
    if '.csv' in f:
        csvfiles.append(f)

hashstr = input('Enter first 4 characters of the hash from the filename:')
if len(hashstr) < 4:
    print(' you like to live dangerously! (might match multiple files)')
dfname = None
for f in csvfiles:
    if hashstr in f:
        dfname = f
if not dfname:
    bd.brl_error('Somethings wrong with hash string (not found)')

#
#  OK - now lets create a datafile and open it for reading
#

print('opening ', dfname)
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



