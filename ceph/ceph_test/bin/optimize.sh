#!/bin/bash
# Copyright (c) 2023. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   hekeming
# @Contact   :   hk16897@126.com
# @Date      :   2023/07/03
# @License   :   Mulan PSL v2
# @Desc      :   Test SSH link
# ############################################
root_path=$(cd $(dirname $0)/../||exit 1;pwd)
source ${root_path}/conf/cluster_info.cfg
recovery_file="/root/optimize_recovery.log"

optimize()
{
for server in ${server_list[@]}
do
  echo ${server} optimize
  data_disk_list=($(ssh ${server} "lsblk|grep disk |grep -v nvme|grep -v \$(lsblk|grep /boot/efi|awk '{print \$1}'|grep -Eo '[a-zA-Z]+')|awk '{print \$1}'|grep sd"))
  recovery_file_flag=$(ssh ${server} "ls ${recovery_file} &>/dev/null;echo \$?")
  if [ "${recovery_file_flag}" != "0" ];then
    scheduler=$(ssh ${server} "cat /sys/class/block/sd*/queue/scheduler|grep -Eo '\[.+?\]'|awk -F'[][]' '{print \$2}'|sort -u|tail -n 1")
    queue_depth=$(ssh ${server} "cat /sys/class/block/sd*/device/queue_depth|sort -u|tail -n 1")
    nr_requests=$(ssh ${server} "cat /sys/block/sd*/queue/nr_requests|sort -u|tail -n 1")
    write_cache=$(ssh ${server} "cat /sys/class/block/sd*/queue/write_cache|sort -u|tail -n 1")
    ssh ${server} "mkdir -p $(dirname ${recovery_file})"
    ssh ${server} "echo scheduler ${scheduler} >> ${recovery_file}"
    ssh ${server} "echo queue_depth ${queue_depth} >> ${recovery_file}"
    ssh ${server} "echo nr_requests ${nr_requests} >> ${recovery_file}"
    ssh ${server} "echo write_cache ${write_cache} >> ${recovery_file}"
  fi

  for disk in ${data_disk_list[*]}
  do
        echo ${server} "echo mq-deadline > /sys/class/block/${disk}/queue/scheduler"
        ssh ${server} "echo mq-deadline > /sys/class/block/${disk}/queue/scheduler"
        echo ${server} "cat /sys/class/block/${disk}/queue/scheduler"
        ssh ${server} "cat /sys/class/block/${disk}/queue/scheduler"

        echo ${server}  "echo 128 > /sys/class/block/${disk}/device/queue_depth"
        ssh ${server}  "echo 128 > /sys/class/block/${disk}/device/queue_depth"
        echo ${server}  "cat /sys/class/block/${disk}/device/queue_depth"
        ssh ${server}  "cat /sys/class/block/${disk}/device/queue_depth"


        echo ${server} "echo 256 > /sys/block/${disk}/queue/nr_requests"
        ssh ${server} "echo 256 > /sys/block/${disk}/queue/nr_requests"
        echo ${server} "cat /sys/block/${disk}/queue/nr_requests"
        ssh ${server} "cat /sys/block/${disk}/queue/nr_requests"

        ssh ${server} "yum install hdparm -y"
        ssh ${server} "hdparm -W /dev/${disk}"
        sleep 0.5
        ssh ${server} "hdparm -W 0 /dev/${disk}"


        echo ${server} "echo write through> /sys/class/block/${disk}/queue/write_cache"
        ssh ${server} "echo write through> /sys/class/block/${disk}/queue/write_cache"
        echo ${server} "cat /sys/class/block/${disk}/queue/write_cache"
        ssh ${server} "cat /sys/class/block/${disk}/queue/write_cache"
done
done
}

check()
{
for server in ${server_list[@]}
do
  echo ${server} check
  ssh ${server} "cat /sys/class/block/sd*/queue/scheduler"
  ssh ${server}  "cat /sys/class/block/sd*/device/queue_depth"
  ssh ${server} "cat /sys/block/sd*/queue/nr_requests"
  ssh ${server} "cat /sys/class/block/sd*/queue/write_cache"

done
}

recovery()
{
  echo server recovery
for server in ${server_list[@]}
do
  echo ${server} recovery
  scheduler=$(ssh ${server} "cat ${recovery_file}|grep scheduler|awk '{print \$2}'|tail -n 1")
  queue_depth=$(ssh ${server} "cat ${recovery_file}|grep queue_depth|awk '{print \$2}'|tail -n 1")
  nr_requests=$(ssh ${server} "cat ${recovery_file}|grep nr_requests|awk '{print \$2}'|tail -n 1")
  write_cache=$(ssh ${server} "cat ${recovery_file}|grep write_cache|tail -n 1"|awk '{printf "%s %s", $2, $3}')

  data_disk_list=($(ssh ${server} "lsblk|grep disk |grep -v nvme|grep -v \$(lsblk|grep /boot/efi|awk '{print \$1}'|grep -Eo '[a-zA-Z]+')|awk '{print \$1}'|grep sd"))

  for disk in ${data_disk_list[*]}
  do
    if [ "${scheduler}" != "" ];then
        ssh ${server} "echo ${scheduler} > /sys/class/block/${disk}/queue/scheduler"
    fi

    if [ "${queue_depth}" != "" ];then
        ssh ${server} "echo ${queue_depth} > /sys/class/block/${disk}/device/queue_depth"
    fi

    if [ "${nr_requests}" != "" ];then
        ssh ${server} "echo ${nr_requests} > /sys/block/${disk}/queue/nr_requests"
    fi
    if [ "${write_cache}" != "" ];then
        ssh ${server} "echo ${write_cache} >  /sys/class/block/${disk}/queue/write_cache"
    fi
  done

    ssh ${server}  "rm -f ${recovery_file}"
done

}

write_cache()
{
for server in ${server_list[@]}
do
  echo ${server} optimize
  data_disk_list=($(ssh ${server} "lsblk|grep disk |grep -v nvme|grep -v \$(lsblk|grep /boot/efi|awk '{print \$1}'|grep -Eo '[a-zA-Z]+')|awk '{print \$1}'|grep sd"))

  for disk in ${data_disk_list[*]}
  do
        echo ${server} "echo $1 > /sys/class/block/${disk}/queue/write_cache"
        ssh ${server} "echo $1 > /sys/class/block/${disk}/queue/write_cache"
  done
done
}

usage()
{
 echo "Usage: $0 all|check|recovery|write_through|write_back"
 exit 1
}


case $1 in
all)
  optimize
  ;;
check)
  check
  ;;
recovery)
  recovery
  ;;
write_through)
  write_cache "write through"
  ;;
write_back)
  write_cache "write back"
  ;;
*)
  usage
  ;;
esac