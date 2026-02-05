# brl_data    A python package for standardizing data files in .csv and associated metadata

## Features

* Generates consistent, unique, and informative file names -- no more collisions!
  File names contain the creation date and a unique hash. 

* Supports a flexible and expandable dictionary of metadata saved in a separate human-readable file with 
  the same filename root as each datafile.

* Records the git commit hash of your currently running software in the metadata.    Later on you can 
  go back to the exact code commit that generated your data (especially good for simulations).

* Optionally can detect at runtime that you have changed any of your code and automatically make a new commit.

* Intelligently append to existing brl_data datafiles (if for example your code runs once per day). 

## News

* New: 29-Jan-26:  Tests are cleaned up and passing.

We now make it easier for a new user not to have to edit code.  New file brl_data.conf will
initialize some key metadata (meta-metadata??) such as the user's name and the data folder location.
brl_data will look for brl_data.conf in a few 'logical' places and not be too picky.  File format
is each line starts with a keyword followed by one or more other words:
   -  user_name   First Last
   -  data_folder   < full pathname of where you want data to go>
   - git_folder     < full pathname of where do you want it to track git commits of your code (advanced feature) >
   - test_type     < any word which describes the generic class of data: examples:  experiment, engineeringtest, debugging, demo >
   - new_metadata  < anything you want to add to the metadata dictionary:  example:  "new_metadata  Location  Arctic Base 9"
   or "new_metadata  TissueType  Liver">

brl_data.conf is *optional*. defaults will be assumed.   Also you can set these parameters in your code if you prefer,
even if the file exists you could override them. If present, brl_data.conf is read and parsed when you instantiate a datafile class.

* New: 24-Jul-23:  added a utility 'mdview.py' to quickly pull up and view/edit the
metadata with just a few characters from the hash code.
* New: 28-Jun-23:  Created example file (brl_data_read_a_file_example.py) for
simple reading of an existing brl_data datafile.  Now uses the metadata for smart
type conversion from .csv string data.  You can still use regular python .csv
module if desired.
* New: 23-Jun-23:  tried to suport "pwd" on windows with "cd" - runs on linux but needs
windows testing.  There could be other windows problems.
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

## This repo includes

* brl_data.py  module containing the basic methods

* brl_data_test.py    Unit tests for brl_data's basic features.   If it is run with -userinput the test requires
  the user to enter simulated metadata in the test.  If run with -gittesting, the git autocommit feature will be tested.

* brl_data_min_ example.py   A minimal very simple example that writes out data. 

* brl_data_example.py        An example which uses more features.

* brl_convert_metadata.py    Convert all or some of your `.meta` files to `_meta.json` files.

