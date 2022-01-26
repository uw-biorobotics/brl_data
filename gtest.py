# git testing

import brl_data as bd
import sys, os, subprocess, ast

#xxx

md = bd.metadata()

modified = subprocess.check_output('git status | grep modified:',shell=True).decode('UTF-8').strip().replace('\n',' | ')

print( 'Git modified: ', modified)

for dep in ast.literal_eval(md.d['Dependencies']):
    GIT_FAIL = False
    print('looking at dependency: ', dep)
    try:
        # make git add and commit the new source code.
        gitresp1 = subprocess.check_output(['git','add',dep],stderr=subprocess.STDOUT)
        print('STEP 1: ', str(gitresp1))
    except subprocess.CalledProcessError as cpe:
        print('Fail 1',cpe)
        GIT_FAIL = True
    try: # do the commit
        gitresp2 = subprocess.check_output(['git', 'commit', '-m', "'auto commit due to change in "+dep+"'"])   
        print('Step 2: ', str(gitresp2))
    except subprocess.CalledProcessError as cpe:
        print('Fail 2',cpe)
        GIT_FAIL = True
    if not GIT_FAIL:
        try:
            new_commit_info = get_latest_commit()
        except subprocess.CalledProcessError as cpe:
            print('Fail 3',cpe)
            GIT_FAIL = True
    if GIT_FAIL:
        bd.brl_error('Something went wrong with git commands!')
