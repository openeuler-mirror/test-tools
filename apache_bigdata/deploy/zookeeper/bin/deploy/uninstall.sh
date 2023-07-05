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
tool_root_dir=$(cd "$(dirname "$0")"/../..||exit 1;pwd)
source "${tool_root_dir}"/conf/config
source "${tool_root_dir}"/bin/common/remote.sh

echo "you will uninstall zookeeper,please input 'yes' to confirm"
read -r yes

if [ "${yes}" = yes ];then
    # 先停止集群                              
    bash "${tool_root_dir}"/bin/switch/stop.sh
    echo "Zookeeper will be uninstalled"

    export IFS=","
    # 删除所有节点上的zookeeper包
    for ip in ${zookeeper_list}
    do
        delete_remote "${zookeeper_dir}"/zookeeper "${ip}" "root"        
        delete_remote "${zookeeper_dir}"/"${package%.tar*}" "${ip}" "root"
    done

    echo "Zookeeper has successfully removed from your computer!"
else
    echo "Cancel"
fi
