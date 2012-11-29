This is a python script that scans directories for Drupal sites and uses Drush to grab database backups for each site. It will also automatically git add/commit the changes.

*The first time you run the script you should run it with the -h or --help option.*

# Requirements

* Drush
* Git
* Python (at least version 2.7)

# Configuration
The "--structure-tables-key=common" option will be used for the sql-dump operation. This means you can create a drushrc.php file to exclude data from certain tables. See http://drush.ws/examples/example.drushrc.php for more information. I suggest doing this per-site (create sites/all/drush/drushrc.php).

If you don't want any tables to be skipped, either remove that line from my code, or empty the array in your drushrc.php file like this:

<code>$options['structure-tables']['common'] = array();</code>

If you want to exclude data from more than just the "common" tables (cache, watchdog, etc.), simply add table names to the array or create a new array and merge into the default.

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

<code>15  2   *   *   *   /usr/local/bin/python2.7 /usr/local/bin/drush-git-db-backup.py</code>
<code>--commit --scan-dir=/webapps/ --target-dir=/db_backups/</code>
<code>-t 1 | mail -s "Drush DB Backup on server123" agileadam@gmail.com</code>
