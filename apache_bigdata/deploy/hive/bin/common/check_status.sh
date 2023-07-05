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
PROCESS_NAME=RunJar
INSTALL_DIR=${hive_dir}/${package%.tar*}

user=root
host=localhost
port=10000
file=/check_alive_hive.sql

################################# functions ##################################

function check_alive() {

# create sql file
echo 'create database check_alive_hive_test;' > ${file}
echo 'use check_alive_hive_test;' >> "${file}"
echo 'create table test(id int,name string);' >> ${file}
echo 'insert into table test values(1, "1");' >> ${file}

# execute
if beeline -n ${user} -u jdbc:hive2://${host}:${port} -f ${file}; then
	result_value=0
else
	result_value=1
fi

# clear database and sql file
echo 'DROP DATABASE IF EXISTS check_alive_hive_test CASCADE;' > ${file}
beeline -n ${user} -u jdbc:hive2://${host}:${port} -f ${file}
rm -f ${file}

# return result
if [ ${result_value} -eq 0 ]; then
    echo "hive is alive"
	exit 0
else
    echo "hive is not alive"
	exit 1
fi

}

function check_process() {
    command=$(ps -ef |grep -w ${PROCESS_NAME}|grep -v grep -c)
	if [ "${command}" -le 1 ]; then
	    echo "hive ${PROCESS_NAME} alive less then 1"
		exit 1
	fi
	echo "${command} ${PROCESS_NAME} alive on server"
}

function check_install() {
    if [ -d "${INSTALL_DIR}" ]; then
	    echo "hive install check ok"
        exit 0
    else
	    echo "hive is not install"
        exit 1
    fi
}

################################# execute #######################################

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
