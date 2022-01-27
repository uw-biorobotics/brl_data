#!/usr/bin/python3
#
#   brl_data_example.py

#   Exampe of some typical use
#


##   we have an experiment which generates rows containing one int and three floats.
##  
##      We will get 100 of these and we want to store them in a datafile with associated 
##      metadata.

import brl_data as bd
import math as m
 
 
#  How to treat the situation where code has changed
#   between the time a file was first opened and some data is appended
#   This flag specifies: what to do if the code has been modified AFTER
#   the file was first opened.   If ALWAYS (or user enters 'Y'), then 
#   create a new commit for the code and add it to the metadata.

# Options:   
#     bd.NEVER      never do auto-commits of the source code
#     bd.ASK        if code has changed since last commit ask user if
#                      autocommit should be done
#     bd.ALWAYS     just automatically generate autocommits when needed
BRL_auto_git_commit = bd.ASK

####################################################################
##   Generate some fake data  

d1 = []
d2 = []
d3 = []
d4 = []

for i in range(100):
    intval = 7*(i+3)
    f1 = float(i) * 16.273
    f2 = 4928.0/float(i+3)
    f3 = -57.3 + m.sqrt(float(i))* 3.716
   
    d1.append(intval)
    d2.append(f1)
    d3.append(f2)
    d4.append(f3)
    
# done with generating fake data
#
#####################################################################


# create a datafile with:
#    descriptive name (testingFile)
#    investigator initials (BH_
#    data file type    (valid list is in the class validinputs())  (experiment, simulation, etc)
df1 = bd.datafile('testingFile','BH','experiment')



#  after defining a datafile, you have to set it's two default folders as follows
#  set up folders defining should the datafiles go, and where is the source code
datafiledir = ''          # '' means same folder as code runs 
codedir = ''              # '' means same folder as currently running
df1.set_folders(datafiledir, codedir)     # use the same folder for brl_data_example




##  Now lets set the metadata for this datafile (but this can be done after saving data, right before close()
col_names = ['TagNumber', 'Voltage', 'Temperature', 'Pressure' ]
int_type = type(5)
float_type = type(3.14159)
col_types = [int_type, float_type, float_type, float_type]
col_comments = [
    'tag number read with model 2160 bar code scanner',
    'Voltage measured at test-point 5',
    'Thermocouple calibration #14739',
    'Relative to atmospheric at 700 ft. elevation'    ]
df1.set_metadata(col_names, col_types, col_comments)
#
#   we also have some custom metadata that is special to our particular experiment
df1.metadata.d['Location'] = 'Site 5, Antarctic Base'

##  Now we can check to make sure our metadata is complete and validated:
if df1.validate():
    print('Datafile is properly set up with valid metadata')
else:
    print('somethings wrong with datafile or metadata setup')
    
df1.open()  # let's open the file (default is for writing)
    
##  Now lets write out data
for i,d in enumerate(d1):
    row = [d, d2[i], d3[i], d4[i]]
    df1.write(row)

df1.close()   # all done

quit()
