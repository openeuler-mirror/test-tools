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
    dnf hotupgrade ${patch_list[0]} -y
    LOG_INFO "End to prepare the test environment."
}

function run_test() {
    LOG_INFO "Start to run test."
    dnf hotpatch -h | grep "usage"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch -h failed!"
    dnf hotpatch --list | grep "kernel"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch --list failed!"
    dnf hotpatch --list cves | grep "CVE"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch --list cves failed!"
    dnf hotpatch --list cves --cve ${cve_list[0]} | grep "${cve_list[0]}"
    CHECK_RESULT $? 0 0 "Test dnf hotpatch --list cves --cve ${cve_list[0]} failed!"
    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."
    DNF_REMOVE  ${patch_list[0]}
    DNF_REMOVE
    LOG_INFO "End to restore the test environment."
}

main "$@"
