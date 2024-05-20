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

    LOG_INFO "End to prepare the test environment."
}

function run_test() {
    LOG_INFO "Start to run test."
    aops-ceres apollo --set-repo '{    "repo_info":{        "name":"update",        "dest":"/etc/yum.repos.d/aops-update.repo",        "repo_content":"[aops-update]\nname=update\nbaseurl=https://repo.openeuler.org/openEuler-22.03-LTS-SP1/update/$basearch/\nenabled=1\ngpgcheck=1\ngpgkey=https://repo.openeuler.org/openEuler-22.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler"},    "check_items":[],    "check":false}'  | grep  "{\"code\": \"Succeed\", \"msg\": \"operate success\"}"
    CHECK_RESULT $? 0 0 "test set repo failed"
    test -e /etc/yum.repos.d/aops-update.repo
    CHECK_RESULT $? 0 0 "aops-update.repo non exist"
    aops-ceres apollo --set-repo 2>&1 | grep 'error: argument --set-repo: expected one argument'
    CHECK_RESULT $? 0 0 "test set invalid repo failed"
    aops-ceres apollo --set-repo '{}' 2>&1 | grep "'repo_info' is a required property"
    CHECK_RESULT $? 0 0 "test repo_info is blank failed"
    aops-ceres apollo --set-repo 'invalid.repo' 2>&1 | grep "'Param.Error' is not of type 'object'"
    CHECK_RESULT $? 0 0 "test verify invalid param failed"
    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."

    DNF_REMOVE
    rm -rf /etc/yum.repos.d/aops-update.repo

    LOG_INFO "End to restore the test environment."
}

main "$@"
