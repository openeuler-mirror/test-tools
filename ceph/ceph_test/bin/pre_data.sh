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
source ${root_path}/conf/fio.cfg
source ${root_path}/bin/lib.sh


pre_data()
{
rw=write
block_size=1024K

size=100%

test_cmd="fio "
log_path=${root_path}/logs/${block_size}-${rw}-$(date +%Y%m%d%H%M%S)
mkdir -p ${log_path}
cd ${log_path}
echo ${log_path}

count=0
client_num=${#client_list[@]}

# clean cache
clean_cache
sleep 2
# start fio server
start_fio_server

sleep 2

for i in $(seq 1 ${image_num})
do 
  cat >> ${block_size}_image${i}_${rw}.fio  <<EOF
[global]  
ioengine=rbd  
clientname=admin  
pool=${pool_name} 
size=${size} 
direct=1  
numjobs=1  
ramp_time=${ramp_time}
log_avg_msec=500  
thread  
rbdname=${image_name}${i}  
[${block_size}-${rw}]  
bs=${block_size}  
rw=${rw}  
iodepth=${iodeph}
stonewall
buffer_compress_percentage=40
EOF

test_cmd="${test_cmd} --client=${client_list[${count}]} ${block_size}_image${i}_${rw}.fio"

count=$((${count} + 1))
if [[ ${count} -eq ${client_num} ]]
then
    count=0
fi
done

echo $test_cmd
${test_cmd} --group_reporting 2>&1 |tee ${block_size}-${rw}.log

kill_fio_server
cd -
}


usage()
{
 echo "Usage: $0 run"
 exit 1
}


case $1 in
run)
  pre_data
  sleep 60
  # pg balance
  pg_balance
  ;;
*)
  usage
  ;;
esac
