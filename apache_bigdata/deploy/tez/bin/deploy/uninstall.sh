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
tool_root_dir=$(cd "$(dirname "$0")"/../.. || exit 1;pwd)
source "${tool_root_dir}"/conf/config
source "${tool_root_dir}"/bin/common/remote.sh

echo "you will uninstall tez,please input 'yes' to confirm"
read -r yes

if [ "${yes}" = yes ];then
    # 先停止集群                              
    bash "${tool_root_dir}"/bin/switch/stop.sh
    echo "Tez will be uninstalled"

    # 删除tez相关的目录
    rm -rf "${tez_dir}"/tez 
    rm -rf "${tez_dir}"/"${package%.tar*}"
    rm -rf "${tomcat_dir}"/"${tomcat_package%.tar*}"
    rm -rf "${tomcat_dir}"/tomcat
    hadoop fs -rm -r /user/tez/"${package}"

    # 删除yarn-site.xml中关于tez的参数
    cat "${tool_root_dir}"/conf/tez-conf/"${platform}"/"${tez_version}"/tez-ui-yarn-site.xml | while read -r line
    do
        para=$(echo "${line}" | awk -F '=' '{print $1}')
        para_idx=$(grep -n "${para}" "${hadoop_home}"/etc/hadoop/yarn-site.xml | awk -F ":" '{print $1}')
        if [ "${para_idx}" != "" ]; then
            ((start_idx=${para_idx}-1))
            ((end_idx=${para_idx}+2))
            sed -i "${start_idx},${end_idx}d" "${hadoop_home}"/etc/hadoop/yarn-site.xml
        fi
    done

    # 重启hadoop集群使得配置生效
    bash "${tool_root_dir}"/bin/common/restart_hadoop.sh
fi
