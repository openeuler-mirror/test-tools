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
#@Desc          :   test ebs-create-projects
#####################################

source ${OET_PATH}/libs/locallibs/common_lib.sh

# 测试对象、测试需要的工具等安装准备
function pre_test() {
    LOG_INFO "Start to prepare the test environment."
    date_name=$(date +%m%d%H%M%S)
    ccb create projects test-00-${date_name} --json ../data/json/build_single_project.json
    LOG_INFO "End to prepare the test environment."
}

# 测试点的执行
function run_test() {
    LOG_INFO "Start to run test."
    ccb build os_project=test-00-${date_name} build_type=specified -j ../data/json/single_incremental.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "build single incremental by json failed"
    ccb build os_project=test-00-${date_name} build_type=specified -y ../data/yaml/single_incremental.yaml | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "build single incremental by yaml failed"
    ccb build os_project=test-00-${date_name} -j ../data/json/single_incremental.json build_type=specified | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "build single incremental no-specified order failed"
    ccb build os_project=test-00-${date_name} -j ../data/json/single_incremental.json build_type=single | grep '\"code\": 4048'
    CHECK_RESULT $? 0 0 "build single incremental error build_type required failed"
    ccb build os_project=test-00-${date_name} -j ../data/json/single_incremental.json build_type=ysc | grep '\"code\": 4019'
    CHECK_RESULT $? 0 0 "build single incremental with build_type not exist required failed"
    ccb build os_project=test-00-${date_name} -j ../data/json/single_incremental.json | grep "build_type can't be empty"
    CHECK_RESULT $? 0 0 "single incremental build missing parameter failed"
    ccb build os_project=test-00-${date_name} build_type=specified -j ../data/json/single_incremental_fill.json | grep '\"code\": 4077'
    CHECK_RESULT $? 0 0 "build single incremental with empty verification required failed"
    ccb build os_project=test-00-${date_name} build_type=specified -j ../data/json/single_incremental_err_type.json | grep '\"code\": 4077'
    CHECK_RESULT $? 0 0 "build single incremental with error type value required failed"
    LOG_INFO "End to run test."
}

# 后置处理，恢复测试环境
function post_test() {

    LOG_INFO "Start to restore the test environment."
    ccb update projects test-00-${date_name} -j ../data/json/del.json
    LOG_INFO "End to restore the test environment."
}

main "$@"
