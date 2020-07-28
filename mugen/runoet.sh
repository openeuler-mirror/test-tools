#!/usr/bin/bash
# Copyright (c) [2020] Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
# ####################################
# @Author    	    :   lemon.higgins
# @Contact   	    :   lemon.higgins@aliyun.com
# @Date      	    :   2020-04-14 16:45:43
# @License   	    :   Mulan PSL v2
# @Version   	    :   1.0
# @Desc      	    :   Used to execute test cases
# ####################################
oet_path=$(
    cd "$(dirname "$0")" || exit 1
    pwd
)
source ${oet_path}/libs/locallibs/common_lib.sh

function usage() {
    printf "Usage:  \n
    -c: configuration environment of test framework\n
    -a: execute all use cases\n
    -f：designated test suite\n
    -r：designated test case\n
    -x：the shell script is executed in debug mode\n
    -C: the mapping in suite2case does not need to be checked.
    \n
    Example: bash runoet.sh -f test_suite -r test_case -x\n"
}

function deploy_env() {
    sed -i "s#OET_PATH.*#OET_PATH=${oet_path}#g" ${oet_path}/conf/env.conf

    if ! grep "${oet_path}/conf/env.conf" ~/.bash_profile >/dev/null 2>&1; then
        echo "source ${oet_path}/conf/env.conf" >>~/.bash_profile
    fi

    source ~/.bash_profile
}

function end_test_case() {
    case_code=$1
    exec 1>&6 6>&-
    exec 2>&7 7>&-
    LOG_INFO "The case exit by code ${case_code}"
    LOG_INFO "End to run testcase:${test_case}"

    test ${case_code} -ne 0 && ((fail_num++))
}

function run_all_cases() {
    cd ${OET_PATH}/suite2cases || exit 1
    mapfile test_suites < <(ls | sort -u)
    test ${#test_suites[*]} -eq 0 && {
        LOG_ERROR "Can't find recording about test_suites."
        end_test_case 1
        return 1
    }

    cd ${OET_PATH} || exit 1
    for test_suite in ${test_suites[*]}; do
        run_test_suite $test_suite
    done
}

function run_test_suite() {
    test_suite=$1

    if ! find ${OET_PATH}/suite2cases -type f -name ${test_suite} >/dev/null 2>&1; then
        LOG_ERROR "In the suite2cases directory, Can't find the file of testsuite:${test_suite}."
        end_test_case 1
        return 1
    fi

    while read -r test_case; do
        run_test_case $test_suite $test_case
    done <"${OET_PATH}/suite2cases/${test_suite}"
    cd ${OET_PATH} || exit 1
}

function run_test_case() {
    test_suite=$1
    test_case=$2

    log_path=${OET_PATH}/logs/${test_suite}/${test_case}
    mkdir -p ${log_path}

    [ "$isCheck"x == "yes"x ] && check_case $test_suite $test_case

    LOG_INFO "start to run testcase:${test_case}"

    exec 6>&1
    exec 7>&2
    exec >${log_path}/"$(date +%Y-%m-%d-%T)".log 2>&1

    ((case_num++))

    case_path=$(find ${OET_PATH}/testcases/${test_suite} -type f -name "${test_case}\.*" | sed -e "s/${test_case}\..*//g")
    cd ${case_path} || exit 1
    script_type=$(ls ${test_case}* | awk -F '.' '{print $NF}')

    if [[ "$script_type"x == "sh"x ]] || [[ "$script_type"x == "bash"x ]]; then
        if [ "$command_x"x == "yes"x ]; then
            bash -x ${test_case}.sh
            case_result=$?
        else
            bash ${test_case}.sh
            case_result=$?
        fi
    elif [ "$script_type"x == "py"x ]; then
        python3 ${test_case}.py
        case_result=$?
    fi

    if [ $case_result -eq 0 ]; then
        touch ${OET_PATH}/results/succeed/${test_case}
    else
        touch ${OET_PATH}/results/failed/${test_case}
    fi

    test $case_result == 0 && {
        end_test_case 0
        ((succee_num++))
    }
    test $case_result != 0 && {
        end_test_case ${case_result}
    }
}

function check_case() {
    test_suite=$1
    test_case=$2

    case_path=$(find ${OET_PATH}/testcases/${test_suite} -type f -name "${test_case}\.*" | sed -e "s/${test_case}\..*//g")

    LOG_INFO "start to check testcase:${test_case}"

    test -d ${OET_PATH}/testcases/${test_suite} || {
        LOG_ERROR "Can't find the dir of testsuite:${test_suite}."
        end_test_case 1
        return 1
    }

    test -f ${OET_PATH}/suite2cases/${test_suite} || {
        LOG_ERROR "In the suite2cases directory, Can't find the file of testsuite:${test_suite}."
        end_test_case 1
        return 1
    }

    if echo "$@" | grep -e '-C' >/dev/null 2>&1; then
        if ! grep -w ${test_case} ${OET_PATH}/suite2cases/${test_suite} >/dev/null 2>&1; then
            LOG_ERROR "In the suite2cases directory, no testcase:${test_case} is found inside the ${test_suite} file."
            end_test_case 1
            return 1
        fi
    fi

    test -f ${case_path}/${test_case}\.* || {
        LOG_ERROR "Can't find testcase. please check whether the case name is correct."
        exit 1
    }
}

function run_test() {
    test_suite=$1
    test_case=$2
    case_num=0
    fail_num=0
    succee_num=0

    if echo "$@" | grep -e '-a\|-f\|-r' >/dev/null 2>&1; then
        rm -rf ${OET_PATH}/results
        mkdir -p ${OET_PATH}/results/succeed
        mkdir -p ${OET_PATH}/results/failed
    fi

    echo "$@" | grep -e '-f' >/dev/null 2>&1 && ! echo "$@" | grep -e '-r' >/dev/null 2>&1 && {
        run_test_suite $test_suite
    }

    echo "$@" | grep -e '-f' | grep -e '-r' >/dev/null 2>&1 && {
        run_test_case $test_suite $test_case
    }

    if echo "$@" | grep -e '-a\|-f\|-r' >/dev/null 2>&1; then
        LOG_INFO "A total of ${case_num} use cases were executed, with ${succee_num} successes and ${fail_num} failures."
    fi

    if [ ${succee_num} != ${case_num} ]; then
        return 1
    fi
}

export command_x="no"
export isCheck="yes"
while getopts ":caxf:Cr:h" opt; do
    case $opt in
    x)
        command_x="yes"
        ;;
    a)
        run_all_cases
        ;;
    c)
        deploy_env
        ;;
    f)
        test_suite=$OPTARG
        [[ -z "$test_suite" ]] && {
            usage
            exit 1
        }
        ;;
    r)
        test_case=$OPTARG
        [[ -z "$test_case" ]] && {
            usage
            exit 1
        }
        ;;
    C)
        isCheck="no"
        ;;
    h)
        usage
        ;;
    *)
        usage
        ;;
    esac
done

run_test $test_suite $test_case "$@"
