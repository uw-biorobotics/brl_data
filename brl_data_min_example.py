#!/usr/bin/python3
#
#   brl_data_min_example.py

#   Absolute minimalist example
#


##   we have an experiment which generates rows containing one int and three floats.
##  
##      We will get 100 of these and we want to store them in a datafile with associated 
##      metadata.

import brl_data as bd
import math as m
 
  

####################################################################
##                        Generate some fake data  

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
#    investigator initials (BH)
#    data file type    (valid list is in the class validinputs())  (experiment, simulation, etc)

#
#   library will automatically promt you.  Just <enter> to accept the
#     prompt examples.   Changing these is a little sketchy and it's
#     better to use your code to set the key metadata (see brl_data_example.py)
#     (right now the lib is hacked to prompt to match this example).

df1 = bd.datafile('testingFile','BH','experiment')
df1.set_folders('','')   # everything will be in the same folder

print('minimalist example: datafile name: ',df1.name)
#
    
df1.open()  # let's open the file (default is for writing)


##  Now lets write out data  (note this rquires 4 cols)
for i,d in enumerate(d1):
    row = [d, d2[i], d3[i], d4[i]]
    df1.write(row)
df1.close()   # all done

print('\n\n     Your data file is read.  Look for hash: ',df1.hashcode,'\n\n')
