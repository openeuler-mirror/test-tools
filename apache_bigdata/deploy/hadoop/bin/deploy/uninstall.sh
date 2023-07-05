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

echo "you will uninstall hadoop,please input 'yes' to confirm"
read -r yes

if [ "${yes}" = yes ];then
    # 先停止集群
    bash "${tool_root_dir}"/bin/switch/stop.sh
    echo "hadoop will be uninstalled"

    if [ "${platform}" == "HDP" ] || [ ${platform} == "APACHE"  ]; then
        package_name=${package%.tar*}
    elif [ "${platform}" == "CDH" ]; then
        package_name=${package%-bin*}
    else
        echo "Unsupported platform!"
        exit 1;
    fi

    node_list="${namenode},${datanode}"
    namenode_dir=$(echo ${namenode_dir} | sed "s/,/\/*\ /g")/*
 
#read -r -a namenode_dir_arr <<< "${namenode_dir//,/ }"
#namenode_dir="${namenode_dir_arr[0]}"

    datanode_dir=`echo ${datanode_dir} | sed "s/,/\/*\ /g"`/*

    export IFS=","
    for node_host in ${node_list}
    do
        delete_remote "${hadoop_dir}/hadoop" "${node_host}" "root"
        delete_remote "${hadoop_dir}/${package_name}" "${node_host}" "root"
        delete_remote "${hadoop_dir}/${package_name}.tar.gz" "${node_host}" "root"
        delete_remote "${hadoop_tmp_dir}" "${node_host}" "root"
        delete_remote "${namenode_dir}" "${node_host}" "root"
        delete_remote "${datanode_dir}" "${node_host}" "root"
    done
    echo "Hadoop has successfully removed from your computer!"
else
    echo "cancel"
fi
