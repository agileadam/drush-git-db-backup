#!/usr/bin/env python
#
# Cronjob example (single line):
# /usr/local/bin/python2.7 /usr/local/bin/drush_backup_git.py --scan-dir=/webapps/
#      --target-dir=/db_backups/ -t 1 | mail -s "Drush DB Backup on server123" agileadam@gmail.com

import sys
import os
import subprocess
import argparse
import glob

parser = argparse.ArgumentParser(description='Automatically backs up Drupal site databases and commits the changes to a git repo. Outputs a report (to screen or file) that shows the success/failure of each backup. A popular implementation is to run this via a cronjob and pipe the command to a mail application to email the output. View the source code for more help!')
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
    sys.exit("Couldn't not find the Drush application in $PATH. If you are \
running this from a cronjob, try setting cron's PATH to include the drush \
application.")

# Process a Drupal directory (dir MUST be a Drupal directory
# as we're not checking this here!)
def processDir(dir):
    os.chdir(dir)
    drush = subprocess.Popen([drush_app, 'sql-dump', '--ordered-dump',
                              '--result-file=' + args.targetdir + '/' + dir + '.sql'],
                             stdout=subprocess.PIPE,
                             )
    results = drush.stdout.read()
    if results:
        if args.verbose:
            print results
    os.chdir(args.scandir)

# Clean up the paths to fix any problems we might
# have with user paths (--target-dir=~/xyz won't work otherwise)
args.targetdir = os.path.expanduser(args.targetdir)

# Clean up the paths to fix any problems we might
# have with user paths (--dir=~/xyz won't work otherwise)
args.scandir = os.path.expanduser(args.scandir)

# Store the directory from which the user is executing this script
# so we can store a file (if they use -f/--file) relative to this directory
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

# Move back to where the user started
os.chdir(origdir)
