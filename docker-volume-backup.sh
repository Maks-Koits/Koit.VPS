#Bash script to Backup Docker Volumes
#For those who wish to use shell to backup their docker volumes.
#UPDATED WITH RESTORE DIRECTIONS, ADDED "PATH", AND FIXED CRON JOB NOT WORKING 3/6/24
#***THIS SCRIPT WILL STOP ALL DOCKER CONTAINERS RUNNING and will then RESTART ALL CONTAINERS after the backup has completed.***
#Step 1. Create the backup script.
#
#nano /path/where/you/want/to/store/backup/script.sh
#Step 2. Paste the following into the file and edit DESTINATION and SOURCEFOLDER to your needs.

#! /bin/sh
PATH=/usr/local/bin:/usr/bin:
#Script to backup docker volumes

#Stop all running docker containers
docker stop $(docker ps -q)

#Create tar.gz of docker volumes folder
BACKUPTIME=\date +%b-%d-%y\```
DESTINATION=/path/to/backup/location/$BACKUPTIME.tar.gz
SOURCEFOLDER=/path/to/docker/volumes/folder
tar -cpzf $DESTINATION $SOURCEFOLDER

#Restart all docker containers
docker restart $(docker ps -a -q)

#Delete files older than 7 days
find /share/backup/docker -mtime +7 -type f -delete
Step 3. Make the file executable

chmod +x /path/to/script.sh
Step 4 (OPTIONAL). Test the executable.

./path/to/script.sh
This will create a backup with the todays date and compress it into a tar.gz archive.

OPTIONAL STEPS BELOW:

Use CRON to schedule backups.

Step 5. Edit Cron as root.
sudo crontab -e

Step 6. Create a new line in Cron at the bottow. Visit Cron Maker for help with scheduling cron.

30 3 * * * sh /path/to/script.sh
The script will run daily at 3:30 AM.

This script will also delete backups older than 7 days. If you wish to change the amount of days to keep backups. Edit the following line in the script above and change the number 7 to whatever value you want. You can test which files this finds first before deleting anything by running the command below without the -delete flag.

find /share/backup/docker -mtime +7 -type f -delete

***How to Restore Backup***

Navigate to the location of your volume backups directoy and decompress the .tar.gz.

tar -xvzf /path/to/volumesbackup.tar.gz
Stop the container you wish to restore.

Navigate to your docker volumes location and delete the current "_data" folder or rename to "_data.old" for whichever container volume you wish to restore. Then replace the "_data" folder with the one found in the decompressed tar.gz.

Restart docker container and you should be good to go!

Feel free to offer suggestions or improvements in the comments. This is really my first attempt at making any kind of shell executable.