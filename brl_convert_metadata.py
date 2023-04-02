#!/usr/bin/python3
#
#   brl_convert_metadata.py

#  The metadata class now has a method to output metadata in a basic JSON forma:
#
#  This is a utility to convert brl-style metadata to JSON metadata
#

import brl_data as bd
import os


dnames = os.listdir()
files = []
for n in dnames:
    if os.path.isfile(n) and '.meta' in n:
        files.append(n)

print('The meta files are: ')
print(files)

print('Enter a string to select desired .meta files: (default "*" means ALL .meta files)')
keystr = input('(*) >')

targets = []
if (keystr == '' or keystr == '*'):
    targets = files
else:
    for i,f in enumerate(files):
        if keystr in f:
            targests.append(f)  #

# we could have re-used df1, but to simulate the case of running once per day
#   we'll instantiate a new datafile
foldername = ''  # means current folder
for f in targets:
    print('Converting metadata to JSON: ', f)
    df = bd.datafile('X','X','single')
    df.set_folders(foldername,foldername)
    df.set_both_filenames(f.replace('.meta','.csv'))  # brl_data wants this to INCLUDE the .csv
    df.metadata.read()
    df.metadata.saveJSON(foldername)
