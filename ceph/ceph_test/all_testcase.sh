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
root_path=$(cd $(dirname $0)||exit 1;pwd)
source ${root_path}/conf/cluster_info.cfg
source ${root_path}/bin/lib.sh

per_testcase_count=5


usage()
{
 echo "Usage: $0 run nomal|bcache"
 exit 1
}



run_all_test()
{
cd ${root_path}/bin
# env pre
sh env_pre.sh pre

# pre data
sh pre_data.sh run

# check ceph
sleep_count=0
while true
do
  if [[ ${sleep_count} -gt 480 ]];then
    echo check ceph failed
    exit 1
  fi
  ceph -s|grep misplaced
	if [ $? -eq 0 ]; then
	  sleep_count=$((sleep_count + 1))
	  echo sleep 10
		sleep 10
	else
		break
	fi
done


# 1M rw
sed -i "s#block_size=.*#block_size=1024K#" "${root_path}/conf/testcase.cfg"
sed -i "s#operate=.*#operate=rw#" "${root_path}/conf/testcase.cfg"
sed -i "s#read_ratio=.*#read_ratio=70#" "${root_path}/conf/testcase.cfg"
sed -i "s#is_bcache=.*#is_bcache=${is_bcache}#" "${root_path}/conf/testcase.cfg"

for count in $(seq 1 ${per_testcase_count})
do
  sh fio_test.sh run
  sleep 6
done

# 4K randwrite
sed -i "s#block_size=.*#block_size=4K#" "${root_path}/conf/testcase.cfg"
sed -i "s#operate=.*#operate=randwrite#" "${root_path}/conf/testcase.cfg"
sed -i "s#is_bcache=.*#is_bcache=${is_bcache}#" "${root_path}/conf/testcase.cfg"

for count in $(seq 1 ${per_testcase_count})
do
  sh fio_test.sh run
  sleep 6
done

# 4K randrw
sed -i "s#block_size=.*#block_size=4K#" "${root_path}/conf/testcase.cfg"
sed -i "s#operate=.*#operate=randrw#" "${root_path}/conf/testcase.cfg"
sed -i "s#read_ratio=.*#read_ratio=70#" "${root_path}/conf/testcase.cfg"
sed -i "s#is_bcache=.*#is_bcache=${is_bcache}#" "${root_path}/conf/testcase.cfg"


for count in $(seq 1 ${per_testcase_count})
do
  # nomal 4k randrw need restart ceph osd
  if [[ "${is_bcache}" = "false" ]];then
    restart_ceph_osd
    sleep 10
  fi
  sh fio_test.sh run
  sleep 6
done

}


case $2 in
bcache)
  is_bcache=true
  ;;
nomal)
  is_bcache=false
  ;;
*)
usage
  ;;
esac


case $1 in
run)
  run_all_test
  ;;
*)
  usage
  ;;
esac
