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

export OET_PATH=$(
    cd "$(dirname "$0")" || exit 1
    pwd
)

source ${OET_PATH}/libs/locallibs/common_lib.sh

export EXECUTE_T="30m"
export case_num=0
export success_num=0
export fail_num=0
export isCheck=yes
export command_x=no
export conf_file="/etc/mugen/env.conf"
export cases_url="https://gitee.com/openeuler/integration-test.git"
if [ ! -d "/etc/mugen" ]; then
    export conf_file="${OET_PATH}/conf/env.conf"
    mkdir -p ${OET_PATH}/conf
fi

function usage() {
    printf "Usage:  \n
    -c: configuration environment of test framework\n
    -d: download test cases what provided by the openEuler community.\n
    -a: execute all use cases\n
    -f：designated test suite\n
    -r：designated test case\n
    -x：the shell script is executed in debug mode\n
    -C: the mapping in suite2cases does not need to be checked.(you must ensure that the case name does't exist.)
    \n
    Example: 
        run all cases:
          normal mode:
            bash mugen.sh -a
          debug mode:
            bash mugen.sh -xa

        run test suite:
          normal mode:
            bash mugen.sh -f test_suite
          debug mode:
            bash mugen.sh -xf test_suite

        run test case:
          normal mode:
            bash mugen.sh -f test_suite -r test_case
          normal mode and no check suite2case:
            bash mugen.sh -f test_suite -Cr test_case
          debug mode:
            bash mugen.sh -xf test_suite -r test_case
          debug mode and no check suite2case:
            bash mugen.sh -xf test_suite -Cr test_case
        \n
	configure env of test framework:\n
	    bash mugen.sh -c localip username passwd port,like bash mugen.sh -c 1.1.1.1 root xxxxxxx 4567\n"
}

function deploy_conf() {
    local ipaddr=$2
    local user=${3:-"root"}
    local password=${4:-"openEuler12#$"}
    local connport=${5:-"22"}

    if [ -z "$ipaddr" ] || [ -z "$user" ] || [ -z "$password" ] || [ -z "$connport" ]; then
        LOG_ERROR "Parameter missing."
        exit 1
    fi

    if ! SSH_CMD "echo" "$ipaddr" "$password" "$user" "" "$connport" > /dev/null; then
	    LOG_ERROR "The user name($user) and password($password) can't be used to log in the address($ipaddr) and port($connport)"
        exit 1
    fi

    if [ -f "$conf_file" ]; then
        node_num=$(grep -ci 'node' "$conf_file")
    fi
    ((node_num++))

    localtion=local
    ip addr show | grep $ipaddr >/dev/nul || localtion=remote

    conf=$(SSH_CMD "
    nics=(\$(ls /sys/class/net | grep -Ewv 'lo.*|docker.*|bond.*|vlan.*|virbr.*|br.*|vnet.*' | sed 's/ $//g'))
    for nic in \${nics\[*\]}; do
        mac+=(\$(cat /sys/class/net/\${nic}/address))

        ipv4+=(\$(ip addr show \${nic} | grep -w inet | awk '{print \$2}' | awk -F '/' '{print \$1}'))

        ipv6+=(\$(ip addr show \${nic} | grep -w inet6 | awk '{print \$2}' | awk -F '/' '{print \$1}'))
    done

    machines=virtual
    hostnamectl | grep 'Virtualization: kvm' || machines=physical

    frame=$(uname -m)

    result=NODE=$node_num,LOCALTION=$localtion,USER=$user,PASSWORD=$password,MACHINE=\$machines,FRAME=\$frame,NICS='\('\${nics\[@\]}'\)',MAC='\('\${mac\[*\]}'\)',IPV4='\('\${ipv4\[*\]}'\)',IPV6='\('\${ipv6\[*\]}'\)'

    test \$machines == physical && {
        dnf install ipmitool -y >/dev/null
        bmcip=\$(ipmitool lan print | grep -i 'ip address' | grep -iv 'source' | awk '{print \$NF}')
        result+="BMCIP=\$bmcip,BMCUSER=,BMCPASSWORD="
    }

    echo -e \$result
    " "$ipaddr" "$password" "$user" | tail -n 1)

    echo "$conf" | grep ERROR >/dev/nul && {
        LOG_ERROR "Failed in remote CMD operation:1"
        exit 1
    }
    echo -e "\n$conf" >>"$conf_file"
    dos2unix "$conf_file" >/dev/nul 2>&1

}

function download_testcases() {
    local tmpdir
    tmpdir=$(mktemp -d)
    git clone "$cases_url" "$tmpdir"
    cp "$tmpdir"/* "$OET_PATH" -r
    rm -rf "$tmpdir"
}

function process() {
    local cmd=$1

    (sleep "$EXECUTE_T" && {
        case_pid=$(pgrep -f "$cmd")
        test -n "$case_pid" && {
            if kill -9 "$case_pid" >/dev/nul 2>&1; then
                LOG_WARN "The case execution timeout."
            fi
        }
    }) 2>/dev/nul &

    exec 6>&1
    exec 7>&2
    exec >"$log_path"/"$(date +%Y-%m-%d-%T)".log 2>&1

    ((case_num++))

    $cmd
    ret_code=$?

    exec 1>&6 6>&-
    exec 2>&7 7>&-

    sleep_pid=$(pgrep -f "sleep $EXECUTE_T")
    test -n "$sleep_pid" && kill -9 "$sleep_pid"

    if [ $ret_code -eq 0 ]; then
        LOG_INFO "The case exit by code $ret_code."
        mkdir -p ${OET_PATH}/results/succeed
        touch ${OET_PATH}/results/succeed/${test_case}
        ((success_num++))
    else
        LOG_ERROR "The case exit by code $ret_code."
        mkdir -p ${OET_PATH}/results/failed
        touch ${OET_PATH}/results/failed/${test_case}
        ((fail_num++))
    fi
}

function run_test_case() {

    local test_suite=$1
    local test_case=$2

    if [[ -z "$test_suite" || -z "$test_case" ]]; then
        LOG_ERROR "Parameter(test suite or test case) loss."
        exit 1
    fi

    [ "$isCheck"x == "yes"x ] && {
        [ -z "$(find "$OET_PATH"/suite2cases -name "$test_suite")" ] && {
            LOG_ERROR "In the suite2cases directory, Can't find the file of testsuite:${test_suite}."
            return 1
        }
        if ! grep -q --line-regexp --fixed-strings "$test_case" suite2cases/"$test_suite"; then
            LOG_ERROR "In the suite2cases directory, Can't find the case name:${test_case} in the file of testsuite:${test_suite}."
            return 1
        fi
    }

    mapfile suite_paths < <(find "$OET_PATH"/testcases -name "$test_suite")

    if [ ${#suite_paths[@]} -ge 1 ]; then
        for suite_path in ${suite_paths[*]}; do
            case_path=()
            while IFS="" read -r line; do
                case_path+=("${line%/*}")
            done < <(find "$suite_path" -type f -name "${test_case}.*")

            if [ ${#case_path[@]} -gt 1 ]; then
                LOG_ERROR "There are multiple use cases with the same use case name:${test_case} under the test suite:${test_suite}."
                return 1
            elif [ ${#case_path[@]} -eq 1 ]; then
                break
            fi
        done

        [ ${#case_path[@]} -eq 0 ] && {
            LOG_ERROR "No test cases found under the test suite:${test_suite}."
            return 1
        }
    fi

    log_path=${OET_PATH}/logs/${test_suite}/${test_case}
    mkdir -p ${log_path}

    LOG_INFO "start to run testcase:$test_case"

    pushd "${case_path[*]}" >/dev/null || return 1

    local execute_t
    execute_t=$(grep -w --fixed-strings EXECUTE_T ${test_case}.* 2>/dev/nul | awk -F '=' '{print $NF}')
    test -n "$execute_t" && EXECUTE_T=$execute_t

    local script_type
    script_type=$(ls ${test_case}.* | awk -F '.' '{print $NF}')

    if [[ "$script_type"x == "sh"x ]] || [[ "$script_type"x == "bash"x ]]; then
        if [ "$command_x"x == "yes"x ]; then
            process "bash -x ${test_case}.sh"
        else
            process "bash ${test_case}.sh"
        fi
    elif [ "$script_type"x == "py"x ]; then
        process "python3 ${test_case}.py"
    fi

    popd >/dev/nul || return 1

    LOG_INFO "End to run testcase:$test_case"
}

function case_count() {

    LOG_INFO "A total of ${case_num} use cases were executed, with ${success_num} successes and ${fail_num} failures."

    if [ ${success_num} != ${case_num} ]; then
        exit 1
    fi
}

function run_test_suite() {
    local test_suite=$1

    [ -z "$(find "$OET_PATH"/suite2cases -name "$test_suite")" ] && {
        LOG_ERROR "In the suite2cases directory, Can't find the file of testsuite:${test_suite}."
        return 1
    }

    for test_case in $(shuf ${OET_PATH}/suite2cases/${test_suite} | tr -d ' '); do
        run_test_case "$test_suite" "$test_case"
    done
}

function run_all_cases() {
    mapfile test_suites < <(find ${OET_PATH}/suite2cases/ -type f -name "*" | awk -F '/' '{print $NF}')
    test ${#test_suites[@]} -eq 0 && {
        LOG_ERROR "Can't find recording about test_suites."
        return 1
    }

    for test_suite in ${test_suites[*]}; do
        run_test_suite "$test_suite"
    done
}

function load_conf() {
    if [ ! -f "$conf_file" ]; then
        LOG_ERROR "The configuration file does not exist."
        exit 1
    fi

    node_num=$(grep -ci 'node=' "$conf_file")

    tmp=$(mktemp)
    echo -e "function share_arg() {" >"$tmp"
    for id in $(seq 1 $node_num); do
        while IFS="" read -r var; do
            if echo "$var" | grep '(' >/dev/nul; then
                echo -e "$var" >>"$tmp"
            else
                declare -g -x ${var}
            fi
        done < <(grep -iw "node=$id" "$conf_file" | sed 's/,/\n/g' | sed "/node=/d;s/^/NODE${id}_/g")
    done
    echo -e "}" >>"$tmp"
    if grep '=(' "$tmp" >/dev/nul; then
        source "$tmp"
        export -f share_arg
    fi
}

function pre_run() {
    rm -rf ${OET_PATH}/results
    load_conf
    $@
    case_count
}

if ! rpm -qa | grep '^expect' >/dev/null 2>&1; then
    yum -y install expect dos2unix >/dev/nul
fi

while getopts ":xdcaf:Cr:h" option; do
    case $option in
    x)
        export command_x="yes"
        ;;
    a)
        pre_run run_all_cases
        ;;
    f)
        test_suite=$OPTARG
        [[ -z "$test_suite" ]] && {
            usage
            exit 1
        }
        echo "$@" | grep -e '-r\|-Cr' >/dev/null 2>&1 || {
            pre_run "run_test_suite $test_suite"
        }
        ;;
    r)
        test_case=$OPTARG
        [[ -z "$test_case" ]] && {
            usage
            exit 1
        }
        pre_run "run_test_case $test_suite $test_case"
        ;;
    C)
        isCheck="no"
        ;;
    c)
        deploy_conf "$@"
        ;;
    d)
        download_testcases
        ;;
    h)
        usage
        ;;
    *)
        usage
        ;;
    esac
done
