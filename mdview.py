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

#  all the dirs we might find data files
dirs = ['.',
        '/folder1',
        '...folder 2...',
        '/home/user/folder 3'
        ]
dirs = ['.']  # delete this if you modify the list above

print('cmd line: ',sys.argv)
if len(sys.argv) != 2:
   bd.brl_error('To view metadata:\n  usage: >mdview FILE ')
# get list of files
elif len(sys.argv) == 2:
   targethash = sys.argv[1]

fnames = []
files = []
for d in dirs:
   fnames += os.listdir(d)
   for n in fnames:
      files.append([d,str(n)]) # dir, name

mdflist = []
for f in files:
   if '_meta.json' in f[1] and targethash in f[1]:
      mdflist.append(f)

found = False
if len(mdflist) > 1:
   mdflist = [mdflist[0]]    # de dup (copies in other dirs)
for f in mdflist:
   if targethash in f[1]:
      found = True
      filepath = f[0]+'/'+f[1]
      subprocess.run( VIEWER +  [filepath] )

if not found:
   print('I found no metadata file with: ', targethash ,'in:')
   for d in dirs:
      print('     ',d)
