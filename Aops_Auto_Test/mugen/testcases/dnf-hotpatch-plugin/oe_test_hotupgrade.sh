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

source common.sh
function pre_test() {
    LOG_INFO "Start to prepare the test environment."
    DNF_INSTALL  "aops-ceres dnf-hotpatch-plugin syscare"
    get_cve_and_patch
    LOG_INFO "End to prepare the test environment."
}

function run_test() {
    LOG_INFO "Start to run test."
    dnf hotupgrade -h | grep "usage"
    CHECK_RESULT $? 0 0 "Test dnf hotupgrade -h failed!"
    dnf hotupgrade ${patch_list[0]} -y | grep "Apply hot patch succeed"
    CHECK_RESULT $? 0 0 "Test dnf hotupgrade ${patch_list[0]} failed!"
    syscare list | grep "ACTIVED"
    CHECK_RESULT $? 0 0 "Test syscare list failed!"
    dnf hotupgrade invalid-patch   | grep 'Cannot parse NEVRA for package "invalid-patch"'
    CHECK_RESULT $? 0 0 "Test dnf hotupgrade invalid-patch failed!"
    dnf hotupgrade --cve ${cve_list[1]} -y | grep 'Apply hot patch succeed'
    CHECK_RESULT $? 0 0 "Test dnf hotupgrade --cve ${cve_list[1]} failed!"
    dnf hotupgrade --cve invalid-cve  | grep "The cve doesn't exist or cannot be fixed by hotpatch: invalid-cve"
    CHECK_RESULT $? 0 0 "Test dnf hotupgrade --cve invalid-cve failed!"
    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."
    DNF_REMOVE patch-kernel* 
    DNF_REMOVE
    LOG_INFO "End to restore the test environment."
}

main "$@"
