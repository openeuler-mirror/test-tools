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
PROCESS_NAME=Bootstrap
INSTALL_DIR=${tez_dir}/${package%.tar*}

function check_alive() {
    command=$(ps -ef |grep -w $PROCESS_NAME|grep -v grep|wc -l)
    if [ "${command}" -le 0 ]; then
       echo "tez is not alive"
        exit 1
    else
        echo "tez is alive"
        exit 0
    fi
}

function check_install() {
        if [ -d "${INSTALL_DIR}" ]; then
            exit 0
        else
            exit 1
        fi
}

function check_process() {
        command=$(ps -ef |grep -w $PROCESS_NAME|grep -v grep|wc -l)
        if [ "${command}" -le 0 ]; then
                exit 1
        fi
}

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