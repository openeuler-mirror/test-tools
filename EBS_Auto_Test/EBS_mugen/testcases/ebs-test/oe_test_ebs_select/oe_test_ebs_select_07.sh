#!/usr/bin/bash

# Copyright (c) 2023. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
#@Author        :   ysc
#@Contact       :   scyang_zjut@163.com
#@Date          :   2023/08/22
#@License       :   Mulan PSL v2
#@Desc          :   test ccb-select
#####################################

source ${OET_PATH}/libs/locallibs/common_lib.sh

# 测试对象、测试需要的工具等安装准备
function pre_test() {
    LOG_INFO "Start to prepare the test environment."
    LOG_INFO "End to prepare the test environment."
}

# 测试点的执行
function run_test() {
    LOG_INFO "Start to run test."
    ccb select projects os_project=test_for_ysc | grep os_project
    if [$? -eq 0]; then
        ccb select projects os_project=test_for_ysc -f create_time --sort 'create_time:asc' | grep 'create_time'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc --sort create_time asc successful "
        ccb select projects os_project=test_for_ysc -f create_time -s 'create_time:asc' | grep 'create_time'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s create_time asc successful "
        ccb select projects os_project=test_for_ysc -f create_time --sort 'create_time:desc' | grep 'create_time'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc --sort create_time desc successful "
        ccb select projects os_project=test_for_ysc -f create_time -s 'create_time:desc' | grep 'create_time'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s create_time desc successful "
        ccb select projects os_project=test_for_ysc -f create_time -s 'create_time:asc' --size 1 | grep 'create_time' | wc -l  | grep 1
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s create_time asc --size 1 successful "
        ccb select projects os_project=test_for_ysc -f create_time -s 'create_time:desc' --size 1 | grep 'create_time' | wc -l  | grep 1
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s create_time desc --size 1 successful "
        ccb select projects os_project=test_for_ysc -f create_time --size 1 -s 'create_time:desc'  | grep 'create_time' | wc -l  | grep 1
        CHECK_RESULT $? 0 0 "check ccb select snapshots os_project=test_for_ysc with different option order successful "
        ccb select builds os_project=test_for_ysc -f create_time --sort 'create_time:asc' | grep 'create_time'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc --sort create_time asc successful "
        ccb select builds os_project=test_for_ysc -f create_time -s 'create_time:asc' | grep 'create_time'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s create_time asc successful "
        ccb select builds os_project=test_for_ysc -f create_time --sort 'create_time:desc' | grep 'create_time'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc --sort create_time desc successful "
        ccb select builds os_project=test_for_ysc -f create_time -s 'create_time:desc' | grep 'create_time'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s create_time desc successful "
        ccb select builds os_project=test_for_ysc -f build_id --sort 'build_id:asc' | grep 'build_id'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc --sort build_id asc successful "
        ccb select builds os_project=test_for_ysc -f build_id -s 'build_id:asc' | grep 'build_id'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s build_id asc successful "
        ccb select builds os_project=test_for_ysc -f build_id --sort 'build_id:desc' | grep 'build_id'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc --sort build_id desc successful "
        ccb select builds os_project=test_for_ysc -f build_id -s 'build_id:desc' | grep 'build_id'
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s build_id desc successful "
        ccb select builds os_project=test_for_ysc -f build_id -s 'build_id:asc' --size 1 | grep 'build_id' | wc -l | grep 1
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s build_id asc --size 1 successful "
        ccb select builds os_project=test_for_ysc -f build_id -s 'build_id:desc' --size 1 | grep 'build_id' | wc -l | grep 1
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc -s build_id desc --size 1 successful "
        ccb select builds os_project=test_for_ysc -f build_id --size 1 -s 'build_id:desc' | grep 'build_id' | wc -l | grep 1
        CHECK_RESULT $? 0 0 "check ccb select projects os_project=test_for_ysc --size 1 -s build_id desc  successful "
        JOB_ID = ccb select rpms os_project=test_for_ysc -f job_id | grep job_id | awk -F: 'NR==1{print $2}'
        ccb log JOB_ID | grep http
        CHECK_RESULT $? 0 0 "check ccb log job_id successful"
        ccb log ysc | grep http
        CHECK_RESULT $? 1 0 "check ccb log not exist job_id required failed"
    else
        LOG_ERROR  "The projects test_for_ysc is not exist"
    fi
    LOG_INFO "End to run test."
}

# 后置处理，恢复测试环境
function post_test() {
    LOG_INFO "Start to restore the test environment."
    LOG_INFO "End to restore the test environment."
}

main "$@"

