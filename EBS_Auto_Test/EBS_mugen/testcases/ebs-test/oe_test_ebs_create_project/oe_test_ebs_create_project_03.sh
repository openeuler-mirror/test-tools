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
#@Author    	:   ysc
#@Contact   	:   scyang_zjut@163.com
#@Date      	:   2023/08/22
#@License   	:   Mulan PSL v2
#@Desc      	:   test ebs-create-projects
#####################################

source ${OET_PATH}/libs/locallibs/common_lib.sh

# 测试对象、测试需要的工具等安装准备
function pre_test() {
    LOG_INFO "Start to prepare the test environment."
    date_name=$(date +%m%d%H%M%S)
    LOG_INFO "End to prepare the test environment."
}

# 测试点的执行
function run_test() {
    LOG_INFO "Start to run test."

    ccb create projects test-01-${date_name} -j ../data/json/my_spec.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with singgel my_spec failed"
    ccb create projects test-02-${date_name} -j ../data/json/bootstrap_rpm_repo.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with bootstrap_rpm_repo failed"
    ccb create projects test-03-${date_name} -j ../data/json/build_targets.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with build_targets failed"
    ccb create projects test-04-${date_name} -j ../data/json/layer_urls.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with layer_urls failed"
    ccb create projects error_url_project -j ../data/json/my_spec_err_url.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with error_url required failed"
    ccb create projects error_name_type_project -j ../data/json/my_spec_err_name_type.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with error_name_type required failed"
    ccb create projects error_spec_branch_type_project -j ../data/json/error_spec_branch_type.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with error_spec_branch_type required failed"
    ccb create projects error_repo_project -j ../data/json/bootstr_err_repo.json | grep '\"code\": 4065'
    CHECK_RESULT $? 0 0 "project with bootstrap_err_repo required failed"
    ccb create projects bootstr_error_name_type_project -j ../data/json/bootstr_err_name_type.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with bootstrap_err_name_type required failed"
    ccb create projects layer_urls_err_name_project -j ../data/json/layer_urls_err_name_type.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with layer_urls_err_name_type required failed"
    ccb create projects layer_urls_err_url_project -j ../data/json/layer_urls_err_url.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with layer_urls_err_url required failed"
    ccb create projects test-05-${date_name} -j ../data/json/mul_build_targets.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with multiple build_targets failed"
    ccb create projects test-06-${date_name} -j ../data/json/mul_my_specs.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with multiple my_specs failed"
    ccb create projects test-07-${date_name} -j ../data/json/mul_layer_urls.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create projects with mutiple layer_urls failed"

    LOG_INFO "End to run test."
}

# 后置处理，恢复测试环境
function post_test() {
    LOG_INFO "Start to restore the test environment."
    ccb update projects test-01-${date_name} -j ../data/json/del.json
    ccb update projects test-02-${date_name} -j ../data/json/del.json
    ccb update projects test-03-${date_name} -j ../data/json/del.json
    ccb update projects test-04-${date_name} -j ../data/json/del.json
    ccb update projects test-05-${date_name} -j ../data/json/del.json
    ccb update projects test-06-${date_name} -j ../data/json/del.json
    ccb update projects test-07-${date_name} -j ../data/json/del.json
    LOG_INFO "End to restore the test environment."
}

main "$@"
