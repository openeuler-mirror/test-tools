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
    aops-ceres apollo --scan '{"check_items": [], "check": false, "basic": false}'

    LOG_INFO "End to prepare the test environment."
}

function run_test() {
    LOG_INFO "Start to run test."
    aops-ceres apollo --fix 2>&1 | grep "argument --fix: expected one argument"
    CHECK_RESULT $? 0 0 "Test fix cve without argument failed"
    aops-ceres apollo --fix '{"cve_id": "CVE-2023-1068","hotpatch": false}]}' 2>&1 | grep "'Param.Error' is not of type 'object'"
    CHECK_RESULT $? 0 0 "Test fix cve with invalid argument failed"
    aops-ceres apollo --fix '{"fix_type": "hotpatch","check_items": [], "rpms": [{ "installed_rpm": "kernel-5.10.0-153.12.0.92.oe2203sp2.x86_64", "available_rpm": "patch-kernel-5.10.0-153.12.0.92.oe2203sp2-ACC-1-1.x86_64"}],"accepted": false}' 2>&1 | grep -E "success|fail"
    CHECK_RESULT $? 0 0 "Test fix cve failed"
    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."

    DNF_REMOVE

    LOG_INFO "End to restore the test environment."
}

main "$@"
