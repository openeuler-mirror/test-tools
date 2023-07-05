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

tool_root_dir=$(cd "$(dirname "$0")/../../"||exit 1;pwd)

source "${tool_root_dir}/conf/config"
source "${tool_root_dir}/bin/common/remote.sh"


function uninstall()
{
    echo "Start uninstall"
    #read -r -a node_arr <<< "${spark_client//,/ }"
    
    # stop history server
    bash "${tool_root_dir}/bin/switch/stop.sh"

    # delete install file
    rm -rf "${spark_dir}/${package%.tgz*}"
    rm -rf "${spark_dir}/spark"
    rm -rf "${scala_dir}/${scala_package%.tar*}"
    rm -rf "${scala_dir}/scala"
    node_arr="${hive_node},${spark_client}"
    export IFS=","
    for node in ${node_arr[*]}
    do
        delete_remote "${spark_dir}/${package%.tar.gz*}" "${node}" "root"
        delete_remote "${spark_dir}/spark" "${node}" "root"
        delete_remote "${scala_dir}/${scala_package%.tar*}" "${node}" "root"
        delete_remote "${scala_dir}/scala" "${node}" "root"
    done
}


read -r -p "Are You Sure To Uninstall? [Y/n] " input
case ${input} in
    [yY][eE][sS]|[yY])
		uninstall
		;;

    [nN][oO]|[nN])
		echo "quit uninstall"
                exit 1
       	        ;;

    *)
		echo "Invalid input..."
		exit 1
		;;
esac
