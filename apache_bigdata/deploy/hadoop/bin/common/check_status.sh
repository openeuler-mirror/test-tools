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
source /etc/profile
tool_root_dir=$(cd "$(dirname "$0")"/../..||exit 1;pwd)
source "${tool_root_dir}"/conf/config
PROCESS_NAME=DataNode
INSTALL_DIR=${hadoop_dir}/hadoop-${hadoop_version}

read -r -a node_list <<< "${datanode//,/ }"
file=/check_alive_hadoop_word_count.txt

#################################### functions #####################################

function check_alive() {
    # prepare source file
    touch ${file}
    echo 'hello hello' > ${file}

    hadoop fs -mkdir -p /root
    hadoop fs -put ${file} /root

    # get params
    cd "${INSTALL_DIR}" || exit 1
    jar_path=$(find -name hadoop-mapreduce-examples*.jar |grep -v source |head -1 |awk '{print substr($1,2)}')
    example_jar_path=${INSTALL_DIR}/${jar_path}
    id=wordcount

    # execute
    hadoop jar "${example_jar_path}" ${id} /root /root2

    if [ $? -eq 0 ]; then
        result_value=0
    else
        result_value=1
    fi

    # clear files
    hadoop fs -rm -r /root
    hadoop fs -rm -r /root2

    rm -f ${file}

    # return result
    if [ ${result_value} -eq 0 ]; then
        echo "hadoop is alive"
        exit 0
    else
        echo "hadoop is not alive"
        exit 1
    fi
}

function check_process() {
    command="ps -ef |grep -w ${PROCESS_NAME}|grep -v grep -c"
    for agent in "${node_list[@]}"
        do
            result=$(ssh "${agent}" "${command}")
            if [ "${result}" -lt 1 ];then
                echo "hadoop ${PROCESS_NAME} alive less then 1 on ${agent}"
                exit 1
            fi
        done
    echo "hadoop process check ok"

}

function check_install() {
    command="test -d ${INSTALL_DIR}"
    for agent in "${node_list[@]}"
        do
            if ssh "${agent}" "${command}"; then
                echo "${agent} ${INSTALL_DIR} exist"
            else
                echo "hadoop is not install on ${agent}"
                exit 1
            fi
        done
}

##################################### execute #########################################

if [[ $# -ne 1 ]]; then
    echo "Usage: bash ${0##*/} check_alive|check_install|check_process"
    exit 1
fi

case ${1} in
    check_alive)
        check_process
        check_alive
        ;;
    check_install)
        check_install
        ;;
    check_process)
        check_process
        ;;
    *)  echo "[Usage] bash ${0##*/} check_alive|check_install|check_process"
        exit 1
        ;;
esac
