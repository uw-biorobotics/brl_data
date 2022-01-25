#ic_test.py
#
#   test functions for brl_data classes

#   Goal:  standardized data file I/O 

#       University of Washington
#       Biorobotics Lab
#       Summer 2020
#
#   TODO:  use the python unittests module with this (it's great!)
#

import brl_data as bd

n1 = 'testParams1'
n2 = 'testParams2'
tv1 = '1234'
tv2 = '5678'

#
#  See bottom (__main__()) for overall test flow 
#

#
# test parameter file reading and loading    
#
def paramtest():
    ## first instatiate some parameter files
    pf1 = bd.param_file(n1,'production')      # two types of parameter files are valid: 'production' and 'communication'  (we can expend)
    pf2 = bd.param_file(n2,'communication')
    pf3 = bd.param_file('xxxxx','production')
    
    # read them
    pf1.read()
    pf2.read()
    
    #  they should print out nicely through the __repr__ method
    print(pf1)   # test repr method
    #pf3.read()  ##  this should fail
    
    ##  test that the params are read in right (with meaningless values)
    for k in pf1.params.keys():
        assert pf1.params[k] == tv1
        
    for k in pf2.params.keys():
        assert pf2.params[k] == tv2
        
#
# test the datafile class        
#

def datafiletest():
    # create a datafile with:
    #    descriptive name
    #    investigator initials
    #    parameter file type    (internal valid list)
    #    parameter datafile type 
    df1 = bd.datafile('testingFile','BH','single','.csv')
    ##  note if the file is new, 'a' and 'w' are equivalent.
    df1.open('a')  # 'w' for fresh start, 'a' for append mode
    df1.dataN = 4  # number of variables. (see also metadata['Ncols'] -- oops!)
    dtest = [3,4,5,6]  # some made up data 
    df1.write(dtest)    # write a row
    for i in range(10):   # write 10 more rows
        dtest[3] = i
        df1.write(dtest)
        
    # can set the metadata either at START or END of experiment if desired.
    df1.set_metadata(['d1','d2','d3','d4'], 
                     #['int','int','int'],    # oops- only 3 types given need 4 (uncomment to test checking)
                     [type(5)]*4,  # 
                     ['important data', 'nice to have', 'the upload latency', 'feebdack latency in (ms)'])
    #  above arguments to set_metadata are
    #    Col names
    #    col types 
    #    col comments (desecrip for each column
    df1.metadata.d['TESTING CUSTOM'] = ' custom metadata can be added.'
    
    df1.close()
    
    ###  Test file data input routine

    df2 = bd.datafile('testingFile2','','','.csv')
    assert df2.validate() == False
    #print('The file data is valid: ', df2.validate())
     
def datafileAppendTest(): 
    dtest = [3,4,5,6]

    ##   test append with open/close
    df3 = bd.datafile('appendingfile','BH','single','.csv')
    # can set the metadata at END of experiment if desired.
    df3.set_metadata(['d1','d2','d3','d4'], 
                     #['int','int','int'],    # oops- only 3 types given need 4 (uncomment to test checking)
                     [type(5)]*4,  # 
                     ['important data', 'nice to have', 'the upload latency', 'feebdack latency in (ms)'])
    df3.metadata.d['TESTING CUSTOM'] = ' custom metadata can be added.'
    # example:
    df3.metadata.d['Units'] = ['DateTime','msec','%','Volts'] # probably should be mandatory
    print('The datafile setup is valid: ', df3.validate(),'  (correct answer: True)')
    assert df3.validate() == True
    
    df3.open('w')      # put in some initial data
    store_name = df3.name
    df3.dataN = len(df3.metadata.d['Names'].split(','))
    for i in range(5):
        df3.write(dtest)
    df3.close()        # close the file
    print('          data file closed')
    #  now open it again (simulate e.g. the next day!)
    df3.open('a',tname=store_name)  # we're using an EXISTING filename
    print('          data file re-opened')

    for i in range(3):
        dtest[2] += i
        df3.write(dtest)  # additional data appended
    df3.metadata.d['CUSTOM2'] = 'should reflect Nrows = 8'
    assert df3.metadata.d['Nrows'] == str(8)  # note all metadata are strings
    df3.close()


#
#   Test metadatafile class
#

def metadata_rw_test():
    mdd = {'test1':'val1','test2':'val2','test3':'val3'}
    
    mdo1 = bd.metadata()
    mdo2 = bd.metadata()
    mdo1.data_file_name = 'metadata_test_file.meta'
    mdo2.data_file_name = 'metadata_test_file.meta'

    # write out a metadata file
    # load up values
    for k in mdd.keys():
        mdo1.d[k] = mdd[k]
    mdo1.save()
    # read in a metadata file
    mdo2.read()
    
    print (mdo1.d)
    print (mdo2.d)
    assert mdo1.d == mdo2.d

def metadata_getuser_test():
    md1 = bd.metadata()
    md1.get_user_basics()
    
    for k in md1.d.keys():
        print('>>> {:20} {:}'.format(k,md1.d[k]))
        
    print('\n\n')

   # test the ability to read in old metadata from an existing metadata file.
def readMetaFile_test():
    df3 = bd.datafile('testfile','BH','single','.csv')
    md = df3.read_oldmetadata(tname='tmp.meta')
    t = md.d['Names'].replace('[','').replace(']','')
    nameslist = t.split(',')
    assert len(nameslist) == int(md.d['Ncols'])
    print(md)
    return md

   # a utility function to ask user for data with a pre-filled answer
   #   <Enter> accepts the default
   #   function rejects answers which do not belong to optional valid list
def prefuserdata_test():
    tvalids = ['v1','v2','v3']
    print('Testing user input utility:')
    x = bd.pref_input('try an input','v2',valids=tvalids)
    
    # test the datafile validator
def validator_test():
    # not valid due to missing info
    df3 = bd.datafile('testingFile2','','','.csv')
    assert df3.validate() == False
    print('The file data is valid: ', df3.validate(),'  (correct answer: False)')
      
        
    
if __name__ == '__main__':
    
    # quickly set up fake param files:    
    x = bd.param_file(n1,'production')
    fn = n1+'.prod'
    of = open(fn,'w')
    for k in x.production_keywords:
        print(k, '1234', file=of)
    of.close()
    fn = n2+'.comms'
    of = open(fn,'w')
    for k in x.communication_keywords:
        print(k, '5678', file=of)
    of.close()
    
    #  don't bother with git checking EXCEPT on datafileAppendTest
    bd.BRL_auto_git_commit = bd.NEVER
    # now run all the tests.
    
    paramtest() 
    passstring = ' '*65 + '{:25} PASS'
    print(passstring.format('paramtest'))
    datafiletest()
    print(passstring.format('datafiletest'))
    readMetaFile_test()
    print(passstring.format('readMetaFile_test'))
    validator_test()
    print(passstring.format('validator_test'))
    
    bd.BRL_auto_git_commit = bd.ASK
    datafileAppendTest()
    print(passstring.format('datafileAppendTest'))
    bd.BRL_auto_git_commit = bd.NEVER
 
    prefuserdata_test()
    print(passstring.format('prefuserdata_test'))
    metadata_rw_test()
    print(passstring.format('metadata_rw_test'))
    metadata_getuser_test()
    print(passstring.format('metadata_getuser_test'))


    print ('\n               ALL TESTS PASSED \n\n')
    
