# brl_data    A python package for standardizing data files in .csv and associated metadata

## Features

* New: 23-Jun-23:  Now can open a datafile for reading ('.csv' only). (all tests passing)
```
df = bd.datafile('', '','')  # 3 empty args needed
df.set_folders('','')        # set folders as appropriate
df.open('r',tname=fname)     # fname in string form
```
  - datafile now exposes an attribute `reader` (no parens) which is an iterator for the data rows. Metadata
  is automatically read in as well.
```
for row in df.reader:
    print (row)              # each row is a vector of values from one line of .csv file
```

* New: 5-Apr-23 (all tests passing):   `json` format is now standard for the meta files by default.
To stay with the old ASCII format, set `BRL_json_metadata = False` in top of brl_data.py.

  There is a new utility file `brl_convert_metadata.py` which will convert your old .meta files to additional `_meta.json` files.

* Generates consistent, unique, and informative file names -- no more collisions!
  File names contain the creation date and a unique hash. 

* Supports a flexible and expandable dictionary of metadata saved in a separate human-readable file with 
  the same filename root as each datafile.

* Records the git commit hash of your currently running software in the metadata.    Later on you can 
  go back to the exact code commit that generated your data (especially good for simulations).

* Optionally can detect at runtime that you have changed any of your code and automatically make a new commit.

* Intelligently append to existing brl_data datafiles (if for example your code runs once per day). 

## This repo includes

* brl_data.py  module containing the basic methods

* brl_data_test.py    Unit tests for brl_data's basic features.   If it is run with -userinput the test requires
  the user to enter simulated metadata in the test.  If run with -gittesting, the git autocommit feature will be tested.

* brl_data_min_ example.py   A minimal very simple example that writes out data. 

* brl_data_example.py        An example which uses more features.

* brl_convert_metadata.py    Convert all or some of your `.meta` files to `_meta.json` files.

