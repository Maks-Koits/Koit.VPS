#!/bin/bash

logfile=./requests.log
tempfile=./tempfile
tempfile2=./tempfile2
count_to_ban=500
list_of_patterns=".git/|wp-config.php|/databases.zip|/.env|/www.zip|/xmlrpc.php"

#grep -Ei $list_of_patterns "$logfile" | awk -F ' - ' '{print $1}' | awk -F ', ' '{print $1}' | awk '{ gsub("\"", ""); print }' | uniq -c > "$tempfile"
#grep -Ei $list_of_patterns "$logfile" | awk -F ' ' '{print $24}' | awk '{ gsub("\"", ""); print }' | uniq -c > "$tempfile"

grep -Ei $list_of_patterns "$logfile" | awk -v RS='([0-9]{1,3}\\.){3}[0-9]{1,3}' 'RT{print RT}' | grep -Ev '169\.254\.[0-9]{1,3}\.[0-9]{1,3}' \
| sort -n | uniq -c | sort -n | awk -v count="$count_to_ban" '$1 > count { print }' > "$tempfile"
echo '--------------------'
echo 'count of ip-s:'
cat $tempfile
echo '--------------------'
echo "ip-s more then ${count_to_ban} for ban:"
awk '{ if($1 >= '$count_to_ban' ) {print $2}}' $tempfile  > $tempfile2
echo "list of patterns: ${list_of_patterns}"
cat $tempfile2
echo '--------------------'
rm $tempfile $tempfile2
