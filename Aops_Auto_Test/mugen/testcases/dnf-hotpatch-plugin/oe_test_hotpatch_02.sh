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
    DNF_INSTALL "aops-ceres dnf-hotpatch-plugin syscare"
    get_cve_and_patch
    LOG_INFO "End to prepare the test environment."
}

function run_test() {
    LOG_INFO "Start to run test."
    DNF_INSTALL ${patch_list[0]}
    CHECK_RESULT $? 0 0 "Test install $patch_name failed!"
    patch_name=$(syscare list | awk -F ' ' 'NR==2{print $2}')
    dnf hotpatch --apply $patch_name | grep "apply hot patch '$patch_name' succeed"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch --apply $patch_name failed!"
    dnf hotpatch --list | grep "ACTIVED"
    CHECK_RESULT $? 0 0 "Test hotptach status is actived failed!"
    dnf hotpatch --deactive $patch_name | grep "deactive hot patch '$patch_name' succeed"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch --deactive $patch_name failed!"
    dnf hotpatch --list | grep "DEACTIVED"
    CHECK_RESULT $? 0 0 "Test hotptach status is deactived failed!"
    dnf hotpatch --active $patch_name | grep "active hot patch '$patch_name' succeed"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch --active $patch_name failed!"
    dnf hotpatch --list | grep "ACTIVED"
    CHECK_RESULT $? 0 0 "Test hotptach status is actived failed!"
    dnf hotpatch --accept  $patch_name | grep "accept hot patch '$patch_name' succeed"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch --accept $patch_name failed!"
    dnf hotpatch --list | grep "ACCEPTED"
    CHECK_RESULT $? 0 0 "Test hotptach status is acceptef failed!"
    dnf hotpatch --remove $patch_name | grep "remove hot patch '$patch_name' succeed"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch --remove $patch_name failed!"
    dnf hotpatch --list | grep "NOT-APPLIED"
    CHECK_RESULT $? 0 0 "Test hotptach status is not-applied failed!"

    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."
    DNF_REMOVE ${patch_list[0]}
    DNF_REMOVE
    LOG_INFO "End to restore the test environment."
}

main "$@"
