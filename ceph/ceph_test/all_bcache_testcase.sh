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
# bcache need optimize
  if [[ "${is_bcache}" = "true" ]];then
    sh optimize.sh all
  fi
# env pre
sh env_pre.sh pre

# pre data
sh pre_data.sh run

sleep 180

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

sh optimize.sh write_back
# 4K randrw  write_cache write back
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
