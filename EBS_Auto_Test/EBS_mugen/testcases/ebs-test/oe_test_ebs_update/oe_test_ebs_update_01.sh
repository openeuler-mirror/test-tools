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
#@Desc          :   test ebs-update-projects
#####################################

source ${OET_PATH}/libs/locallibs/common_lib.sh

# 测试对象、测试需要的工具等安装准备
function pre_test() {
    LOG_INFO "Start to prepare the test environment."
    date_name=$(date +%m%d%H%M%S)
    ccb create projects test-00-${date_name} -j ../data/json/test_for_select_project.json
    LOG_INFO "End to prepare the test environment."
}

# 测试点的执行
function run_test() {
    LOG_INFO "Start to run test."
    ccb update projects test-00-${date_name} -j ../data/json/user_add.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects by add users successful"
    ccb update projects test-00-${date_name} -j ../data/json/user_del.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0  "check ccb update projects by del users successful"
    ccb update projects test-00-${date_name} -j ../data/json/user_add_err.json | grep '\"code\": 4030'
    CHECK_RESULT $? 0 0 "check ccb update projects by not exist user required failed"
    ccb update projects test-00-${date_name} -j ../data/json/user_del_err.json | grep '\"code\": 4015'
    CHECK_RESULT $? 0 0 "check ccb update projects by not exist user required failed"
    ccb update projects test-00-${date_name} package_overrides.redis.lock=true | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects k=v successful"
    ccb update projects test-00-${date_name} package_overrides.redis.lock=false | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects k=v successful"
    ccb update projects test-00-${date_name} package_overrides.redis.lock=ysc | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "check ccb update projects k=error_value required failed"
    ccb update projects test-00-${date_name} -j ../data/json/update_my_spec_add.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with my_spec_add successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_my_spec_del.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with my_spec_del successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_my_spec.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with my_spec successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_my_spec_err.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "check ccb update projects with my_spec_error_url required failed"
    ccb update projects test-00-${date_name} -j ../data/json/update_layer_urls_add.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with layer_urls_add successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_layer_urls_del.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with layer_urls_del successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_layer_urls.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with layer_urls successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_layer_urls_err.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "check ccb update projects with err layer_urls required failed"
    LOG_INFO "End to run test."
}

# 后置处理，恢复测试环境
function post_test() {
    LOG_INFO "Start to restore the test environment."
    ccb update projects test-00-${date_name} -j ../data/json/del.json
    LOG_INFO "End to restore the test environment."
}

main "$@"

