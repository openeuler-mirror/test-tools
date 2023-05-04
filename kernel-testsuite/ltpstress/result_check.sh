#!/bin/bash
uptime
ls /var/crash

cat /proc/slabinfo | awk '{print $3*$4/1000," ",$0}' | sort -n -k 1
ps aux | sort -n -k 6 | awk '{$7="";$8="";$9="";print $0}' | grep " /"

find /var/log -type f -size +10M
find /home -type f -size +10M

cat /proc/net/netlink | wc -l

ps -A -o stat,ppid,pid,cmd | grep -e '^[Dd]'
ps -A -o stat,ppid,pid,cmd | grep -e '^[Zz]'

ls -l /proc/*/fd/* | grep delete
ulimit -a

ls $(dirname `cat /proc/sys/kernel/core_pattern`)
ls -l $(dirname `cat /proc/sys/kernel/core_pattern|awk '{print $1}'|awk -F "|" '{print $2}'`)
