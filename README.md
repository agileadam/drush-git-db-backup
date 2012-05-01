This is a python script that scans directories for Drupal sites and uses Drush to grab database backups for each site. It will also automatically git add/commit the changes.

*The first time you run the script you should run it with the -h or --help option.*

# Requirements

* Drush
* Git
* Python (at least version 2.7)

# Cronjobs
One of the main reasons to use a script like this is to have automatic, daily git commits of Drupal site database changes.

*If you're running the script from a cronjob, make sure that Drush and Git are somewhere in the cron user's $PATH.*

Here's an example cronjob (all on a single line):

* It runs every day at 02:15
* The output is emailed to agileadam@gmail.com
* The Drupal sites are located up to 1 level below /webapps/
* The backup files are saved to /db_backups/
* The --target-dir is a git repository
* The backed-up files will be automatically added / committed to git

<code>15  2   *   *   *   /usr/local/bin/python2.7 /usr/local/bin/drush_backup_git.py</code>
<code>--commit --scan-dir=/webapps/ --target-dir=/db_backups/</code>
<code>-t 1 | mail -s "Drush DB Backup on server123" agileadam@gmail.com</code>
