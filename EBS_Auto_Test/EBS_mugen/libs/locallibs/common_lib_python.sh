#!/usr/bin/bash
# Copyright (c) [2021] Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
# @Author  : lemon-higgins
# @email   : lemon.higgins@aliyun.com
# @Date    : 2021-04-20 15:11:47
# @License : Mulan PSL v2
# @Version : 1.0
# @Desc    :
#####################################

function LOG_INFO() {
    message=${*-"Developer does not write the log messages."}
    python3 ${OET_PATH}/libs/locallibs/mugen_log.py --level 'info' --message "$message"
}

function LOG_WARN() {
    message=${*-"Developer does not write the log messages."}
    python3 ${OET_PATH}/libs/locallibs/mugen_log.py --level 'warn' --message "$message"
}

function LOG_DEBUG() {
    message=${*-"Developer does not write the log messages."}
    python3 ${OET_PATH}/libs/locallibs/mugen_log.py --level 'debug' --message "$message"
}

function LOG_ERROR() {
    message=${*-"Developer does not write the log messages."}
    python3 ${OET_PATH}/libs/locallibs/mugen_log.py --level 'error' --message "$message"
}

function SSH_CMD() {
    cmd=$1
    remoteip=$2
    remotepasswd=${3-openEuler12#$}
    remoteuser=${4-root}
    timeout=${5-300}
    connport=${6-22}

    bash ${OET_PATH}/libs/locallibs/sshcmd.sh -c "$cmd" -i "$remoteip" -u "$remoteuser" -p "$remotepasswd" -t "$timeout" -o "$connport"
    ret=$?
    test $ret -ne 0 && LOG_ERROR "Failed in remote CMD operation:$ret"
    return $ret
}

function SSH_SCP() {
    src=$1
    dest=$2
    remotepasswd=${3-openEuler12#$}
    connport=${4-22}

    bash ${OET_PATH}/libs/locallibs/sshscp.sh -p "$remotepasswd" -o "$connport" -s "$src" -d "$dest"
    ret=$?
    test $ret -ne 0 && LOG_ERROR "Failed in remote SCP operation: $ret"
    return $ret
}

function P_SSH_CMD() {
    python3 ${OET_PATH}/libs/locallibs/ssh_cmd.py "$@"
}

function SFTP() {
    python3 ${OET_PATH}/libs/locallibs/sftp.py "$@"
}

function TEST_NIC() {
    id=${1-1}
    python3 ${OET_PATH}/libs/locallibs/get_test_device.py \
        --device nic --node "$id"
}

function TEST_DISK() {
    id=${1-1}
    python3 ${OET_PATH}/libs/locallibs/get_test_device.py \
        --device disk --node "$id"
}

function DNF_INSTALL() {
    pkgs=$1
    node=${2-1}
    #多节点初始系统环境相同，本地和远端安装的包，在任何节点不不应该存在
    [ -z "$tmpfile" ] && tmpfile=""

    tmpfile2=$(python3 ${OET_PATH}/libs/locallibs/rpm_manage.py \
        install --pkgs "$pkgs" --node $node --tempfile "$tmpfile")

    [ -z "$tmpfile" ] && tmpfile=$tmpfile2
}

function DNF_REMOVE() {
    node=${1-1}
    pkg_list=${2-""}
    mode=${3-0}

    if [[ -z "$tmpfile" && -z "$pkg_list" ]]; then
        LOG_WARN "no thing to do."
        return 0
    fi

    [ $mode -ne 0 ] && {
        tmpf=$tmpfile
        tmpfile=""
    }

    if [ "$node" == 0 ]; then
        node_num=$(python3 ${OET_PATH}/libs/locallibs/read_conf.py node-num)

        for node_id in $(seq 1 $node_num); do
            python3 ${OET_PATH}/libs/locallibs/rpm_manage.py \
                remove --node $node_id --pkgs "$pkg_list" --tempfile "$tmpfile"
        done
    else
        python3 ${OET_PATH}/libs/locallibs/rpm_manage.py \
            remove --node $node --pkgs "$pkg_list" --tempfile "$tmpfile"
    fi

    [ $mode -ne 0 ] && {
        tmpfile=$tmpf
    }
}

function GET_FREE_PORT() {
    ip=${1-""}
    start_port=${2-1000}
    end_port=${3-10000}
    python3 ${OET_PATH}/libs/locallibs/free_port.py \
        get --ip "$ip" --start "$start_port" --end "$end_port"
}

function IS_FREE_PORT() {
    port=$1
    ip=${2-""}
    python3 ${OET_PATH}/libs/locallibs/free_port.py \
        check --port "$port" --ip "$ip"
}

function REMOTE_REBOOT() {
    node=${1-2}
    waittime=${2-""}
    if [ "$waittime"x != ""x ]; then
        python3 ${OET_PATH}/libs/locallibs/remote_reboot.py "reboot" --node $node --waittime $waittime
    else
        python3 ${OET_PATH}/libs/locallibs/remote_reboot.py "reboot" --node $node
    fi
}

function REMOTE_REBOOT_WAIT() {
    node=${1-2}
    waittime=${2-""}
    if [ "$waittime"x != ""x ]; then
        python3 ${OET_PATH}/libs/locallibs/remote_reboot.py "wait" --node $node --waittime $waittime
    else
        python3 ${OET_PATH}/libs/locallibs/remote_reboot.py "wait" --node $node
    fi
}

function SLEEP_WAIT() {
    wait_time=$1
    cmd=$2
    mode=${3-1}
    python3 ${OET_PATH}/libs/locallibs/sleep_wait.py --time $wait_time --cmd "$cmd" --mode $mode
}
