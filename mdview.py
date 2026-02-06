#!/usr/bin/python3


#
#  quickly and easily open up metadata files with just a few characters
#     from their hash.   You can edit the metadata if you wish.
#
import brl_data as bd
import sys
import os
import subprocess

VIEWER = 'kate --new'.split()   # substitute your favorite viewer/editor


# print('cmd line: ',sys.argv)
if len(sys.argv) != 2:
   bd.brl_error('To view metadata:\n  usage: >mdview FILE ')
# get list of files
elif len(sys.argv) == 2:
   targethash = sys.argv[1]

# automatically get list of dirs to search
filef = bd.finder()
filef.get_search_dirs()
matchingFiles = filef.findh(targethash)

fnames = []
files = []

mdflist = []
dirs = set()
for f in matchingFiles:
   if '_meta.json' in f[1] and targethash in f[1]:
      mdflist.append(f)
      dirs.add(f[0])
found = False
if len(mdflist) > 1:
   mdflist = [mdflist[0]]    # de dup (copies in other dirs)
for f in mdflist:
   if targethash in f[1]:
      found = True
      filepath = (f[0]+'/'+f[1]).replace('//','/')
      print('opening: ',filepath)
      subprocess.run( VIEWER +  [filepath] )

if not found:
   print('I found no metadata file with: ', targethash)
   for d in dirs:
      print('     ',d)
