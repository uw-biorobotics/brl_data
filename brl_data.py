# Class skeletons for ICARUS project
#
## ICARUS = Internet Characterization for Robotics Surgery

#   reference:   https://docs.google.com/document/d/1vdLvEAG2EOO_GQrVbXmGArcY1ufwau3ExKEuPfJ0TFE/edit?usp=sharing
#

####  Imports
import datetime as dt
#from dateutil import parser
import uuid
import inspect
import sys, os, subprocess, ast
import csv
import json

#############  Configurations
#
#  SUMMARY
#

NEVER = 0
ASK   = 1
ALWAYS = 2
#  How to treat the situation where code has changed
#   between the time a file was first opened and some data is appended
#   This flag specifies: what to do if the code has been modified AFTER
#   the file was first opened.   If ALWAYS (or user enters 'Y'), then 
#   create a new commit for the code and add it to the metadata.
BRL_auto_git_commit = ASK

######################   Utilities

############# create a simplistic n-char UUID
def brl_id(n):
    u = uuid.uuid4()  # 
    u = str(u).replace('-','')
    m = int(n/2)
    return u[0:m] + u[-m:-1]

#############  accept some input with a default example
#        and optional list of valid responses
#  "Prefilled input" with optional validation
#   message:  prompt to user (str)
#   example:  prefilled / default value (assumed valid)
#   valids: a list of strings that input must belong to
#
def pref_input(message, example, valids=None):
    while True:
        vin = input(message+' ({:}):'.format(example))
        if vin == '':
            return example
        else:
            if valids != None:
                if vin in valids:
                    return vin
                else:
                    print('invalid response: please enter '+str(valids))
            else:  # no checking
                return vin

##############   interact with user to input or update metadata
#                   directly to the metadata dictionary
#
def smart_query(d,k,msg=None,example=None,valids=None):
    if msg == None:
        msg = k        
    if example == None:
        if k in d:
            example = d[k]
        else:
            example = ''
    if  k in d:
        y = pref_input(msg,example,valids)
    else:
        y = pref_input(msg,example,valids)
    d[k] = y
    return
 
#############  Error handling
#
#  simplify diagnostics when things go wrong
#
def brl_error(msg,fatal=True):
    # this identifies the function than had the error(!)
    err_fcn = sys._getframe(1).f_code.co_name
    #https://stackoverflow.com/questions/53153075/get-a-class-name-of-calling-method
    frame = inspect.currentframe().f_back
    try:
        # try to access the caller's "self"
        try:
            self_obj = frame.f_locals['self']
            # get the class of the "self" and return its name
            err_class = type(self_obj).__name__
        except KeyError:
            err_class = 'unknown'
    finally:
        # make sure to clean up the frame at the end to avoid ref cycles
        del frame
    print('brl_data:class ' +err_class+'():'+err_fcn+'():',msg)
    if fatal:
        quit()
    else:
        return

class validinputs:
    def __init__(self):
        self.validtesttypes = ['simulation','experiment','single', 'longterm']  # examples only
        self.validfiletypes = ['.csv', '.json']       # others?  or standardize on csv??
        validPfTypes = ['production','communication']
        self.production_keywords= ['homegitFolder', 'debugOutput', 'homedataFolder','dataFolder','weekdays','ops_per_day', 'duration_mean','duration_sd','start_hour','end_hour','end_date','ename','homeFolder','githomeFolder','datahomeFolder']  # production keywords
        self.communication_keywords = ['identity','server','command_nbytes','feedback_nbytes']  # coms. keywords
        self.testkeywords = ['floattestp','inttestp']
        self.knownKeywords = self.production_keywords + self.communication_keywords+self.testkeywords
###
#
#  metadata: Dictionary and file I/O
#    TODO: replace comparable functions in 
#     datafile()
#
class metadata:
    def __init__(self):
        self.d = {}  # the actual metadata 
        self.data_file_name = '' 
        self.d['Dependencies'] = str([ sys.argv[0],'brl_data.py' ])
     
    # write out metadata (OVERWRITE old metadata)
    def save(self,folder):
        if len(self.data_file_name) == 0:
            brl_error(" no data file name has been specified.")
        # derive metadata file name from datafile name
        mdfn = self.data_file_name.split('.')[0] + '.meta'
        print('saving metada as '+mdfn)
        fdmd = open(mdfn,'w')
        for k in self.d.keys(): 
            print('{0:20} "{1:}"'.format(k, str(self.d[k])),file=fdmd)
        fdmd.close()
        
    # this reads in the metadata from a file (which might include comments)
    #  Note that dictionary will still contain string values.  e.g. Lists must
    #  be parsed, ints must be cast etc.
    #
    #  sometimes the metadata file might be missing but we want to be robust to that
    def read(self):
        mfn = self.data_file_name.split('.')[0] + '.meta'
        fdmd = False
        try:
            fdmd = open(mfn,'r')
        except:
            brl_error("Can't open metadata file: [{:}]".format(mfn),fatal=False)
        if fdmd:
            #print('reading metadata from '+mfn)
            for line in fdmd:
                if '#' in line:
                    l1, l2 = line.split('#')
                else:
                    l1 = line
                l1 = l1.strip()
                if len(l1)>0:
                    w1, w2 = l1.split(' ',1)  # white space split
                    w1 = w1.strip()
                    w2 = w2.strip()
                    self.d[w1] = w2.replace('"','')
            fdmd.close()
            return True
        else:
            return False
        
    def get_user_basics(self): 
        vis = validinputs()
        print('\nPlease enter basic information for the metadata you would like to create:')
        smart_query(self.d,'Ncols',msg='How many colums of data?', example=3) # str type for everything!
        smart_query(self.d,'Names',msg='Column names (as list [...]):', example=['col 1', 'col 2', 'col 3'])
        smart_query(self.d,'Types',msg='Column Types (as list [...]):', example=[ type(1), type(1), type(1)])
        smart_query(self.d,'Description',msg='...  description ...')
        smart_query(self.d,'Notes',msg='Notes: (...):', example='...some notes...')
        smart_query(self.d,'GitLatestCommit',example='Not Recorded')        
        smart_query(self.d,'Investigator', example='*your name*')
        #
        # generate initials
        n1, n2 = self.d['Investigator'].split()
        n1 = n1[0]
        n2 = n2[0]
        
        smart_query(self.d,'Initials', msg='Your Initials',example=n1+n2)
        thedate = str(dt.date.today())
        smart_query(self.d,'OpenTime', msg='Creation Date:', example=thedate)
        vinp = validinputs()
        vf = vinp.validfiletypes
        vt = vinp.validtesttypes
        smart_query(self.d,'FileType', example=vf,valids=vis.validfiletypes)
        smart_query(self.d,'TestType', example=vt,valids=vis.validtesttypes)
        

    def __repr__(self):
        str = '----------------------------------------------\n' 
        str += '{:25}{:}\n'.format('Experiment Metadata: ','') 
        str += '{:25}{:}\n'.format('Dictionary:','')
        for k in self.d.keys():
            str += '       {:25}{:} [{:}]\n'.format(k,self.d[k],type(self.d[k])) 
        str += '----------------------------------------------\n'
        return str
     
#
#          Data
#
       
#############  Log file for data storage
#
#  creation and I/O for numerical datafiles
#   TODO: create a class for image files and a class for video files

#  descrip_str     A descriptive string for the dataset
#  inv_init        Investigator's initials
#  testtype        "type" of test generating the data (see validinputs class)

class datafile:
    def __init__(self, descrip_str, inv_init, testtype):
        self.descrip = descrip_str
        self.initials = inv_init
        self.ttype = testtype  # defined in "validinputs" class
        self.ftype = '.csv'  # only .csv at this point
        self.fd = None  # file descriptor
        self.name = ''    # can override this any time
        self.folder = ''  # can direct datafiles into a folder
        self.gitrepofolder = ''   # place where current code lives
        self.output_class = None  # for example:  csv.writer()
        self.metadata = metadata()
        self.metadata.d['Ncols'] = 0 # correct length of data vector
        self.metadata.d['Nrows'] = 0 # number of rows of data written so far.
        self.dataN = 0
        self.setFoldersFlag = False
        
    # set correct folders for this datafile
    #   datafolder     where to put the datafile
    #   gitfolder      where is your current source code
    #
    #   folder is an absolute or relative pathname which 
    #     will be pre-pended to the filename 
    #
    #   to use the "current" folder for everything, just enter
    #    '' for both folders.
    def set_folders(self, datafolder, gitfolder):
        self.setFoldersFlag = True
        self.set_data_folder(datafolder)
        self.gitrepofolder = gitfolder
        # these can only be done after folders are set
        self.metadata.d['GitLatestCommit'] = get_latest_commit(folder=self.gitrepofolder)
        self.gen_name()  # generate output filename
        self.metadata.data_file_name = self.name


    def set_data_folder(self,folname):
        if self.fd:
            brl_error('Its too late to change folder to'+folname+'. datafile already open')
        if '.' in folname: 
            brl_error('You cannot use . in folder name: ' + folname)
        self.folder=folname
        
    def gen_name(self):
        todaydate = dt.datetime.now().strftime('%Y-%m-%d')
        #https://pynative.com/python-uuid-module-to-generate-universally-unique-identifiers/
        #sm_uuid = str(uuid.uuid4())[0:7]  # just 8 chars should be enough
        sm_uuid = brl_id(8)
        self.name = '{:}_{:}_{:}_{:}_{:}{:}'.format(todaydate,sm_uuid, self.descrip,self.initials,self.ttype,self.ftype)
        self.add_folder_to_fname()
        if type(self.name) != type('a string'):
            brl_error('problem generating filename')
        if '.' in self.name.replace(self.ftype,''):
            brl_error(' You cannot have a period (.) in base filename: '+ self.name.replace(self.ftype,''))
        print('Generated filename: '+self.name)
        
        
    def set_metadata(self,names, types, notes):
        N = len(names)
        if len(types) != N or len(notes) != N:
            brl_error('uneven metadata. do you need to make metadata into lists?')
        self.metadata.d['Ncols'] = str(N)     # str type for everything!
        self.metadata.d['Names'] = str(names)
        self.metadata.d['Types'] = str(types)
        self.metadata.d['Notes'] = str(notes)
        self.metadata.d['GitLatestCommit'] = get_latest_commit(folder=self.gitrepofolder)
    
    def read_oldmetadata(self,tname=None):
        md = metadata()
        if tname == None:
            tmpname = self.name
        else:
            tmpname = tname
        md.data_file_name = tmpname
        md.read()
        return md
    
    def write_metadata(self):
        self.metadata.save(self.folder)  # save into same folder as data
        
    def validate(self): 
        vis = validinputs()
        valid = True
        if self.initials == '':
            brl_error('missing initials for filename',fatal=False)
            valid = False
        if not self.ttype in vis.validtesttypes:
            brl_error('test type {:} is unknown in {:}'.format(self.ttype,vis.validtesttypes),fatal=False)
            valid = False
        if type(self.
                descrip) is not type('a string') or self.descrip == '':
            brl_error('invalid description for filename',fatal=False)
            valid = False
        for k in self.metadata.d.keys():
            if type(k) != type('string'):
                brl_error('metadata key [{:}] is not a string'.format(k))
        return valid
            
    def request_user_data(self):
        self.metadata.get_user_basics()
        
    def add_folder_to_fname(self): # if folder=='' does nothing
        if len(self.folder) > 0:
            if self.folder[-1] != '/':
                self.folder = self.folder+'/'
            self.name = self.folder + self.name
            

    # if you want to open a specific existing file,f
    #   just set MyDatafile.name = "** your filename **"
    #   before calling open. or use tname= to set a name you want
    def open(self,mode='w',tname='none_flag'):
        vis = validinputs()
        if not self.setFoldersFlag:
            brl_error('tried to open a datafile without calling set_folders() first.')
        if tname != 'none_flag':
            if mode == 'w' and os.path.exists(tname):
                brl_error('Attempting to overwrite an existing file ('+tname+') dont you want to append?)')
            self.name = tname
        if self.name == None:
            brl_error('output file name has not been set')
        if not self.validate():
            self.request_user_data()
        self.metadata.d['OpenTime'] = dt.datetime.now().strftime("%I:%M%p, %B %d, %Y")
        self.metadata.d['Nrows'] = 0
        if mode == 'w':   # write mode
            ##
            #  Check if source code is modified and optionally automatically commit it
            # find the commit data
            commit_data = self.check_code_version()
            if commit_data != '':
                self.metadata.d['GitLatestCommit'] = commit_data
            self.fd = open(self.name,mode)
            
        elif mode == 'a':   # append mode
            ##
            #  Check if source code is modified and optionally automatically commit it
            commit_data = self.check_code_version()
            # if there is a new commit, add in its info
            if commit_data != '':
                self.metadata.d['GitLatestCommit'] = self.metadata.d['GitLatestCommit'] + r' || ' + commit_data
                
            if os.path.exists(self.name):
                ## here we are updating / adding to an existing file so we need to 
                #read in and update metadata
                tmd = self.read_oldmetadata().d
                self.metadata.d['Nrows'] = tmd['Nrows']     # these two should reference the ORIGINAL open
                self.metadata.d['OpenTime']=tmd['OpenTime'] #  
                #
                # now some sanity checks
                if self.metadata.d['Ncols'] != tmd['Ncols']:
                    brl_error('Appending to a file with DIFFERENT number of columns: {:} vs {:}'.format(self.metadata.d['Ncols'],tmd['Ncols']))
                if self.metadata.d['Names'] != tmd['Names']:
                    brl_error('Appending to a file with DIFFERENT column names: {:} vs {:}'.format(self.metadata.d['Names'],tmd['Names']))
                if self.metadata.d['Types'] != tmd['Types']:
                    brl_error('Appending to a file with DIFFERENT column types: {:} vs {:}'.format(self.metadata.d['Types'],tmd['Types']))
                            
                 
            ###########################################
            ## finally, open the file in append mode
            self.fd = open(self.name,'a')
            
        else:
            brl_error('illegal log file mode (must be "a" or "w"): {:}'.format(mode))
        ##############################
        ###  set up class for data output depending on datafile type
        if self.ftype == '.csv':
            self.output_class = csv.writer(self.fd, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        elif self.ftype == '.json':
            brl_error('json data file output not yet supported')
        else:
            brl_error('trying to open unknown file type,'+self.ftype+', must be '+str(vis.validfiletypes))
            
    def close(self):
        if self.fd == None:
            brl_error('Trying to close a datafile that has not been opened yet')
        else:
            self.fd.close()   # close the file descriptor
            # now output the metadata
            self.metadata.d['CloseTime'] = dt.datetime.now().strftime("%I:%M%p, %B %d, %Y")
            #
            #  Save the metadata at very end
            #
            self.write_metadata()
            
    def write(self,data):  # TODO: figure out a way to standardize the "data" argument
        #  data:  a list of values to add to the currently open output file as one row.
        #
        if self.fd == None:
            brl_error('attempting to write data but file not open yet')
        if self.dataN > 0 and (len(data) != int(self.dataN)):
            brl_error('writing data vector of wrong length: {:} vs. {:}'.format(len(data), int(self.dataN)))
        if self.ftype == '.csv':
            ####   write data to csv file
            self.output_class.writerow(data)
            self.metadata.d['Nrows'] = str(int(self.metadata.d['Nrows'])+1)
            return
        if self.ftype == '.json':
            brl_error('.json output data files not yet supported')
            ##  write to json???
        else:
            brl_error('unknown file type: '+self.ftype)
            
    def read(self,data):  # maybe also use for reading configurations? json??
        ##
        ##  TBD a method for reading from our data files which uses
        ##    the .meta files 
        ##
        pass
        
    def check_code_version(self):
        ##
        #  Check if source code is modified and optionally automatically commit it
        #
        #
        try: # may fail if no modified files, not a git repo etc. 
            if self.gitrepofolder == '':
                modified = subprocess.check_output('git status | grep modified:',shell=True).decode('UTF-8').strip().replace('\n',' | ') 
            else:
                modified = subprocess.check_output('git status | grep modified:',cwd=self.gitrepofolder,shell=True).decode('UTF-8').strip().replace('\n',' | ') 
        except:
            print('Code is unmodified')
            modified = ''
        for dep in ast.literal_eval(self.metadata.d['Dependencies']):
            if dep in modified:
                ddep = self.gitrepofolder+dep   #  add in the folder path name
                DO_AUTOCOMM = False
                if BRL_auto_git_commit == ASK:
                    com_resp = input('       Code for {:} was modified: auto git commit?? (y/N/?):'.format(dep))
                    com_resp = com_resp.lower()
                    if com_resp == '':
                        DO_AUTOCOMM = False
                    if com_resp == '?':
                        print('''\nDo you want to automatically generate a git add/commit to reflect 
                            current state of this code? (y/N).   Quitting, please start over...\n\n''')
                        quit()
                    if com_resp == 'y':
                        DO_AUTOCOMM = True
                if BRL_auto_git_commit == ALWAYS:
                    DO_AUTOCOMM = True
                if BRL_auto_git_commit == NEVER:
                    DO_AUTOCOMM = False                        
                if DO_AUTOCOMM:
                    GIT_FAIL = False
                    try:
                        # make git add and commit the new source code.
                        #a = subprocess.check_output(['git','add',dep],cwd=self.gitrepofolder)
                        gitresp1 = subprocess.getoutput('git add ' + ddep)

                    except:
                        print('Fail 1')
                        GIT_FAIL = True
                    try: # do the commit
                        #b = subprocess.check_output(['git', 'commit', '-m', "'auto commit due to change in "+dep+"'"],cwd=self.gitrepofolder)        
                        gitresp2 = subprocess.getoutput("git commit -m 'auto commit due to change in "+ddep+"'")   
                    except:
                        print('Fail 2')
                        GIT_FAIL = True
                    if not GIT_FAIL:
                        try:
                            new_commit_info = get_latest_commit(folder=self.gitrepofolder)
                        except:
                            print('Fail 3')
                            GIT_FAIL = True
                    if GIT_FAIL:
                        brl_error('Something went wrong with git commands!')
                                        
                    brl_error('Notice: Source code was changed: auto commit has been done, metadata updated.',fatal=False)
        info = get_latest_commit(folder=self.gitrepofolder)
        return info
            
            
def get_latest_commit(folder='no folder'):
    if folder=='no folder':
        brl_error('get_latest_commit should be called with an explict folder\nUse empty string ("") for same folder as your running code')
        tmp = subprocess.check_output('git log', shell=True).decode('UTF-8').split('\n')
    else:
    #    brl_error('checking git in folder: '+folder,fatal=False)
        if folder == '':
            tmp = subprocess.check_output('git log', shell=True).decode('UTF-8').split('\n')
        else:
            tmp = subprocess.check_output('git log',cwd=folder, shell=True).decode('UTF-8').split('\n')

    return str('Git: '+tmp[0]+' '+tmp[4].strip())
    
###########################################  Configurations
#############   Parameter Files  
#
#  Store setups for experiments
#    pfname   str   parameter file name
#
#

class param_file:
    def __init__(self,pfname):
        vfs = validinputs() 
        self.name = pfname 
        self.params = {}    # values read from or written to param file
        
    
    def read(self): 
        vfs = validinputs()
        try:
            fp = open(self.name, 'r')
        except:
            brl_error('Cant open parameter file: '+self.name)
        for line in fp:
            if '#' in line:
                l2 = line.split('#')  # clear comments
            else:
                l2 = [line]
            if len(l2[0].strip()) == 0:  # there's no keyword here
                continue
            else:
                line = line.strip()
                if line != '':
                    kw,val = l2[0].split(None,1)    # get kw/value pairs
                    kw = kw.strip()
                    val = val.strip()
                    if kw in vfs.knownKeywords:
                        self.params[kw] = val
                    else:
                        brl_error('unknown keyword: '+kw,fatal=True)
    
    def __repr__(self):
        str = '----------------------------------------------\n'
        str += '{:25}{:}\n'.format('Parameter File: ',self.name)
        str += '{:25}{:}\n'.format('Dictionary:','')
        for k in self.params.keys():
            str += '       {:25}{:}\n'.format(k,self.params[k]) 
        str += '----------------------------------------------\n'
        return str

