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
source "${tool_root_dir}/conf/config"
PROCESS_NAME=SparkSubmit
INSTALL_DIR=${spark_dir}/${package%.tar*}
# read -r -a node_list <<< "${spark_client//,/ }"
file=/check_alive_spark.sql

################################## functions ############################################

function check_alive() {

	# generate sql file
	touch ${file}
	echo 'create database check_alive_spark_database;' > ${file}
	echo 'use check_alive_spark_database;' >> "${file}"
	echo 'create table check_alive_spark_table(id int, name string);' >> ${file}
	echo 'insert into table check_alive_spark_table values(1, "nick");' >> ${file}

	# execute
	cd "${spark_dir}"/spark/bin||exit 1
	./beeline -n root -u jdbc:hive2://localhost:10016 -f ${file}

	if [ $? -eq 0 ]; then
		result_value=0
	else
		result_value=1
	fi

	# clear script file and database
	echo 'DROP DATABASE check_alive_spark_database CASCADE;' > ${file}
	./beeline -n root -u jdbc:hive2://localhost:10016 -f ${file}

	rm -f ${file}

	# return report
	if [ ${result_value} -eq 0 ]; then
	    echo "spark is alive"
		exit 0
	else
	    echo "spark is not alive"
		exit 1
	fi
}

function check_process() {
    command=$(ps -ef |grep -w ${PROCESS_NAME}|grep -v grep -c)
	if [ "${command}" -lt 1 ]; then
	    echo "spark ${PROCESS_NAME} alive less then 1"
		exit 1
	fi
	echo "${command} ${PROCESS_NAME} alive on server"
}

function check_install() {
    if [ -d "${INSTALL_DIR}" ]; then
        echo "spark install check ok"
        exit 0
    else
	    echo "spark is not install"
        exit 1
    fi
}

################################## execute ##############################################

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
