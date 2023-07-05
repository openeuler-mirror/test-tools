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
HOSTNAME=$1
IP_HOSTNAME_FILE=$2

echo -e "\033[42;30m ====================Deploy hostname [${HOSTNAME}]==================== \033[0m"
hostnamectl set-hostname "${HOSTNAME}"

newhostname=$(hostname)
if [ "${HOSTNAME}" != "${newhostname}" ];then
    echo "Failed to deploy hostnamectl"
    exit 1
fi

while read -r line
do
    if ! cat < "/etc/hosts" | grep "^${line}" > /dev/null 2>&1;then
        echo "Add ${line} to /etc/hosts [${HOSTNAME}]"
        echo "${line}" >> /etc/hosts
    fi
done < "${IP_HOSTNAME_FILE}"

echo "Finish deploy hostname"
