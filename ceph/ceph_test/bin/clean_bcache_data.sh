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

caches=$(ls /sys/block/ | grep bcache)
bcaches=()
uids=()
devs=()
for i in $caches
do
	uid=`ls -al /sys/class/block/$i/bcache/cache  | awk -F '/' '{print $NF}'`
	dev=`ls -al /sys/fs/bcache/$uid/cache0 | awk -F '/' '{print $(NF-1)}'`
	echo $i $uid $dev
	uids=(${uids[@]} ${uid})
	devs=(${devs[@]} ${dev})
	bcaches=(${bcaches[@]} ${i})
done 

let n=${#bcaches[@]}-1

for ((i=0;i<=$n; i ++))
do
	echo "detache ${devs[$i]} from cache"
	echo "echo ${uids[$i]} > /sys/block/${bcaches[$i]}/bcache/detach"
	echo ${uids[$i]} > /sys/block/${bcaches[$i]}/bcache/detach
	sleep 1s
done

date
#controller by manual
##touch bcache.lock
while true
do
	if [ -f bcache.lock ]; then
		sleep 1s
	else
		break
	fi
done

while true
do
	str=`cat /sys/block/bcache*/bcache/state | grep -v "no cache" |grep -v "clean"`
	if [ "$str" == "" ];then
		echo "detach ok"
		break
	else
		sleep 1s
	fi
done
date

for ((i=0;i<=$n; i ++))
do
	echo "attache ${devs[$i]} to cache"
	echo "echo ${uids[$i]} > /sys/block/${bcaches[$i]}/bcache/attach"
	echo ${uids[$i]} > /sys/block/${bcaches[$i]}/bcache/attach
	sleep 1s
done


