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
#@Desc          :   test ccb-select-jobs
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
    ccb select jobs os_project=test_for_ysc | grep os_project
    if [$? -eq 0]; then
        ccb select jobs os_project=test_for_ysc -f snapshot_id --sort 'snapshot_id:asc' | grep 'snapshot_id'
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc --sort snapshot_id asc successful "
        ccb select jobs os_project=test_for_ysc -f snapshot_id -s 'snapshot_id:asc' | grep 'snapshot_id'
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc -s snapshot_id asc successful "
        ccb select jobs os_project=test_for_ysc -f snapshot_id --sort 'snapshot_id:desc' | grep 'snapshot_id'
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc --sort create_time desc successful "
        ccb select jobs os_project=test_for_ysc -f snapshot_id -s 'snapshot_id:desc' | grep 'snapshot_id'
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc -s create_time desc successful "
        ccb select jobs os_project=test_for_ysc -f snapshot_id -s 'snapshot_id:asc' --size 1 | grep 'snapshot_id' | wc -l  | grep 1
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc -s snapshot_id asc --size 1 successful "
        ccb select jobs os_project=test_for_ysc -f snapshot_id -s 'snapshot_id:desc' --size 1 | grep 'snapshot_id' | wc -l  | grep 1
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc -s create_time desc --size 1 successful "
        ccb select jobs os_project=test_for_ysc -f snapshot_id --size 1 -s 'snapshot_id:desc'  | grep 'snapshot_id' | wc -l  | grep 1
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc with different option order successful "
        ccb select jobs os_project=test_for_ysc -f submit_id --sort 'submit_id:asc' | grep 'submit_id'
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc --sort submit_id asc successful "
        ccb select jobs os_project=test_for_ysc -f submit_id -s 'submit_id:asc' | grep 'submit_id'
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc -s submit_id asc successful "
        ccb select jobs os_project=test_for_ysc -f submit_id --sort 'submit_id:desc' | grep 'submit_id'
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc --sort submit_id desc successful "
        ccb select jobs os_project=test_for_ysc -f submit_id -s 'submit_id:desc' | grep 'submit_id'
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc -s submit_id desc successful "
        ccb select jobs os_project=test_for_ysc -f submit_id -s 'submit_id:asc' --size 1 | grep 'submit_id' | wc -l | grep 1
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc -s submit_id asc --size 1 successful "
        ccb select jobs os_project=test_for_ysc -f submit_id -s 'submit_id:desc' --size 1 | grep 'build_id' | wc -l | grep 1
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc -s submit_id desc --size 1 successful "
        ccb select jobs os_project=test_for_ysc -f submit_id --size 1 -s 'submit_id:desc' | grep 'submit_id' | wc -l | grep 1
        CHECK_RESULT $? 0 0 "check ccb select jobs os_project=test_for_ysc --size 1 -s submit_id desc  successful "
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

