# brl_data    A python package for standardizing data files in .csv and associated metadata

## Features
* New: 3-Apr-23:   You can also save your metadata in JSON format.  Example:

'''datafile = brl_data(xx,yy,zz)
...  create your data ...
datafile.write(folder)
datafile.metadata.saveJSON()
datafile.close()
'''

*  Generates consistent, unique, and informative file names -- no more collisions!
 File names contain the creation date and a unique hash. 
 
*  Supports a flexible and expandable dictionary of metadata saved in a separate human-readable file with 
the same filename root as each datafile.

*  Records the git commit hash of your currently running software in the metadata.    Later on you can 
go back to the exact code commit that generated your data (especially good for simulations).

*  Optionally can detect at runtime that you have changed any of your code and automatically make a new commit.

*  Intelligently append to existing brl_data datafiles (if for example your code runs once per day). 


## This repo includes
* brl_data.py  module containing the basic methods

* brl_data_test.py    Unit tests for brl_data's basic features.   If it is run with -userinput the test requires
the user to enter simulated metadata in the test.  If run with -gittesting, the git autocommit feature will be tested.
 
* brl_data_min_ example.py   A minimal very simple example that writes out data. 

* brl_data_example.py        An example which uses more features.



    
    
