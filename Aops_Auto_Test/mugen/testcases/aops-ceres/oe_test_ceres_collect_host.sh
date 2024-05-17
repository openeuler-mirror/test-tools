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
    aops-ceres collect --host '[]' | grep -wE "cpu|disk|memory|os"
    CHECK_RESULT $? 0 0 "test collect host info failed"
    aops-ceres collect --host '["cpu"]' | grep -wE "architecture|core_count|model_name|vendor_id|l1d_cache|l1i_cache|l2_cache|l3_cache"
    CHECK_RESULT $? 0 0 "test collect host cpu info failed"
    aops-ceres collect --host '["cpccu"]' 2>&1 | grep "'cpccu' is not one of \['os', 'cpu', 'memory', 'disk'\]"
    CHECK_RESULT $? 0 0 "test collect host non-exist info failed"
    aops-ceres collect --host 'cpu' 2>&1 | grep "'Param.Error' is not of type 'array'"
    CHECK_RESULT $? 0 0 "Failed to test host info with incorrect type"
    aops-ceres collect --host  2>&1 | grep "aops-ceres collect: error: argument --host: expected one argument"
    CHECK_RESULT $? 0 0 "Failed to test host info with missing argument"
    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."

    DNF_REMOVE

    LOG_INFO "End to restore the test environment."
}

main "$@"
