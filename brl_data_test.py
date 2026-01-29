#brl_data_test.py
#
#   test functions for brl_data classes

#   Goal:  standardized data file I/O 

#       University of Washington
#       Biorobotics Lab
#       Summer 2020
#
#   TODO:  use the python unittests module with this (it's great!)
#

import inspect as ins
import brl_data as bd
import unittest as ut
from unittest.mock import patch
import sys
import glob
import os

testParamFileName = 'testParams1' 
testParamValue = '1234' 

#
#  See bottom (__main__()) for overall test flow 
#

def testDeclare(prefix=''): # print name of calling function
    print('\n                                      Testing: ',prefix,ins.stack()[1][3],'\n')

class TestNonUImethods(ut.TestCase):

    #
    # test parameter file reading and loading    
    #
    def test_param(self):
        testDeclare()
        ## first instatiate a parameter file
        pf1 = bd.param_file(testParamFileName)      
        
        # read it
        pf1.read()   # read() opens and closes the file
        
        #  it should print out nicely through the __repr__ method
        print(pf1)   # test repr method 
        
        ##  test that the params are read in right (with meaningless values)
        for k in pf1.params.keys():
            assert pf1.params[k] == testParamValue
             
            
    #
    # test the datafile class        
    #       
    #   We need to mock get_user_basics() to prevent user input requests

        
    def patch_test_get_user_basics(self):
        testDeclare('Patch: ')
        self.d['Ncols']= 3
        self.d['Names'] = ['col 1', 'col 2', 'col 3']
        self.d['Types'] = [ type(1), type(1), type(1)] # ints
        self.d['Description'] = ' ... some descriptive information in text form ...'
        self.d['Notes'] = 'Patch: ... random notes in text form ...'
        self.d['GitLatestCommit'] = 'Patch: Not Recorded'
        self.d['Investigator'] = 'Patch: * your name *'
        self.d['Initials'] = 'Patch: BH'
        self.d['OpenTime'] = 'Patch: 07-Mar-2017'
        self.d['FileType'] = 'Patch: .csv'
        self.d['TestType'] = 'single'
        
    #             the class       the method     the substituted method
    @patch.object(bd.metadata, 'get_user_basics',patch_test_get_user_basics) 
    def test_datafile(self):
        testDeclare()

        # create a datafile with:
        #    descriptive name
        #    investigator initials
        #    parameter file type    (internal valid list)
        #    parameter datafile type 
        print('test_datafile: Got Here!') ###################################################################

        df1 = bd.datafile('testingFile','BH','single')

        df1.set_folders('','')     # use the same folder
        #
        #   .open will call get_user_basics()

        df1.open('w')  # 'w' for fresh start, 'a' for append mode
        df1.dataN = 4  # number of variables. (see also metadata['Ncols'] -- oops!)
        dtest = [3,4,5,6]  # some made up data 
        df1.write(dtest)    # write a row

        for i in range(10):   # write 10 more rows
            dtest[3] = i
            df1.write(dtest)

        # can set the metadata either at START or END of experiment if desired.
        df1.set_metadata(['d1','d2','d3','d4'], 
                        #[type(5)]*3,    # oops- only 3 types given need 4 (uncomment to test checking)
                        [type(5)]*4,  # 
                        ['important data', 'nice to have', 'the upload latency', 'feebdack latency in (ms)'])
        #  above arguments to set_metadata are
        #    Col names
        #    col types 
        #    col comments (desecrip for each column
        df1.metadata.d['TESTING CUSTOM'] = ' custom metadata can be added.'
        print('Initial test datafile generation')
        print(df1.metadata)
        assert df1.validate() == True, 'test file metadata is invalid'   # this should be a valid datafile
        df1.close()

        ###  Test file data input routine
        #
        #    create partial datafile setup
        df2 = bd.datafile('testingFile2','','')
        #  we didn't supply investigator initials or test type
        assert df2.validate() == False
        #print('The file data is valid: ', df2.validate())
        
    def test_datafileAppendTest(self): 
        testDeclare()
        dtest = [3,4,5,6]

        ##   test append with open/close
        df3 = bd.datafile('appendingfile','BH','single')
        df3.set_folders('','') # use local folder
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
        #print('')
        #print('   - - - -',store_name)
        #print('')
        #quit()
        
        df3.dataN = len(df3.metadata.d['Names'])
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
        assert df3.metadata.d['Nrows'] == 8
        df3.close()


    #
    #   Test metadatafile class
    #

    #  test the old ASCII metadata I/O
    def test_metadata_rw(self):
        testDeclare()
        mdd = {'test1':'val1','test2':'val2','test3':'val3'}
        mdd['Names'] = ['name1','name2','Name3', 'name4']
        tys = str(type('hello'))
        mdd['Types'] = [tys,tys,tys,tys]
        mdd['Ncols'] = len(mdd['Names'])

        mdo1 = bd.metadata()
        mdo2 = bd.metadata()
        mdo1.data_file_name = 'metadata_test_file.meta'
        mdo2.data_file_name = 'metadata_test_file.meta'  # we're not going to read or write it tho

        # load up values
        for k in mdd.keys():
            mdo1.d[k] = mdd[k]
        mdo1.save('')    # write out a metadata file
    
        # read in a metadata file
        mdo2.read()  # read it into a new metadata object
        
        assert mdo1.d == mdo2.d,  'metadata_rw_test   FAIL'



    #  test the new json metadata I/O
    def test_metadata_json_rw(self):
        testDeclare()
        mdd = {'test1':'val1','test2':'val2','test3':'val3'}
        mdd['Names'] = ['name1','name2','Name3', 'name4']
        tys = str(type('hello'))
        mdd['Types'] = [tys,tys,tys,tys]
        mdd['Ncols'] = len(mdd['Names'])

        mdo  = bd.metadata()  # source MD
        mdo3 = bd.metadata()  # save via self.save(folder, MDjson=True)
        mdo.data_file_name  = 'metadata_test_file_meta.json'
        mdo3.data_file_name = 'metadata_test_file_meta.json'

        # load up values in source md
        for k in mdd.keys():
            mdo.d[k] = mdd[k]

        mdo.polish()
        mdo.save(MDjson=True)  # write out a metadata file (jason.dump)
        try:
            mdo3.read(MDjson=True)
        except:
            assert False, 'failed to write json metadata'
        mdo3.polish()  # md.read includes automatic string unpacking/type conversion

        #assert mdo.d == mdo2.d,  'metadata_json_rw_test (saveJSON(folder))  FAIL'
        assert mdo.d == mdo3.d,  'metadata_json_rw_test (save(folder,MDjson=True))  FAIL'


    @patch.object(bd.metadata, 'get_user_basics',patch_test_get_user_basics) 
    def test_metadata_getuser(self):
        testDeclare()
        md1 = bd.metadata()
        md1.get_user_basics()
        
        #for k in md1.d.keys():
            #print('>>> {:20} {:}'.format(k,md1.d[k]))
            
        print('\n\n')

    # test the ability to read in old metadata from an existing metadata file.
    def test_readMetaFile(self):
        testDeclare()
        df3 = bd.datafile('testfile','BH','single')
        md = df3.read_oldmetadata(tname='metadata_test_file')
        assert md.validate(), 'Invalid metadata'
        assert len(md.d['Names']) == int(md.d['Ncols'])
        print(md)
        return md

        # test the datafile validator
    def test_validator(self):
        testDeclare()
        # not valid due to missing info
        df3 = bd.datafile('testingFile2','','')
        assert df3.validate() == False
        print('The file data is valid: ', df3.validate(),'  (correct answer: False)')
    

def patch_test_input(message):
    return('v3')

class TestUIMethods(ut.TestCase):
    # a utility function to ask user for data with a pre-filled answer
    #   <Enter> accepts the default
    #   function rejects answers which do not belong to optional valid list
    
    @patch.object(bd, 't_input',patch_test_input) 
    def test_prefuserdata(self):
        testDeclare()
        tvalids = ['v1','v2','v3']
        print('Testing user input utility:')
        print('  press [ENTER] or enter any data to complete the test ...')
        x = bd.pref_input('try an input','v2',valids=tvalids)
        assert x in tvalids, 'pref_input FAIL '
    
        
##   Error Exit for tests
    
def bad_option_exit():    
    print ('\n\nillegal command line input: ',sys.argv[1:])
    print ('valid option(s):  -userinput (test user inputs)')
    print ('                  -gittesting (test git auto functions)')
    print('\n\n')
    quit()
        
    
#
###############     Main   ############################################################
###############            ############################################################
#
    
if __name__ == '__main__':
    
    USER_INPUT_ALLOWED = False
    bd.BRL_auto_git_commit = bd.NEVER
    
    if len(sys.argv) not in [1, 2] :
        bad_option_exit()
        
    if len( sys.argv) == 2:
        if sys.argv[1] == '-userinput':
            USER_INPUT_ALLOWED = True
            bd.BRL_auto_git_commit = bd.NEVER
        elif sys.argv[1] == '-gittesting':
            USER_INPUT_ALLOWED = False
            bd.BRL_auto_git_commit = bd.ASK
            OK = input(' This test may generate new git auto-commits: OK? (y/N): ')
            if OK not in ['Y','y']:
                quit()
        else:
            bad_option_exit()
            

    # quickly set up fake param file:    
    keywords = bd.validinputs().knownKeywords

    x = bd.param_file(testParamFileName)
    fn = testParamFileName
    of = open(fn,'w')
    for kw in keywords: # some keywords 
        print(kw, testParamValue, file=of)
    of.close() 
    
    nskip = 0
    
    #
    # now run all the tests.
    # 
    print('executing Unit Tests')
    
    ut.main(exit=False)

    print('\n\n       Testing is completed\n')  # note that this doesn't print - unittest doesn't return!

    x = input('Do you want to clean up auto-generated testing files? (Y/n)')

    if not ('n' in x.lower()):
        files = glob.glob('*_appendingfile_*')
        files += glob.glob('*_testingFile_*')
        for p in files:
            os.remove(p)
    else:
        print('testing files saved.')

