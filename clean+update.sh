#!/bin/bash
# Standard update and clear
# Removes old revisions of snaps
# CLOSE ALL SNAPS BEFORE RUNNING THIS

# Функция для конвертации размера из байт в человеко-читаемый формат
bytesToHuman() {
  local bytes=$1
  local -a suffixes=('B' 'KB' 'MB' 'GB' 'TB' 'PB')

  if (( bytes == 0 )); then
    echo "0 Bytes"
    return
  fi
  local i=0
  local size=$(( bytes ))
  while (( size > 1024 )); do
    size=$(( size / 1024 ))
    (( i++ ))
  done
  echo "${size} ${suffixes[i]}"
}

# Функция для получения занятого места на диске
getDiskUsage() {
  local usage=$(df -B1 / | awk 'NR==2 {print $3}')
  echo "$usage"
}

# Функция
spinner() {
    local pid=$1
    printf "["
    while kill -0 $1 2> /dev/null; do
        printf "▓"
        sleep .25
    done
    printf "]\n"
}

# Получение начального значения занятого места
initialUsage=$(getDiskUsage)

# cleaning script
echo "---------------updating packages---------------"
apt update >/dev/null 2>&1 & spinner $!
echo "--------------installing packages--------------"
apt -y upgrade >/dev/null 2>&1 & spinner $!
echo "----------------refreshing snaps---------------"
snap refresh >/dev/null 2>&1 & spinner $!
echo "-----------app's and snap's cleaning-----------"
apt -y autoremove >/dev/null 2>&1 & spinner $!
set -eu
snap list --all | awk '/disabled/{print $1, $3}' |
    while read snapname revision; do
        snap remove "$snapname" --revision="$revision"
    done >/dev/null 2>&1
rm -r /var/lib/snapd/cache/* >/dev/null 2>&1 || true
rm -r /var/lib/swapspace/* >/dev/null 2>&1 || true
echo "-------------old kernel cleaning---------------"
apt-get purge $(dpkg -l 'linux-*' | sed '/^ii/!d;/'"$(uname -r \
| sed "s/\(.*\)-\([^0-9]\+\)/\1/")"'/d;s/^[^ ]* [^ ]* \([^ ]*\).*/\1/;/[0-9]/!d' | head -n -1) -y >/dev/null 2>&1
update-grub >/dev/null 2>&1 & spinner $!
echo "---------docker builder cache cleaning---------"
docker builder prune -af >/dev/null 2>&1 & spinner $!
# Получение значения занятого места после выполнения команды
finalUsage=$(getDiskUsage)
# Вычисление разницы в использовании места на диске
difference=$(( finalUsage - initialUsage ))
# Конвертация разницы в человеко-читаемый формат
humanDifference=$(bytesToHuman $difference)
# Вывод результата
echo "-------------------done!-----------------------"
echo "cleared disk space: $humanDifference "