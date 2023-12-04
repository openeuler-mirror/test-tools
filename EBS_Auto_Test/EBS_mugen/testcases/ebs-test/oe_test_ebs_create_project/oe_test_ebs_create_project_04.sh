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

    ccb create projects test-01-${date_name} -j ../data/json/mul_bootstr_repo.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with multiple bootstrap_rpm_repo failed"
    ccb create projects test-02-${date_name} -j ../data/json/add_ground_projects.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with ground_projects failed"
    ccb create projects test-03-${date_name} -j ../data/json/no_flag.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with no flag failed"
    ccb create projects err_os_variant_project -j ../data/json/build_target_err_os_variant.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with build_target_err_os_variant required failed"
    ccb create projects build_target_err_arch_project -j ../data/json/build_target_err_arch.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with build_target_err_arch failed"
    ccb create projects build_target_err_ground_project -j ../data/json/build_target_err_ground.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "project with build_target_err_ground failed"
    ccb create projects flags_err_build_project -j ../data/json/flags_err_build.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "projects with flags_err_build failed"
    ccb create projects flags_err_publish_project -j ../data/json/flags_err_publish.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "projects with flags_err_publish_project failed"

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
