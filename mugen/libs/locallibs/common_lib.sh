#!/usr/bin/bash
# Copyright (c) [2020] Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
#@Author    	:   lemon.higgins
#@Contact   	:   lemon.higgins@aliyun.com
#@Date      	:   2020-04-09 09:39:43
#@License   	:   Mulan PSL v2
#@Version   	:   1.0
#@Desc      	:   Public function
#####################################

function LOG_INFO() {
    printf "$(date +%Y-%m-%d\ %T)  $0  [ INFO ]  %s\n" "$@"
}

function LOG_WARN() {
    printf "$(date +%Y-%m-%d\ %T)  $0  [ WARN ]  %s\n" "$@"
}

function LOG_ERROR() {
    printf "$(date +%Y-%m-%d\ %T)  $0  [ ERROR ]  %s\n" "$@"
}

function DNF_INSTALL() {
    __pkg_list=$1
    if [ -z "${__pkg_list}" ]; then
        LOG_ERROR "Wrong parameter."
        exit 1
    fi
    reponames=$(grep '^\[.*\]' /etc/yum.repos.d/*.repo | tr -d [] | sed -e ':a;N;$!ba;s/\n/ /g')
    mapfile -t __install_pkgs < <(dnf -y install ${__pkg_list[*]} | grep -wE "${reponames// /|}" | grep -wE "$(uname -m)|noarch" | awk '{print $1}')

    if ! dnf -y install ${__pkg_list[*]}; then
        LOG_ERROR "pkg_list:${__pkg_list[*]} install failed."
        exit 1
    fi

    __installed_pkgs+=" ${__install_pkgs[*]}"

    return 0
}

function DNF_REMOVE() {
    __pkg_list=$1
    type=${2-0}

    if [ ${type} -eq 0 ]; then
        if ! dnf -y remove ${__installed_pkgs[*]} ${__pkg_list[*]}; then
            LOG_ERROR "pkg_list:${__installed_pkgs[*]} ${__pkg_list[*]} remove failed."
            exit 1
        fi
    else
        if ! dnf -y remove ${__pkg_list}; then
            LOG_ERROR "pkg_list:${__pkg_list[*]} remove failed."
            exit 1
        fi
    fi
}

function SLEEP_WAIT() {
    wait_time=${1-1}
    cmd=$2
    sleep_time=0

    while [ $sleep_time -lt $wait_time ]; do
        sleep 1
        if [ -n "$cmd" ]; then
            if $cmd; then
                return 0
            fi
        fi
        ((sleep_time++))
    done
}

function REMOTE_REBOOT_WAIT() {
    remoteuser=$1
    remotepasswd=$2
    remoteip=$3
    count=0

    if [[ "$(dmidecode -s system-product-name)" =~ "KVM" ]]; then
        SLEEP_WAIT 60
    else
        SLEEP_WAIT 200
    fi

    while [ $count -lt 60 ]; do
        if ping -c 1 $remoteip; then
            if SSH_CMD "echo '' > /dev/null 2>&1" $remoteip $remotepasswd $remoteuser; then
                return 0
            else
                SLEEP_WAIT 10
                ((count++))
            fi
        else
            SLEEP_WAIT 10
            ((count++))
        fi
    done

    return 1
}

function CHECK_RESULT() {
    actual_result=$1
    expect_result=${2-0}
    mode=${3-0}
    error_log=$4

    if [ -z "$actual_result" ]; then
        LOG_ERROR "Missing actual error code."
        return 1
    fi

    if [ $mode -eq 0 ]; then
        test "$actual_result"x != "$expect_result"x && {
            LOG_ERROR "$error_log"
            ((exec_result++))
            all_result="$all_result $exec_result"
        }
    else
        test "$actual_result"x == "$expect_result"x && {
            LOG_ERROR "$error_log"
            ((exec_result++))
            all_result="$all_result $exec_result"
        }
    fi
}

function CASE_RESULT() {
    [[ -z $exec_result ]] && {
        LOG_INFO "The case execute succeed."
        exec_result=0
        all_result=0
        return 0
    }

    for ret in "${all_result[@]}"; do
        LOG_ERROR "Test point $ret: execute failed."
    done
    exec_result=0
    all_result=0
    return 1
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

function main() {
    trap post_test EXIT INT TERM

    if ! rpm -qa | grep expect >/dev/null 2>&1; then
        dnf install expect -y
    fi

    config_params

    pre_test

    run_test

    CASE_RESULT
    test $? -eq 0 || exit 1
}
