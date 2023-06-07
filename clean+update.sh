#!/bin/bash
# Standard update and clear
# Removes old revisions of snaps
# CLOSE ALL SNAPS BEFORE RUNNING THIS
echo "-------------------------------------"
echo "------poluchenie spiska paketov------"
echo "-------------------------------------"
apt -y update
echo "-------------------------------------"
echo "----------ustanovka paketov----------"
echo "-------------------------------------"
apt -y upgrade
snap refresh
echo "-------------------------------------"
echo "------ochistka paketov app i snap----"
echo "-------------------------------------"
apt -y autoremove
set -eu
snap list --all | awk '/disabled/{print $1, $3}' |
    while read snapname revision; do
        snap remove "$snapname" --revision="$revision"
    done
rm -rf /var/lib/snapd/cache/*
echo "-------------------------------------"
echo "--------udaleniye stari yader--------"
echo "-------------------------------------"
apt-get purge $(dpkg -l 'linux-*' | sed '/^ii/!d;/'"$(uname -r | sed "s/\(.*\)-\([^0-9]\+\)/\1/")"'/d;s/^[^ ]* [^ ]* \([^ ]*\).*/\1/;/[0-9]/!d' | head -n -1) -y
update-grub
echo "-------------------------------------"
echo "--------udalenie cache docker--------"
echo "-------------------------------------"
docker builder prune -af
echo "-------------------------------------"
echo "----------------done!----------------"
echo "-------------------------------------"