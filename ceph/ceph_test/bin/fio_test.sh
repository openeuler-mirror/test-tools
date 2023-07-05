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
source ${root_path}/conf/testcase.cfg
source ${root_path}/conf/fio.cfg
source ${root_path}/bin/lib.sh


test_exec()
{
test_cmd="fio "

log_path=${root_path}/logs/${block_size}-${operate}-$(date +%Y%m%d%H%M%S)
mkdir -p ${log_path}
cd ${log_path}
echo ${log_path}

count=0
client_num=${#client_list[@]}

if [[ "${is_bcache}" = "true" ]];then
  clean_bcache
  bcache_watch start
fi

# clean cache
clean_cache
sleep 2
# nmon start
if [[ "${nmon_switch}" = "true" ]];then
  nmon_start
fi


# start fio server
start_fio_server

sleep 2


for i in $(seq 1 ${image_num})
do
  cat >> ${block_size}_image${i}_${operate}.fio  <<EOF
[global]
ioengine=rbd
clientname=admin
pool=${pool_name}
size=${image_size}
direct=1
numjobs=${numjobs}
ramp_time=${ramp_time}
runtime=${runtime}
time_based
log_avg_msec=500
thread
rbdname=${image_name}${i}
EOF

if [[ "${operate}" == "rw" || "" == "randrw" ]]
then

cat >> ${block_size}_image${i}_${operate}.fio  <<EOF
rwmixread=${read_ratio}
EOF

fi

cat >> ${block_size}_image${i}_${operate}.fio  <<EOF

[${block_size}-${operate}]
bs=${block_size}
rw=${operate}
iodepth=${iodeph}
stonewall
buffer_compress_percentage=40
EOF

test_cmd="${test_cmd} --client=${client_list[${count}]} ${block_size}_image${i}_${operate}.fio"

count=$((${count} + 1))
if [[ ${count} -eq ${client_num} ]]
then
    count=0
fi
done

echo $test_cmd
if [[ "${operate}" = "rw" || "${operate}" = "randrw" ]]
then
  output_log=${block_size}_${operate}_read${read_ratio}.log
else
  output_log=${block_size}_${operate}.log
fi

time_out=$[${runtime} + ${ramp_time} + 60]
timeout ${time_out} ${test_cmd} --group_reporting 2>&1 |tee ${output_log}

kill_fio_server

# nmon stop
if [[ "${nmon_switch}" = "true" ]];then
  nmon_stop
fi


if [[ "${is_bcache}" = "true" ]];then
  bcache_watch end
fi

deal_fio_result
cd -

}


usage()
{
 echo "Usage: $0 run"
 exit 1
}


case $1 in
run)
  test_exec
  ;;
*)
  usage
  ;;
esac
