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
root_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
source "${root_dir}"/conf/config

function change_os() {
    read -r -a all_os <<< "$(cat < "${root_dir}"/conf/os_config | grep -v ^\# | xargs)"
    read -r -a ip_list <<< "${os_ip_list//,/ }"
    self_ip=$(ip a | grep -w 'inet' | grep -v 127 | sed 's/^[ \t]*//g' | cut -d ' ' -f2 | head -1)
    self_ip=${self_ip%%/*}
    for ip in "${ip_list[@]}"
        do
            for one_change in "${all_os[@]}"
	        do
                    shell_name=${one_change%%=*}
	            shell_parameter=${one_change#*=}
		    read -r -a parameter <<< "${shell_parameter//,/ }"
	            ssh "${ip}" "scp ${self_ip}:${root_dir}/remote/${shell_name} /root;bash /root/${shell_name} ${parameter[*]}" 
	        done
	   done
}

if [ "${is_need_os}" = "true" ] || [ "${is_need_os}" = "TRUE" ];then 
    change_os
else
    echo "not need change os"
    exit 0
fi

