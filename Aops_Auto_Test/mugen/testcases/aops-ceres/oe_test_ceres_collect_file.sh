#!/usr/bin/bash

# Copyright (c) 2021. Huawei Technologies Co.,Ltd.ALL rights reserved.
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
#@Desc      	:   Take the test ls command as an example
#####################################

source ${OET_PATH}/libs/locallibs/common_lib.sh

function pre_test() {
    LOG_INFO "Start to prepare the test environment."

    DNF_INSTALL "aops-ceres"
    touch test_repo.repo

    LOG_INFO "End to prepare the test environment."
}

function run_test() {
    LOG_INFO "Start to run test."

    aops-ceres collect --file '["/etc/aops/ceres.conf"]' | grep "\"success_files\": \[\"/etc/aops/ceres.conf\"\]"
    CHECK_RESULT $? 0 0 "test collect exist file failed"
    aops-ceres collect --f '["/etc/aops/ceres.conf1"]' | grep "\"fail_files\": \[\"/etc/aops/ceres.conf1\"\]"
    CHECK_RESULT $? 0 0 "test collect non-exist file failed"
    aops-ceres collect --f '["/etc/aops/ceres.conf1"]' 2>&1 | grep "file /etc/aops/ceres.conf1 cannot be found or is not a file"
    CHECK_RESULT $? 0 0 "test collect non-exist file failed"
    aops-ceres collect --f '/opt/gala-gopher/meta/tcp_link.meta' 2>&1 | grep "'Param.Error' is not of type 'array'"
    CHECK_RESULT $? 0 0 "test collect file more than 1MB failed"
    aops-ceres collect --f './test_repo.repo' 2>&1 | grep "'Param.Error' is not of type 'array'"
    CHECK_RESULT $? 0 0 "test collect empty file failed"
    chmod 777 test_repo.repo
    aops-ceres collect --f './test_repo.repo' 2>&1 | grep "'Param.Error' is not of type 'array'"
    CHECK_RESULT $? 0 0 "test collect executable file failed"

    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."

    DNF_REMOVE
    rm -rf test_repo.repo

    LOG_INFO "End to restore the test environment."
}

main "$@"
