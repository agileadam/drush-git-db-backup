#!/usr/bin/env python
import sys
import os
import subprocess
import argparse
import glob
import re

parser = argparse.ArgumentParser(description='Automatically backs up Drupal site databases and commits the changes to a git repo. A useful implementation is to run this via a cronjob and pipe the command to a mail application to email the output. View the source code for more help!')
parser.add_argument("-s", "--scan-dir", dest="scandir", required=True,
                  help="which directory contains your drupal sites (you can optionally \
                  traverse deeper from this root directory using the -t/--traverse argument)",
                  metavar="SCAN_DIRECTORY")
parser.add_argument("-d", "--target-dir", dest="targetdir", required=True,
                  help="write files to specific directory (the git working directory)",
                  metavar="DIRECTORY")
parser.add_argument("-t", "--traverse", dest="traverse", default=0, type=int,
                  help="how many levels deep to scan for drupal sites", metavar="N")
parser.add_argument("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="do not show output")
parser.add_argument("-c", "--commit", dest="docommit", default=False,
                  action="store_true", help="automatically add and commit the backup file changes")
parser.add_argument("--use-dirname", dest="usedirname", default=False,
                  action="store_true", help="output files as dirname.sql instead of using the database name (websites/mysite  -> websites_mysite.sql)")
args = parser.parse_args()

# Emulate the which binary
# http://stackoverflow.com/a/377028
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

# Look for Drush and store its location; quit if we cannot find it
drush_app = which('drush')
if drush_app == None:
    sys.exit("ERROR: Could not find the Drush application in $PATH. If you are \
running this from a cronjob, try setting cron's PATH to include the drush \
application.")

if args.docommit:
    # Look for Git and store its location; quit if we cannot find it
    git_app = which('git')
    if git_app == None:
        sys.exit("ERROR: Could not find the Git application in $PATH. If you are \
    running this from a cronjob, try setting cron's PATH to include the git \
    application.")

# Process a Drupal directory (dir MUST be a Drupal directory
# as we're not checking this here!)
def processDir(dir):
    os.chdir(dir)

    if args.usedirname:
        filename = dir.replace('/', '_')
    else:
        drushdb = subprocess.Popen([drush_app, 'sql-conf'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 )
        drushdb_results = drushdb.stdout.read()
        dbname_search = re.search("\[database\] => (.*)", drushdb_results, re.MULTILINE)
        if dbname_search == None:
            print "ERROR: Could not get database name for site at " + dir
            os.chdir(args.scandir)
            return
        else:
            filename = dbname_search.group(1)

    drushdump = subprocess.Popen([drush_app, 'sql-dump', '--ordered-dump', '--nocolor',
                              '--structure-tables-key=common',
                              '--result-file=' + args.targetdir.rstrip('/') + '/' + filename + '.sql'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             )
    results = drushdump.stdout.read()
    if results:
        if args.verbose:
            print results
    os.chdir(args.scandir)

# Clean up the paths to fix any problems we might
# have with user paths (e.g., --target-dir=~/xyz won't work otherwise)
args.targetdir = os.path.expanduser(args.targetdir)
args.scandir = os.path.expanduser(args.scandir)

if not os.path.exists(args.targetdir):
    sys.exit("ERROR: Could not find the target directory.")

if not os.path.exists(args.scandir):
    sys.exit("ERROR: Could not find the scan directory.")

# Store the directory from which the user is executing this script
origdir = os.getcwd()

# Move to the directory that contains the Drupal sites
os.chdir(args.scandir)

# Traverse into subdirectories until the --traverse depth is reached
count = 0
while (count <= args.traverse):
    count = count + 1
    wildcards = '*/' * count
    for name in glob.glob(wildcards + 'sites/all/modules'):
        processDir(name.replace('/sites/all/modules', ''))

# If the user used the --commit option, git add and commit the files
if args.docommit:
    os.chdir(args.targetdir)

    # Stage all of the new/changed files
    gitadd = subprocess.Popen([git_app, 'add', '*.sql'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             )
    gitadd_results = gitadd.stdout.read()
    if gitadd_results:
        if args.verbose:
            print gitadd_results

    # Commit all of the changes with a message
    gitcommit = subprocess.Popen([git_app, 'commit', '-a', '-m', 'Automatic commit'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             )
    gitcommit_results = gitcommit.stdout.read()
    if gitcommit_results:
        if args.verbose:
            print gitcommit_results

# Move back to where the user started
os.chdir(origdir)
