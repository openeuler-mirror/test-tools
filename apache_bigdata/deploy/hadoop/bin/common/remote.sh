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

run_remote() {
    cmd_str=$1
    remote_ip=$2
    remote_user=$3

    ssh -n -o "StrictHostKeyChecking=no" "${remote_user}"@"${remote_ip}" "${cmd_str}"
}

run_remote_return_now() {
    cmd_str=$1
    remote_ip=$2
    remote_user=$3

    ssh -f -n -o "StrictHostKeyChecking=no" "${remote_user}"@"${remote_ip}" "${cmd_str}"
}

send_remote() {
    src_file=$1
    target_file=$2
    send_ip=$3
    send_user=$4

    scp -r -o "StrictHostKeyChecking=no" "${src_file}" "${send_user}"@"${send_ip}":"${target_file}"
}

delete_remote() {
    delete_file=$1
    remote_ip=$2
    remote_user=$3

    run_remote "rm -rf ${delete_file}" "${remote_ip}" "${remote_user}"
}
