#!/bin/bash
#该脚本用于清理buff/cache，释放内存
 
used=`free -m | awk 'NR==2' | awk '{print $3}'`
free=`free -m | awk 'NR==2' | awk '{print $4}'`
buff_cache=`free -m | awk 'NR==2' | awk '{print $6}'`
available=`free -m | awk 'NR==2' | awk '{print $7}'`

LOG_FILE=/var/log/mem.log

echo -n "$(date '+%Y-%m-%d %H:%M:%S') " >> $LOG_FILE
echo -n "used:${used}M free:${free}M buff_cache:${buff_cache}M available:${available}M " >> $LOG_FILE

#设置free小于150M时就开始进行清理
if [ $free -le 150 ] ; then
        sync && echo 1 > /proc/sys/vm/drop_caches
        sync && echo 2 > /proc/sys/vm/drop_caches
        sync && echo 3 > /proc/sys/vm/drop_caches
        echo -n "OK" >> $LOG_FILE
else
        echo -n "free >= 150, pass." >> $LOG_FILE
fi
echo "" >> $LOG_FILE
