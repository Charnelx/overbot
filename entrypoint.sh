#!/bin/bash

echo "Starting"

# make environment variables visible to Cron
printenv > /etc/environment

# run python script every 10 minutes
# redirect output (including errors) to cron.log file
echo "*/10 * * * * /usr/local/bin/python3 /home/app/scrapper/scrap_to_db.py >> /var/log/cron.log 2>&1" > scheduler.txt

crontab scheduler.txt
crond -f