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
from pathlib import Path
import brl_data
import csv
import json
import re

#############  Configurations
#
#  SUMMARY
#

#  How to treat the situation where code has changed
#   between the time a file was first opened and some data is appended
#   This flag specifies: what to do if the code has been modified AFTER
#   the file was first opened.   If ALWAYS (or user enters 'Y'), then
#   create a new commit for the code and add it to the metadata.
NEVER = 0
ASK   = 1
ALWAYS = 2
BRL_auto_git_commit = NEVER

#  metadata format:
#  True = Always save metadata as json object
#  False = old style plain ascii key/value pairs
BRL_json_metadata = True

######################   Utilities

############# create a simplistic n-char UUID
def brl_id(n):
    u = uuid.uuid4()  #
    u = str(u).replace('-','')
    m = int(n/2)
    return u[0:m] + u[-m-1:-1]


###############   Wrap the input function so it can be mocked
def t_input(message):
    return(input(message))

#############  accept some input with a default example
#        and optional list of valid responses
#  "Prefilled input" with optional validation
#   message:  prompt to user (str)
#   example:  prefilled / default value (assumed valid)
#   valids: a list of strings that input must belong to
#
def pref_input(message, example, valids=None):
    while True:
        vin = t_input(message+' ({:}):'.format(example))
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

##################################################################
#
#  some utilities for type conversion (see metadata.polish)
#
def null_conversion(x): # for str to str(!)
    if type(x) != type('hello'):
        brl_error('illegal type conversion')
    return x
def int_conv(x):
    return int(x)
def float_conv(x):
    return float(x)
def complex_conv(x):
    return complex(x)


hashmatcher = '(?<![0-9A-Fa-f])[0-9A-Fa-f]{8}(?![0-9A-Fa-f])'  # Thanks ChatGPT!!!
#   note - this matches numbers of > 8 digits(!) (not sure why)
hmc = re.compile(hashmatcher)

def getHashFromFilename(fn):
        result = hmc.findall(fn)
        if result is None:
            result = []
        #print(f'result: {result}, hv2: {hashResult}')
        return result # a list of hash codes found in the file name (comparison files have 2!)

##################################
#
#   a finder when your data files are in several dirs
#
#
class finder:
    def _init__(self):
        self.dirs = None
        self.keys = []
        #print('datadir: ', datadir)
        #print('targethash: ', targethash)

    def set_dirs(self,dlist):
        self.dirs = dlist

    def get_search_dirs(self):
        tmp = datafile('dummy', 'dummy', 'dummy')  # basically just to read the config file for the dirs
        dirs = set([tmp.data_folder] + tmp.search_folders)
        # print('debug: search folders set to: ', dirs)
        self.set_dirs(dirs)

    def findh(self,keys):
        if type(keys) != type(['xyz256']):
            keys = [keys]
        if self.dirs is None:
            brl_error('finder: You must specify some dirs/folders with .set_dirs(ds) first.')
        self.keys = keys
        # keys: a list of strings which must be contained in filename
        if len(self.dirs) < 1:
            brl_error(' file finder needs at least one directory/folder')
        if len(keys) < 1:
            brl_error(' you must specify at least one search key for finder.findh')
        files = []
        for d in self.dirs:
            # print('Looking at: ',d)
            fnames = os.listdir(d)
            for n in fnames:
                files.append([d,str(n)]) # dir, name
        matchlist = []
        for f in files:
            found = True
            for k in self.keys:
                if not k in f[1]:
                    found = False
            if found:
                matchlist.append(f)
        print(f'finder.findh: heres what I found: {matchlist}')

        return matchlist  # list of [d,fname] pairs


class validinputs:
    def __init__(self):
        # self.validtesttypes = ['simulation','single', 'longterm', 'engineering']  # too rigid - allow anything  TODO: allow user to customize
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
        self.polished = False # after reading md, convert types
         # functions to convert from strings to correct types
         #   these are set in metadata.polish()
        self.row_type_funcs = []

    def set_data_file_name(self,name):
        if (not '.csv' in name):
            brl_error('metadata filename SHOULD include .csv')
        self.data_file_name = name

    # write out metadata (OVERWRITE old metadata)
    def save(self,MDjson=BRL_json_metadata):
        if len(self.data_file_name) == 0:
            brl_error(" no data file name has been specified.")

        if MDjson:  # JSON metadata
            metadata_fname = self.data_file_name.split('.')[0] + '_meta.json'
            #print('metadata.save: about to replace: ', metadata_fname)
            metadata_fname = metadata_fname.replace('meta_meta','meta')  # glitch on append mode
            #print('metadata.save: saving metadata as json: '+metadata_fname+' (method 2)')
            metadata_fd = open(metadata_fname,'w')
            json.dump(self.d,metadata_fd,indent=3)
            metadata_fd.close()

        else:   # original ASCII format
            # derive metadata file name from datafile name
            metadata_fname = self.data_file_name.split('.')[0] + '.meta'
            #print('saving metadata as '+metadata_fname+' (ASCII)')
            metadata_fd = open(metadata_fname,'w')
            for k in self.d.keys():
                print('{0:20} "{1:}"'.format(k, str(self.d[k])),file=metadata_fd)
            metadata_fd.close()

    def validate(self):  # metadata
            valid = True
            for k in self.d.keys():
                if type(k) != type('string'):
                    brl_error('metadata key [{:}] is not a string'.format(k),fatal=False)
                    valid=False
            try:
                x = self.d['Names']
            except:
                brl_error('validate: metadata dictionary must have "Names" key',fatal=False)
                valid=False
            try:
                x = self.d['Types']
            except:
                brl_error('validate: metadata dictionary must have "Types" key',fatal=False)
                valid=False
            return valid

    def polish(self): #metadata
        #
        int_type = str(type(5))    # these have to be strings b/c json can't serialize types(!)
        float_type = str(type(3.14159))
        str_type = str(type('hello'))
        complex_type = str(type(1.0+2j))

        # intelligently convert types from string in metadata
        if not self.polished:
            #1) convert string rep of names list to real list:
            if type(self.d['Names']) == type('hello'):  # string version of list was old style
                t = self.d['Names'].replace('[','').replace(']','')
                t = t.replace("'","")
                nameslist = t.split(',')
                for i,n in enumerate(nameslist):
                    nameslist[i] = n.strip()
                self.d['Names'] = nameslist  # a real list of strings instead of '[ x,y,etc]'

            #2) assign type conversion functions to each col based on metadata:
            try:
                x = self.d['Types']
            except:
                print('No Types tag????')
                print(self)
                brl_error('no types tag')

            ttypes = self.d['Types']

            # Currently d['Types'] is stored as a list of string-converted types.  Some older files
            #  store the list converted into one big string
            if  type(self.d['Types']) == type('hello'):  # if old one-string version,
                t = self.d['Types'].replace('[','')
                t = t.replace(']','')
                t = t.replace('"','')
                ttypes = t.split(',')

            self.row_type_funcs = []  # Build a list of functions to convert each data col in a row
            for t in ttypes:
                t = t.strip()
                if t == int_type:
                    self.row_type_funcs.append(int_conv)  #int_conv etc defined up top.
                elif t == float_type:
                    self.row_type_funcs.append(float_conv)
                elif t == str_type:
                    self.row_type_funcs.append(null_conversion)
                elif t == complex_type:
                    self.row_type_funcs.append(complex_conv)
                else:
                    brl_error('metadata.polish: trying to convert an unknown type: '+t)

            #3) derive proper string format tags for each col.
            self.row_fmt_tags = []
            for t in ttypes:
                t=t.strip()
                if t == int_type:
                    self.row_fmt_tags.append('{:10d}')
                if t == float_type:
                    self.row_fmt_tags.append('{:10.2f}')
                if t == str_type:
                    self.row_fmt_tags.append('{:10}')
                if t == complex_type:
                    self.row_fmt_tags.append('{:8.4f}')
            self.polished = True
            return
        #print('already polished: ',self.data_file_name.replace('.csv',''))
        return



    # this reads in the metadata from a file (which might include comments)
    #  Note that dictionary will still contain string values.  e.g. Lists must
    #  be parsed, ints must be cast etc.
    #
    #  sometimes the metadata file might be missing but we want to be robust to that
    #   update June 23:  no - we are not going to be robust to a non existent md file.
    def read(self, MDjson=BRL_json_metadata):
        if MDjson:
            metadata_fname = self.data_file_name.split('.')[0] + '_meta.json'
        else:
            metadata_fname = self.data_file_name.split('.')[0] + '.meta'
            metadata_fd = False
        # correct append mode glitch
        metadata_fname = metadata_fname.replace('meta_meta', 'meta')

        try:
            print('metadata.read: Opening: ', metadata_fname)
            metadata_fd = open(metadata_fname,'r')
        except:
            brl_error("Can't open metadata file: [{:}]".format(metadata_fname),fatal=True)

        if MDjson:  # JSON formatted metadata.
            self.d = json.load(metadata_fd)
            metadata_fd.close()
            self.polish()
            return True
        else:    # plain ASCII format (deprecated)
            #print('reading metadata from '+metadata_fname)
            for line in metadata_fd:
                if '#' in line:
                    l1, l2 = line.split('#')
                else:
                    l1 = line
                l1 = l1.strip()
                if len(l1)>0:
                    #print('MD file line: ', l1)
                    try:
                        w1, w2 = l1.split(' ',1)  # white space split
                    except:
                        w1 = l1
                        w2 = ''
                    w1 = w1.strip()
                    w2 = w2.strip()
                    self.d[w1] = w2.replace('"','')
            metadata_fd.close()
            # polish the data
            self.polish()
            return True


    def get_user_basics(self):
        vis = validinputs()
        print('\nPlease enter basic information for the metadata you would like to create:')
        smart_query(self.d,'Ncols',msg='How many columns of data?', example=4) # str type for everything!
        nc = int(self.d['Ncols'])
        # hack to work with brl_data_min_example.py!!
        itype = str(type(5))
        ftype = str(type(3.1416))
        types = [itype] + 3*[ftype]
        names = ['N','X1','Y1','Z1']
        smart_query(self.d,'Types',msg='Column Types (as list [...]):', example=types) # must convert types to strings (per json pkg)
        smart_query(self.d,'Names',msg='Column names (as list [...]):', example=names)
        smart_query(self.d,'Description',msg='...  description ...')
        smart_query(self.d,'Notes',msg='Notes: (...):', example='...some notes...')
        #smart_query(self.d,'GitLatestCommit',example='Not Recorded')
        smart_query(self.d,'Initials', msg='Your Initials',example='AB')
     #   smart_query(self.d,'OpenTime', msg='Creation Date:', example= '07-March-2017')
     #   smart_query(self.d,'FileType', example='.csv or .json',valids=vis.validfiletypes)
        smart_query(self.d,'TestType', example='simulation')


    def __repr__(self):
        str = '----------------------------------------------\n'
        str += '{:25}{:}\n'.format('Experiment Metadata: ', self.data_file_name.replace('.csv',''))
        str += '{:25}{:}\n'.format('Dictionary:','')
        for k in self.d.keys():
            str += '       {:25}{:} [{:}]\n'.format(k,self.d[k],type(self.d[k]))
        str += '\nmetadata polished: {:}'.format(self.polished)
        str += '\n----------------------------------------------\n'
        return str

#
#          Data
#

#############  Log file for data storage
#
#  creation and I/O for numerical datafiles
#   TODO: create a class for image files and a class for video files

class datafile:
    def __init__(self, descrip_str, user_initials, testtype):
        self.descrip = descrip_str
        self.initials = user_initials
        self.ttype = testtype  # defined in "validinputs" class
        self.ftype = '.csv'  # only .csv at this point
        self.fd = None  # file descriptor
        self.name = ''    # can override this any time
        self.hashcode=brl_id(8)
        self.accessmode=None  # set by self.open()
        self.data_folder = ''  # can direct datafiles into a folder
        self.search_folders = []  # other folders that finder class can search for data files
        self.git_repo_folder = ''   # place where current code lives
        self.output_class = None  # for example:  csv.writer()
        self.metadata = metadata()
        self.metadata.d['Ncols'] = 0 # correct length of data vector
        self.metadata.d['Nrows'] = 0 # number of rows of data written so far.
        self.dataN = 0
        self.setDataFoldersFlag = False
        self.config_file_used = False
        #
        #  read config file for basic parameters (so they don't have to be coded)
        #
        # 1) find brl_data.conf  (e.g. ~, . , ./brl_data/, etc) use newest of files found
        # 2) parse it and set key quantities (initials, metadata.d['Name'], testtype (self.ttype), etc )
        # done
        if self.read_brl_data_config():
            self.config_file_used = True
            print('Read brl_data_config file.')
        else:
            print('No brl_data_config file was found.')
            self.config_file_used = False
            print('brl_data.py: Got Here!',flush=True) ###################################################################
            self.set_data_folder(str(Path.cwd()))  # '.'
            self.set_git_folder(str(Path.cwd()))   # '.'
            print('    set folders to defaults:')
            print(f'        data: {self.data_folder}')
            print(f'         git: {self.git_repo_folder}')

    def read_brl_data_config(self):
        #
        #  Find the latest fresh config file
        #  places to look for it.
        dirs = [Path.home(), Path.cwd(), Path.cwd() / 'brl_data']
        # check them:
        existing_files = []
        for dir in dirs:
            con_path = dir / 'brl_data.conf'
            if con_path.is_file():
                existing_files.append(con_path)
        if existing_files:
            newestCF = max(existing_files, key=lambda p: p.stat().st_mtime)
        else:
            return False
        fp = open(newestCF, 'r')
        for line in fp:
            wds = line.split()
            # print(f'TESTING: config line: {wds}')
            if len(wds)<1:
                break
            if len(wds)==1:
                brl_error(f'unknown config input: {wds}',fatal=False)

            if wds[0] == 'user_name':
                self.metadata.d['UserName']= ' '.join(wds[1:])
                self.initials = ''
                for n in wds[1:]: # get initials
                    self.initials += n[0].upper()
            if wds[0] == 'data_folder':
                self.set_data_folder(wds[1])

            if wds[0] == 'search_folder':
                self.search_folders.append(wds[1])

            if wds[0] == 'git_folder':
                self.set_git_folder(wds[1])

            if wds[0] == 'test_type':
                self.ttype = wds[1]

            if wds[0] == 'new_metadata' and len(wds)==3:
                self.metadata.d[wds[1]]=wds[2]

        return True

    def set_folders(self, datafolder, gitfolder):
        self.set_data_folder(datafolder)
        self.set_git_folder(gitfolder)

    def set_data_folder(self, datafolder):
        if self.fd:
            brl_error('Its too late to change folder to'+datafolder+'. datafile already open')
        if '.' in datafolder:
            brl_error('You cannot use . in folder name: ' + datafolder)
        dirsOK = True
        #'' is allowed, to mean the current directory
        if (not os.path.isdir(datafolder)) and datafolder != '':
            dirsOK = False
        if not dirsOK:
            print('\n\n')
            print(f'    you have set the datafolder to: [{datafolder}] but that folder does not exist.')
            print(f'        suggestion:  > mkdir {datafolder}')
            print('\n\n')
            brl_error(f'data_folder {datafolder} does not exist')
        # can only be done after folder is set
        self.setDataFoldersFlag = True
        self.data_folder = datafolder
        self.gen_name()  # generate output filename
        self.metadata.data_file_name = self.name

    def set_git_folder(self,gitfolder):
        dirsOK = True
        if (not os.path.isdir(gitfolder)) and  gitfolder != '':
            dirsOK = False
        if not dirsOK:
            brl_error(f'git_folder {gitfolder} does not exist')
        # can only be done after folder is set
        self.git_repo_folder = gitfolder
        self.metadata.d['GitLatestCommit'] = get_latest_commit(folder=self.git_repo_folder)


    def set_both_filenames(self, newname):
        self.name = newname
        self.metadata.set_data_file_name(newname)

    def set_filenames(self,newname):
        self.name = newname

    def gen_name(self):
        todaydate = dt.datetime.now().strftime('%Y-%m-%d')
        #https://pynative.com/python-uuid-module-to-generate-universally-unique-identifiers/
        #sm_uuid = str(uuid.uuid4())[0:7]  # just 8 chars should be enough
        self.name = '{:}_{:}_{:}_{:}_{:}{:}'.format(todaydate,self.hashcode, self.descrip,self.initials,self.ttype,self.ftype)
        self.add_folder_to_fname()
        if type(self.name) != type('a string'):
            brl_error('problem generating filename')
        if '.' in self.name.replace(self.ftype,''):
            brl_error(' You cannot have a period (.) in base filename: '+ self.name.replace(self.ftype,''))
        #print('Generated filename: '+self.name)


    def set_metadata(self,names, types, notes):
        N = len(names)
        if len(types) != N or len(notes) != N:
            print(f'{len(names)} Names, {len(types)} Types, {len(notes)} notes')
            brl_error('uneven metadata. do you need to make metadata into lists?')
        for i,t in enumerate(types):
            types[i] = str(t)    # .json can't serialize types
        self.metadata.d['Ncols'] = N
        self.metadata.d['Names'] = names
        self.metadata.d['Types'] = types
        self.metadata.d['Notes'] = notes
        self.metadata.d['GitLatestCommit'] = get_latest_commit(folder=self.git_repo_folder)

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
        self.metadata.save()  # save into same folder as data

    def validate(self): #datafaile
        vis = validinputs()
        valid = True
        #print('df.validate: Validating: ',self.name)
        if not( len(self.name) > 0 and os.path.exists(self.name)): # skip if reading or appending exiting file
            if self.initials == '':
                brl_error('missing initials for filename',fatal=False)
                valid = False
            # if not self.ttype in vis.validtesttypes:
            #     brl_error('test type {:} is unknown in {:}'.format(self.ttype,vis.validtesttypes),fatal=False)
            #     valid = False
            if type(self.descrip) is not type('a string') or self.descrip == '':
                brl_error('invalid description for filename',fatal=False)
                valid = False
            if not self.metadata.validate():
                valid=False
        return valid

    def request_user_data(self):
        self.metadata.get_user_basics()

    def add_folder_to_fname(self): # if folder=='' does nothing
        if len(self.data_folder) > 0:
            if self.data_folder[-1] != '/':
                self.data_folder = self.data_folder+'/'
            self.name = self.data_folder + self.name


    # if you want to open a specific existing file,f
    #   just set MyDatafile.name = "** your filename **"
    #   before calling open. or use tname= parameter
    def open(self,mode='w',tname=None):
        vis = validinputs()
        self.accessmode=mode
        #print('opening: ', tname, ' in ', vis.validfiletypes)
        if self.ftype not in vis.validfiletypes:
                brl_error('trying to open unknown file type,'+self.ftype+', must be '+str(vis.validfiletypes))
        if not self.setDataFoldersFlag:
            brl_error('tried to open a datafile without setting up data directory first.')
        if tname != None:
            self.name = tname
            if mode == 'w' and os.path.exists(tname):
                brl_error('Attempting to overwrite an existing file ('+tname+') dont you want to append?)')
            if mode == 'r' and not os.path.exists(tname):
                brl_error('Attempting to read a non-existing file ('+tname+')')
        if self.name == None:
            brl_error('file name has not been set')
        if not self.validate():
            print('\nAutomatically prompting you for metadata:')
            self.request_user_data()
        self.topen = dt.datetime.now()
        self.metadata.d['OpenTime'] = self.topen.strftime("%I:%M:%S%p, %B %d, %Y")
        self.metadata.d['Nrows'] = 0
        if self.accessmode == 'w':   # write mode
            ##
            #  Check if source code is modified and optionally automatically commit it
            # find the commit data
            commit_data = self.check_code_version()
            if commit_data != '':
                self.metadata.d['GitLatestCommit'] = commit_data
            self.fd = open(self.name,mode)
                ##############################
            ###  set up class for data output depending on datafile type
            if self.ftype == '.csv':
                self.output_class = csv.writer(self.fd, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            elif self.ftype == '.json':
                brl_error('json data file output not yet supported')

        elif self.accessmode == 'a':   # append mode
            if tname is None and self.name == '':
                brl_error('opening in append mode without a filename')
            if self.name == '':
                self.name = self.tname
            ##
            #  Check if source code is modified and optionally automatically commit it
            commit_data = self.check_code_version()
            # if there is a new commit, add in its info
            if commit_data != '':
                self.metadata.d['GitLatestCommit'] = self.metadata.d['GitLatestCommit'] + r' || ' + commit_data

            if os.path.exists(self.name):
                ## here we are updating / adding to an existing file so we need to
                #read in and update metadata
                tmmd = self.read_oldmetadata()
                tmd = tmmd.d   # get old metadata dictionary
                self.metadata.d['Nrows'] = tmd['Nrows']     # these two should reference the ORIGINAL open
                # self.topen = tmmd.topen #time format
                self.metadata.d['OpenTime']=tmd['OpenTime'] #
                self.topen = dt.datetime.strptime(tmd['OpenTime'], "%I:%M:%S%p, %B %d, %Y")
                #
                # now some sanity checks
                if self.metadata.d['Ncols'] != tmd['Ncols']:
                    brl_error('Appending to a file with DIFFERENT number of columns: {:} vs {:}'.format(self.metadata.d['Ncols'],tmd['Ncols']))
                if str(self.metadata.d['Names']) != str(tmd['Names']):
                    brl_error('Appending to a file with DIFFERENT column names: {:} vs {:}'.format(self.metadata.d['Names'],tmd['Names']))
                if self.metadata.d['Types'] != tmd['Types']:
                    brl_error('Appending to a file with DIFFERENT column types: {:} vs {:}'.format(self.metadata.d['Types'],tmd['Types']))
            else:
                brl_error('Attempting to append to a non-existent file: '+self.name)
            ###########################################
            ## finally, open the file in append mode
            self.fd = open(self.name,'a')
            ###  set up class for data output depending on datafile type
            if self.ftype == '.csv':
                self.output_class = csv.writer(self.fd, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            elif self.ftype == '.json':
                brl_error('json data file output append not yet supported')

        elif self.accessmode == 'r':  # read in a datafile's data and metadata
            if not os.path.exists(self.name):
                brl_error('Attempting to read from a non-existent file: '+self.name)
            # set up a reader
            ###  set up class for data output depending on datafile type
            if self.ftype == '.csv':
                self.fd = open(self.name, 'r',newline='')
                self.reader = csv.reader(self.fd, delimiter=',',quotechar='"')
            elif self.ftype == '.json':
                brl_error('json data file reading not yet supported (only for metadata)')
            else:
                brl_error('Attempting to read a file that does not exist: ' + self.name)
            #store the hashcode which is not known when open for reading except in filename
            self.hashcode = self.name.split('/')[-1].split('_')[1] # get hash code from name
            # get the metadata about the file we are reading
            self.metadata = self.read_oldmetadata()
            self.metadata.polish()  # convert str metadata values to their types
        else:
            brl_error('illegal brl_data file mode (must be "a", "r", or "w"): {:}'.format(mode))

    # convert data row from strings to correct types
    def type_row(self,row):
        if not self.metadata.polished:
            print( 'len(Names), d.["Ncols"]: ',len(self.metadata.d['Names']),self.metadata.d['Ncols'])
            brl_error('metadata.typerow: must polish() the metadata before reading')
        for i,d in enumerate(row):
            row[i] = self.metadata.row_type_funcs[i](d) # convert each col correctly
        return row

    # print a row with formatting based on the md.d['Types']
    def print_row(self,row,ncc=10):
        if not self.metadata.polished:
            brl_error('must polish metadata before printing a row')
        print('  ',end='')
        row = self.type_row(row) # convert the types
        for i,d in enumerate(row):
            f_tag = self.metadata.row_fmt_tags[i]
            print(f_tag.format(d), end='')
        print('')
    def print_header(self,ncc=10):
        #"Names": "['d1', 'd2', 'd3', 'd4']",
        print(' '*(ncc-1),end='')
        if not self.metadata.polished:
            brl_error('must polish metadata before printing a row')
        for n in self.metadata.d['Names']:
            print('{:10}'.format(n),end='')
        print('')

    def close(self):
        if self.fd == None:
            brl_error('Trying to close a datafile that has not been opened yet')
        else:
            self.fd.close()  # close the datafile
            if self.accessmode in ['w','a']:
                # now output the new metadata if writing or appending only
                rightnow = dt.datetime.now()
                self.metadata.d['CloseTime'] = rightnow.strftime("%I:%M:%S%p, %B %d, %Y")
                duration = rightnow - self.topen
                self.metadata.d['File Duration'] = duration.total_seconds()
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
            self.metadata.d['Nrows'] = int(self.metadata.d['Nrows'])+1
            return
        if self.ftype == '.json':
            brl_error('.json output data files not yet supported')
            ##  write to json???
        else:
            brl_error('unknown file type: '+self.ftype)

    def check_code_version(self):
        ##
        #  Check if source code is modified and optionally automatically commit it
        #
        #
        try: # may fail if no modified files, not a git repo etc.
            modified = subprocess.check_output('git status | grep modified:',cwd=self.git_repo_folder,shell=True).decode('UTF-8').strip().replace('\n',' | ')
        except:
            modified = 'None'

        print('Modification status of code: ',modified)
        for dep in ast.literal_eval(self.metadata.d['Dependencies']):
            if dep in modified:
                DO_AUTOCOMM = False
                if BRL_auto_git_commit == ASK:
                    com_resp = input('       Code for {:} was modified: auto git commit?? (Y/n/?):'.format(dep))
                    if com_resp == '':
                        DO_AUTOCOMM = True
                    if com_resp == '?':
                        print('''\nDo you want to automatically generate a git add/commit to reflect
                            current state of this code? (Y/n).   Quitting and starting over...\n\n''')
                        quit()
                    if com_resp.lower() != 'n':
                        DO_AUTOCOMM = True
                if BRL_auto_git_commit == ALWAYS:
                    DO_AUTOCOMM = True
                if BRL_auto_git_commit == NEVER:
                    DO_AUTOCOMM = False
                if DO_AUTOCOMM:
                    GIT_FAIL = False
                    try:
                        # make git add and commit the new source code.
                        a = subprocess.check_output(['git','add',dep],cwd=self.git_repo_folder)
                    except:
                        print('Fail 1')
                        GIT_FAIL = True
                    try: # do the commit
                        b = subprocess.check_output(['git', 'commit', '-m', "'auto commit due to change in "+dep+"'"],cwd=self.git_repo_folder)
                    except:
                        print('Fail 2')
                        GIT_FAIL = True
                    try:
                        new_commit_info = get_latest_commit(folder=self.git_repo_folder)
                    except:
                        print('Fail 3')
                        GIT_FAIL = True
                    if GIT_FAIL:
                        brl_error('Something went wrong with git commands!')

                    brl_error('Notice: Source code was changed: auto commit has been done, metadata updated.',fatal=False)
        info = get_latest_commit(folder=self.git_repo_folder)
        return info


def get_latest_commit(folder='no folder'):
    if folder=='no folder':
        brl_error('get_latest_commit should be called with an explict folder')
    else:
        if folder=='':
            if os.name == 'posix':  # Linux  # thanks ChatGPT!!
                folder = subprocess.check_output('pwd',shell=True).strip()
            elif os.name == 'nt':  # Windows
                folder = subprocess.check_output('cd',shell=True).strip()

    #    brl_error('checking git in folder: '+folder,fatal=False)
        tmp = subprocess.check_output('git log',cwd=folder, shell=True).decode('UTF-8').split('\n')
    return str('Git: '+tmp[0]+' '+tmp[4].strip())

###########################################  Configurations
#############   Parameter Files
#
#  Store setups for experiments
#    pfname   str   parameter file name
#
#    Parmeter files are simple key-value pairs
#    You can make up any keys you want.
#    '#' can be used to put comments in your paramfiles
#

class param_file:
    def __init__(self,pfname):
        vfs = validinputs()
        #validPfTypes = ['production','communication']
        #self.production_keywords= ['weekdays','ops_per_day', 'duration_mean','duration_sd','start_hour','end_hour','end_date','ename']  # production keywords
        #self.communication_keywords = ['command_nbytes','feedback_nbytes']  # coms. keywords
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
        fp.close()

    def __repr__(self):
        str = '----------------------------------------------\n'
        str += '{:25}{:}\n'.format('Parameter File: ',self.name)
        str += '{:25}{:}\n'.format('Dictionary:','')
        for k in self.params.keys():
            str += '       {:25}{:}\n'.format(k,self.params[k])
        str += '----------------------------------------------\n'
        return str

