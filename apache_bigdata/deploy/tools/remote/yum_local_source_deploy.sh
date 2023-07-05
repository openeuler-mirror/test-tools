#!/usr/bin/bash
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
YUM_ISO_PATH=$1
MOUNT_PATH=$2

echo -e "\033[42;30m ====================Deploy local yum source==================== \033[0m"
if [ ! -e /etc/yum.repos.d/backup/ ];then
    mkdir /etc/yum.repos.d/backup
    mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/backup/
fi

#mount_flag=`df -h | grep \${MOUNT_PATH} > /dev/null 2>&1; echo $?`
#if [ $((mount_flag)) == 0 ]; then
#    echo "Local yum source has mounted"
#    exit 1
#fi

df -h | grep \\"${MOUNT_PATH}" > /dev/null 2>&1
if [ $? == 0 ]; then
    echo "Local yum source has mounted"
    exit 1
fi

echo -e "\033[42;30m ====================Mount ${YUM_ISO_PATH} to ${MOUNT_PATH}==================== \033[0m"
cat >/etc/yum.repos.d/local.repo <<EOF
[local]
name=local
baseurl=file:///media/
enabled=1
gpgcheck=0
EOF

#umount ${MOUNT_PATH} &>/dev/null
if ! mount "${YUM_ISO_PATH}" "${MOUNT_PATH}" -o loop && yum clean all && yum makecache;then
    echo "Failed to mount $YUM_ISO_PATH ${MOUNT_PATH} -o loop && yum clean all && yum makecache"
    exit 1
fi
echo "Deploy local yum source success"
#yum -y install unzip expect dos2unix
