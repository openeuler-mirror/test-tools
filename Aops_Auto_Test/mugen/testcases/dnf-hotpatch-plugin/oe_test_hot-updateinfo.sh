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

    DNF_INSTALL "aops-ceres dnf-hotpatch-plugin syscare"

    LOG_INFO "End to prepare the test environment."
}

function run_test() {
    LOG_INFO "Start to run test."
    dnf hot-updateinfo list cves -h | grep "usage"
    CHECK_RESULT $? 0 0 "Test dnf hot-updateinfo list cve -h failed!"
    dnf hot-updateinfo list cves | grep "patch"
    CHECK_RESULT $? 0 0 "Test dnf hot-updateinfo list cves failed!"
    dnf hot-updateinfo  list cves  --cve CVE-2023-1068 | grep 'patch'
    CHECK_RESULT $? 0 0 "Test dnf hot-updateinfo list cves --cve failed!"
    dnf hot-updateinfo 2>&1 | grep 'the following arguments are required: spec_action, with_cve'
    CHECK_RESULT $? 0 0 "Test dnf hot-updateinfo failed!"
    dnf hot-updateinfo list 2>&1  | grep 'the following arguments are required: with_cve'
    CHECK_RESULT $? 0 0 "Test dnf hot-updateinfo failed!"
    dnf hot-updateinfo cve 2>&1 | grep "invalid choice: 'cve' (choose from 'list')"
    CHECK_RESULT $? 0 0 "Test dnf hot-updateinfo cve failed!"
    dnf hot-updateinfo list cve --available 2>&1 | grep "patch"
    CHECK_RESULT $? 0 0 "Test dnf hot-updateinfo list cve --available failed!"
    dnf hot-updateinfo list cve --installed
    CHECK_RESULT $? 0 0 "Test dnf hot-updateinfo list cve --installed failed!"

    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."

    DNF_REMOVE

    LOG_INFO "End to restore the test environment."
}

main "$@"
