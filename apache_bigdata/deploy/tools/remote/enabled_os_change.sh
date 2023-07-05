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
if [[ $# -ne 1 ]] || [[ ${1} != "always" ]]  && [[ ${1} != "madvise" ]] && [[ ${1} != "never" ]]; then
    echo -e "\E[1;31m[ERROR]\E[0m you need to set a parameter(always|madvise|never) to bash ${0##*/}"
    exit 1
fi

function enabled_backup()
{
    filePath="/root/enabled_backup.txt"
    enabled=$(cat < /sys/kernel/mm/transparent_hugepage/enabled | cut -d '[' -f2|cut -d ']' -f1)
    if [ "${1}" = "${enabled}" ];then
        echo -e "\E[1;36m[INFO]\E[0m enabled is already set to ${1}"
        exit 0
    else
        echo "${enabled}" > ${filePath}
    fi
}

function enabled_change()
{
    echo "${1}" > /sys/kernel/mm/transparent_hugepage/enabled
    enabled_new=$(cat < /sys/kernel/mm/transparent_hugepage/enabled | cut -d '[' -f2|cut -d ']' -f1)
    if [ "${1}" = "${enabled_new}" ];then
        echo -e "\E[1;36m[INFO]\E[0m enabled change to ${enabled_new} succeed"
    else
        echo -e "\E[1;31m[ERROR]\E[0m enabled change to ${1} falied"
        exit 1
    fi
}

enabled_backup "${1}"
enabled_change "${1}"
