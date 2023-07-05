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

add_env_var() {
    ip=$1
    user=$2
    add_env_var_script=$3

    echo -e "\033[42;30m ====================Check & add environment variables to /etc/profile [${ip}]==================== \033[0m"

    send_remote "${add_env_var_script}" /tmp/"${add_env_var_script##*/}" "${ip}" "${user}"

    run_remote "bash /tmp/${add_env_var_script##*/}" "${ip}" "${user}"

    delete_remote /tmp/"${add_env_var_script##*/}" "${ip}" "${user}"

}

tmp_dir=/tmp
add_env_var_script=${tool_root_dir}/bin/deploy/check_add_env_var.sh

# 下载安装包
if [ "${is_online}" == "true" ]; then
    if ! bash "${tool_root_dir}"/bin/download/download.sh; then
        echo "Download deps fail!"
        exit 1
    fi
fi

idx=1
read -r -a zk_arr <<< "${zookeeper_list//,/ }"
for ip in "${zk_arr[@]}"
do
    # 传输安装包
    send_remote "${tool_root_dir}"/deps/"${platform}"/"${zookeeper_version}"/"${package}" ${tmp_dir}/"${package}" "${ip}" "root"
    
    # 解压压缩包
    run_remote "tar -zxf ${tmp_dir}/${package} -C ${zookeeper_dir}" "${ip}" "root"

    # 建立软链接
    run_remote "ln -s ${zookeeper_dir}/${package%.tar*} ${zookeeper_dir}/zookeeper" "${ip}" "root"

    # 添加环境变量
    add_env_var "${ip}" "root" "${add_env_var_script}"

    # 修改配置文件 zoo.cfg
    run_remote "cp ${zookeeper_dir}/${package%.tar*}/conf/zoo_sample.cfg ${zookeeper_dir}/${package%.tar*}/conf/zoo.cfg" "${ip}" "root" 
    data_dir=$(echo "${zookeeper_dir}zookeeper/tmp" | sed "s/\//\\\\\//g")
    run_remote "mkdir -p ${zookeeper_dir}zookeeper/tmp; sed -i 's/^dataDir=.*/dataDir=${data_dir}/g' ${zookeeper_dir}/${package%.tar*}/conf/zoo.cfg" "${ip}" "root"

    # 在zoo.cfg添加zookeeper进程的信息
    i=1
    for host in "${zk_arr[@]}"
    do
        run_remote "echo \"server.${i}=${host}:2888:3888\" >> ${zookeeper_dir}zookeeper/conf/zoo.cfg" "${ip}" "root"
        ((i++))
    done

    # 修改myid，从1开始
    run_remote "touch ${zookeeper_dir}/${package%.tar*}/tmp/myid; echo ${idx} >${zookeeper_dir}/${package%.tar*}/tmp/myid" "${ip}" "root" 
    ((idx++))
done

# 启动zookeeper集群
bash "${tool_root_dir}"/bin/switch/start.sh