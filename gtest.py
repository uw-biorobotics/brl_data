# git testing

import brl_data as bd
import sys, os, subprocess, ast

#xx

md = bd.metadata()

modified = subprocess.check_output('git status | grep modified:',shell=True).decode('UTF-8').strip().replace('\n',' | ')

print( 'Git modified: ', modified)

for dep in ast.literal_eval(md.d['Dependencies']):
    print('looking at dependency: ', dep)
    try:
        # make git add and commit the new source code.
        gitresp1 = subprocess.check_output(['git','add',dep])
        print('STEP 1: ', gitresp1)
    except:
        print('Fail 1')
        GIT_FAIL = True
    try: # do the commit
        gitresp2 = subprocess.check_output(['git', 'commit', '-m', "'auto commit due to change in "+dep+"'"],cwd=self.gitrepofolder)                    
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
        bd.brl_error('Something went wrong with git commands!')
