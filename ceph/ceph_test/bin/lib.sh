create_images()
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
{
  # create pool
   ssh ${client_list[0]} "ceph osd pool create ${pool_name} ${pg_num} ${pg_pnum}"
  # create images
	for index in $(seq 1 ${image_num})
	do
		 ssh ${client_list[0]} "rbd create ${image_name}${index} --size ${image_size} --pool ${pool_name} --image-format 2 --image-feature layering"
		sleep 1
	done
	# check image num
	 num=$(ssh ${client_list[0]} "rbd ls -p ${pool_name}|grep ${image_name}|wc -l")
  if [ ${num} -lt ${image_num} ];then
    echo "create ${num}  image less than ${image_num}"
    exit 3
  fi
}

pg_balance()
{
  ssh ${client_list[0]} "mkdir -p /home/ceph"
  scp -r ${root_path}/pgbalance ${client_list[0]}:/home
  ssh ${client_list[0]} "chmod 755 /home/pgbalance/*"
  ssh ${client_list[0]} "cd /home/pgbalance; sh run.sh"
}
delete_pool()
{
  ssh ${client_list[0]} "ceph osd pool delete ${pool_name} ${pool_name} --yes-i-really-really-mean-it"
  [[ $? -ne 0 ]]  && echo "${client_list[0]} delete pool failed failed" && exit 2
}

install_fio()
{
cd ${root_path}/bin
for client in ${client_list[*]}
do
  fio_flag=$(ssh ${client} 'command -v fio &>/dev/null;echo $?')
  if [ "${fio_flag}" != "0" ];then
    scp fio-3.19.tar.gz ${client}:/home
    ceph_version=$(ssh ${client} "ceph -v|awk '{print \$3}'")
    ssh ${client} "yum install -y librbd-devel-${ceph_version} tar"
    ssh ${client} '
cd /home
tar -xzf  fio-3.19.tar.gz
cd fio-3.19
./configure
make
make install
'
  sleep 1
  check_flag=$(ssh ${client} 'command -v fio &>/dev/null;echo $?')
  if [ "${check_flag}" != "0" ];then
    echo "${client} install fio failed"
    exit 4
  fi
  fi
done
}

clean_cache()
{
# clean cache
for server in ${server_list[@]}
do
 ssh ${server} "echo 3 > /proc/sys/vm/drop_caches"
done

for client in ${client_list[@]}
do
 ssh ${client} "echo 3 > /proc/sys/vm/drop_caches"
done
}

start_fio_server()
{
# start fio server
for client in ${client_list[@]}
do
 ssh ${client} "killall -9 fio"
 sleep 2
 ssh -f ${client} "mkdir -p /home/fio_server;fio -S 2>&1 >> /home/fio_server/fio_server.log"
done
}

kill_fio_server()
{
for client in ${client_list[@]}
do
 ssh ${client} "killall -9 fio"
done
}

get_bandwith_mb_value()
{
  unit=$(echo $1|grep -Eo '[a-zA-Z]+')
  bandwidth_value=$(echo $1|grep -Eo '[0-9]+([.][0-9]+)?')
  if [[ "${unit}" = "K" || "${unit}" = "k" ]];then
    echo ${bandwidth_value}|awk '{printf "%.2f", $1 / 1000}'
  elif [[ "${unit}" = "M" ]];then
    echo ${bandwidth_value}
  elif [[ "${unit}" = "G" ]];then
    echo ${bandwidth_value}|awk '{printf "%.2f", $1 * 1000}'
  elif [[ "${unit}" = "T" ]];then
    echo ${bandwidth_value}|awk '{printf "%.2f", $1 * 1000 * 1000}'
  else
    echo "bandwith unit ${unit} not support !"
    exit 1
  fi

}

get_iops_value()
{
  unit=$(echo $1|grep -Eo '[a-zA-Z]+')
  iops_value=$(echo $1|grep -Eo '[0-9]+([.][0-9]+)?')
  if [[ "${unit}" = "K" || "${unit}" = "k" ]];then
    echo ${iops_value}|awk '{printf $1 * 1000}'
  elif [[ "${unit}" = "" ]];then
    echo ${iops_value}
  else
    echo "iops unit ${unit} not support !"
    exit 1
  fi
}


deal_fio_result()
{
report_file=${root_path}/report/fio.report
if [ ! -e ${report_file} ];then
  mkdir -p $(dirname ${report_file})
  touch ${report_file}
  printf "%-15s%-10s    %-10s  %-10s    %-10s    %-15s%-15s   %-15s  %-15s\n" "time" "block_size" "operate" "read_ratio" "is_bcache" "iops" "bandwidth/M" "bandwidth_total/M" "iops_total" >> ${report_file}
fi
read_iops=$(cat ${output_log}|grep -A 14 'All clients:'|grep "read: IOPS"|tail -n 1|awk -F '[=,]+' '{print $2}')
read_bandwidth=$(cat ${output_log}|grep -A 14 'All clients:'|grep "read: IOPS"|tail -n 1|awk -F "[()]" '{print $2}')
write_iops=$(cat ${output_log}|grep -A 14 'All clients:'|grep "write: IOPS"|tail -n 1|awk -F '[=,]+' '{print $2}')
write_bandwidth=$(cat ${output_log}|grep -A 14 'All clients:'|grep "write: IOPS"|tail -n 1|awk -F "[()]" '{print $2}')
if [[ "${operate}" = "rw" || "${operate}" = "randrw" ]];then
  read_bandwidth=$(get_bandwith_mb_value ${read_bandwidth})
  write_bandwidth=$(get_bandwith_mb_value ${write_bandwidth})
  read_iops=$(get_iops_value ${read_iops})
  write_iops=$(get_iops_value ${write_iops})
  report_read_ratio=${read_ratio}
  iops="${read_iops}/${write_iops}"
  bandwidth="${read_bandwidth}/${write_bandwidth}"
  bandwidth_total="$(echo ${read_bandwidth} ${write_bandwidth}|awk '{printf "%.2f",  $1 + $2}')"
  iops_total="$(echo ${read_iops} ${write_iops}|awk '{print $1 + $2}')"
elif [[ "${operate}" = "read" || "${operate}" = "randread" ]];then
  read_bandwidth=$(get_bandwith_mb_value ${read_bandwidth})
  report_read_ratio="100"
  iops="$(get_iops_value ${read_iops})"
  bandwidth="${read_bandwidth}"
  bandwidth_total="${read_bandwidth}"
  iops_total="${iops}"
else
  write_bandwidth=$(get_bandwith_mb_value ${write_bandwidth})
  report_read_ratio="0"
  iops="$(get_iops_value ${write_iops})"
  bandwidth="${write_bandwidth}"
  bandwidth_total="${write_bandwidth}"
  iops_total="${iops}"
fi
if [[ "${is_bcache}" != "true" ]];then
   is_bcache=false
fi

printf  "%-15s%-10s    %-10s  %-10s    %-10s    %-15s%-15s   %-15s    %-15s\n"  $(date +%m%d%H%M%S) ${block_size} ${operate}  ${report_read_ratio} ${is_bcache} ${iops} ${bandwidth} ${bandwidth_total} ${iops_total} >> ${report_file}

}


restart_ceph_osd()
{
for server in ${server_list[*]}
do
  ssh ${server} "systemctl restart ceph-osd.target"
done
sleep 30
for i in $(seq 1 3)
do
  osd_up_num=$(ceph -s|grep osd:|awk '{print $4}')
  osd_total_num=$(ceph -s|grep osd:|awk '{print $2}')
  if [ ${osd_up_num} -ne ${osd_total_num} ];then
    restart_ceph_target
  else
    break
  fi
  sleep 30
  if [ ${i} -eq 3 ];then
    echo ceph osd restart failed
    exit 1
  fi
done
}

restart_ceph_target()
{
for server in ${server_list[*]}
do
  ssh ${server} "systemctl daemon-reload"
  ssh ${server} "systemctl restart ceph.target"
done
sleep 6
}

check_bcache()
{
for server in ${server_list[@]}
do
while true
do
flag=$(ssh ${server} "cat /sys/block/bcache*/bcache/state|grep -v clean|grep -v 'no cache'")
if [[ "${flag}" == "" ]]
then
echo ${server} disk is ok

break
else
echo sleep 1
sleep 1

fi

done
done
}

bcache_start()
{
for server in ${server_list[@]}
do
echo ${server}
bcache_list=$(ssh ${server} "ls /sys/block|grep bcache")
for bcache in ${bcache_list[@]}
do
ssh ${server} "echo writeback >/sys/block/${bcache}/bcache/cache_mode"
ssh ${server} "echo 0 >/sys/block/${bcache}/bcache/sequential_cutoff"
ssh ${server} "echo 40 >/sys/block/${bcache}/bcache/writeback_percent"

ssh ${server} "echo 1000 > /sys/block/${bcache}/bcache/writeback_delay"
ssh ${server} "echo 0 > /sys/block/${bcache}/bcache/cache/congested_read_threshold_us"
ssh ${server} "echo 0 > /sys/block/${bcache}/bcache/cache/congested_write_threshold_us"

done
sleep 1
done

}

clean_bcache_data()
{
for server in ${server_list[@]}
do
  scp ${root_path}/bin/clean_bcache_data.sh ${server}:/home
  ssh -f ${server} "sh /home/clean_bcache_data.sh"
done
}


clean_bcache()
{
for server in ${server_list[@]}
do
echo ${server}
bcache_list=$(ssh ${server} "ls /sys/block|grep bcache")
for bcache in ${bcache_list}
do
ssh ${server} "echo 0 > /sys/block/${bcache}/bcache/writeback_delay"
ssh ${server} "echo 0 > /sys/block/${bcache}/bcache/writeback_percent"
sleep 1
ssh ${server} "echo 1 > /sys/block/${bcache}/bcache/cache/internal/trigger_gc"

done
done

sleep 30
# clean bcache data
if [[ "${bcache_detach}" = "true" ]];then
  clean_bcache_data
  sleep 30
fi
# check bcache disk
check_bcache

# bcache start
bcache_start
sleep 5
}


bcache_watch()
{
name=$1
for server in ${server_list[@]}
do
  scp ${root_path}/bin/bcache_watch.sh ${server}:/home
  ssh  ${server} "sh /home/bcache_watch.sh" > ${server}_${name}_watch.log
done
}

NMON_PATH="/home/ceph/nmon"

nmon_start(){
for server in ${server_list[@]}
do

  nmon_flag=$(ssh ${server} 'command -v nmon &>/dev/null;echo $?')
  if [ "${nmon_flag}" != "0" ];then
    ssh ${server} "yum install -y nmon"
  fi
  ssh ${server} "rm -rf ${NMON_PATH};mkdir -p ${NMON_PATH}"
  ssh ${server} "nmon -s 1 -ft -m ${NMON_PATH}"

done
}

nmon_stop(){
for server in ${server_list[@]}
do
  ssh ${server} "ps -ef|grep 'nmon -s'|grep -v 'grep'|awk '{print \$2}'|xargs kill -9"
  scp ${server}:${NMON_PATH}/*nmon .
done
}