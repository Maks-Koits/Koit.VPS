#!/bin/bash

LOG_ACCESS="/var/log/nginx/access.log"
LOG_NGINX_CLEAN="/var/log/nginx/nginx_clean.log"

#while  true
#do
grep -v "node-exporter.maks-koits.site" "$LOG_ACCESS" | grep -v "portainer.maks-koits.site" > "$LOG_NGINX_CLEAN"
cat "$LOG_NGINX_CLEAN" > "$LOG_ACCESS"
rm "$LOG_NGINX_CLEAN"
#        sleep 3600
#done & disown
