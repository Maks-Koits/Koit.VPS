#!/bin/bash

logfile=./request.log
tempfile=./tempfile
tempfile2=./tempfile2
count_to_ban=50
list_of_patterns=".git/|wp-config.php|/databases.zip|/.env|/www.zip"

grep -Ei $list_of_patterns "$logfile" | awk -F ' - ' '{print $1}' | awk -F ', ' '{print $1}' | awk '{ gsub("\"", ""); print }' | uniq -c > "$tempfile"
echo '--------------------'
echo 'count of ip-s:'
sort -n "$tempfile"
echo '--------------------'
echo 'ip-s for ban:'
awk '{ if($1 >= '$count_to_ban' ) {print $2}}' $tempfile  > $tempfile2
cat $tempfile2
echo '--------------------'
rm $tempfile $tempfile2


