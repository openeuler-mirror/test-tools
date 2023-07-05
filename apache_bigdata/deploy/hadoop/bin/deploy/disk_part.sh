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
part_num=$1
dir_name=$2
file_format=$3
echo ${part_num}|grep -E '[0-9]+' &>/dev/null
if [ $? -ne 0 ];then
  echo "Usage: $0 11 /data/data ext4"
  exit
fi
if [ "${file_format}" = "" ];then
  file_format=ext4
fi
if [ "${dir_name}" = "" ];then
  dir_name=/data/data
fi

lsblk|grep ${dir_name}|awk '{print $NF}'|xargs umount

disk_num=1

disk_list=($(lsblk|grep disk |grep -v nvme|grep -v $(lsblk|grep /boot/efi|awk '{print $1}'|grep -Eo '[a-zA-Z]+')|grep sd|awk '{print $1}'))
for disk in ${disk_list[*]:0:${part_num}}
do
echo ${disk}
parted -s /dev/${disk} mklabel gpt
parted -s /dev/${disk} mkpart logical 0% 100%

if [ "${file_format}" = "ext4" ];then
   mkfs.ext4 -F /dev/${disk}1
elif [ "${file_format}" = "xfs" ];then
   mkfs.xfs -f /dev/${disk}1
else
   echo ${file_format} not support!
   exit 1
fi

mkdir  -p ${dir_name}${disk_num}
mount /dev/${disk}1 ${dir_name}${disk_num}
uuid=$(blkid|grep /dev/${disk}1|awk -F "\"" '{print $2}')
data_path=$(lsblk|grep ${disk}1|awk '{print $NF}')

for del_num in $(cat -n /etc/fstab |grep ${data_path}|awk '{print $1}'|sort -r)
do
  sed -i "${del_num}d" /etc/fstab
done

part_str="UUID="${uuid}"    ${data_path}    ${file_format}    defaults,nofail 0    0"

echo ${part_str} >> /etc/fstab

disk_num=$(( disk_num + 1 ))

done

# check part num
if [ "$(lsblk|grep ${dir_name}|wc -l)" != "${part_num}" ];then
  echo part disk failed!
  exit 1
fi
