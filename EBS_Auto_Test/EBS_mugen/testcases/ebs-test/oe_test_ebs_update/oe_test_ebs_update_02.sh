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
    ccb update projects test-00-${date_name} -j ../data/json/update_bootstrap_rpm_repo_add.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with bootstrap_rpm_repo_add successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_bootstrap_rpm_repo_del.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with bootstrap_rpm_repo_del successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_bootstrap_rpm_repo.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with bootstrap_rpm_repo successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_bootstrap_rpm_repo_err.json | grep '\"code\": 4065'
    CHECK_RESULT $? 0 0 "check ccb update projects with bootstrap_rpm_repo_err required failed"
    ccb update projects test-00-${date_name} -j ../data/json/update_package_repo_add.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with package_repos_add successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_package_repo_del.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with package_repos_del successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_package_repo.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with package_repos successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_package_repo_err.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "check ccb update projects with package_repos_err required failed"
    ccb update projects test-00-${date_name} -j ../data/json/update_emsx.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with update_emsx successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_spec_branch.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with update_spec_branch successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_build_targets_add.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with update_build_targets_add successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_build_targets_del.json| grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with update_build_targets_del successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_build_targets.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "check ccb update projects with update_build_targets successful"
    ccb update projects test-00-${date_name} -j ../data/json/update_build_targets_err_os.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "check ccb update projects with update_build_targets_err_os_variant required failed"
    ccb update projects test-00-${date_name} -j ../data/json/update_build_targets_err_arch.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "check ccb update projects with update_build_targets_err_arch required failed"
    ccb update projects test-00-${date_name} -j ../data/json/update_build_targets_err_flag.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "check ccb update projects with update_build_targets_err_flag required failed"
    LOG_INFO "End to run test."
}

# 后置处理，恢复测试环境
function post_test() {
    LOG_INFO "Start to restore the test environment."
    ccb update projects test-00-${date_name} -j ../data/json/del.json
    LOG_INFO "End to restore the test environment."
}

main "$@"

