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
    printf "$(date +%Y-%m-%d\ %T)  $0  [ INFO  ]  %s\n" "$@"
}

function LOG_WARN() {
    printf "$(date +%Y-%m-%d\ %T)  $0  [ WARN  ]  %s\n" "$@"
}

function LOG_ERROR() {
    printf "$(date +%Y-%m-%d\ %T)  $0  [ ERROR ]  %s\n" "$@"
}

function GET_RANDOM_PORT() {
    start_port=${1-1}
    end_port=${1-10000}

    mapfile used_ports < <(printf %d\\n 0x$(cat /proc/net/tcp* /proc/net/udp* | sed '/local_address/d' | awk -F ':' '{print $3}' | awk '{print $1}' | sort -u))

    random_port=0
    while [ $random_port == 0 ]; do
        random_port=$(shuf -i ${start_port}-${end_port} -n1)
        for used_port in "${used_ports[@]}"; do
            test ${used_port} -eq ${random_port} && random_port=0
        done
    done

    echo $random_port
}

function DNF_INSTALL() {
    __pkg_list=$1
    if [ -z "${__pkg_list}" ]; then
        LOG_ERROR "Wrong parameter."
        exit 1
    fi
    reponames=$(grep '^\[.*\]' /etc/yum.repos.d/*.repo | tr -d [] | sed -e ':a;N;$!ba;s/\n/ /g')
    mapfile -t __install_pkgs < <(dnf --assumeno install ${__pkg_list[*]} 2>&1 | grep -wE "${reponames// /|}" | grep -wE "$(uname -m)|noarch" | awk '{print $1}')
    dnf -y install ${__pkg_list[*]}

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
    remoteip=$1
    remotepasswd=$2
    remoteuser=$3
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
            test -n "$error_log" && LOG_ERROR "$error_log"
            ((exec_result++))
        }
    else
        test "$actual_result"x == "$expect_result"x && {
            test -n "$error_log" && LOG_ERROR "$error_log"
            ((exec_result++))
        }
    fi

    return 0
}

function CASE_RESULT() {
    case_re=$1

    test -z "$exec_result" && {
        test $case_re -eq 0 && {
            LOG_INFO "succeed to execute the case."
            exec_result=""
            exit 0
        }
        LOG_ERROR "failed to execute the case."
        exit $case_re
    }

    test $exec_result -gt 0 && {
        LOG_ERROR "failed to execute the case."
        exit $exec_result
    }
    LOG_INFO "succeed to execute the case."
    exit $exec_result
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

function POST_TEST_DEFAULT() {
    LOG_INFO "$0 post_test"
}

function main() {
    share_arg

    if [ -n "$(type -t post_test)" ]; then
        trap post_test EXIT INT TERM || exit 1
    else
        trap POST_TEST_DEFAULT EXIT INT TERM || exit 1
    fi

    if ! rpm -qa | grep expect >/dev/null 2>&1; then
        dnf -y install expect
    fi

    if [ -n "$(type -t config_params)" ]; then
        config_params
    fi

    if [ -n "$(type -t pre_test)" ]; then
        pre_test
    fi

    if [ -n "$(type -t run_test)" ]; then
        run_test
        CASE_RESULT $?
    fi
}
