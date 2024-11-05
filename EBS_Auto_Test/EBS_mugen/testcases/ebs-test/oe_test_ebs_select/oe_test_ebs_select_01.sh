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
#@Desc          :   test ebs-select-projects
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
    ccb select projects os_project=test-00-${date_name} | grep test-00-${date_name}
    CHECK_RESULT $? 0 0 "ccb select projects os_project=value successful"
    ccb select projects os_project=test-${date_name} | grep test-${date_name}
    CHECK_RESULT $? 1 0 "ccb select not exist project required failed"
    ccb select projects owner=ysc | grep owner
    CHECK_RESULT $? 0 0 "ccb select projects owner=value successful"
    ccb select projects owner=test-${date_name} | grep owner
    CHECK_RESULT $? 1 0 "ccb select projects with not exist owner required failed"
    ccb select projects lock=false | grep lock
    CHECK_RESULT $? 0 0 "ccb select projects lock=value successful"
    ccb select projects lock=test-${date_name} | grep lock
    CHECK_RESULT $? 1 0 "ccb select projects lock with invalid value required failed"
    ccb select projects spec_branch=master | grep spec_branch
    CHECK_RESULT $? 0 0 "ccb select projects spec_branch=value successful"
    ccb select projects spec_branch=test-${date_name} | grep spec_branch
    CHECK_RESULT $? 1 0 "ccb select projects spec_branch with not exist value required failed"
    ccb select projects os_project=test-00-${date_name} --field owner | grep owner
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project --field owner successful"
    ccb select projects os_project=test-00-${date_name} -f owner | grep owner
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project -f owner successful"
    ccb select projects -f owner os_project=test-00-${date_name} | grep owner
    CHECK_RESULT $? 0 0 "check ccb select projects with different order options required successful"
    ccb select projects os_project=test-${date_name} -f test-${date_name} | grep test-${date_name}
    CHECK_RESULT $? 1 0 "check ccb select projects with not exist field required failed"
    ccb select projects os_project=test-00-${date_name} -f inherited_from | grep inherited_from
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project -f inherited_from successful"
    ccb select projects os_project=test-00-${date_name} -f bootstrap_rpm_repo | grep bootstrap_rpm_repo
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project -f bootstrap_rpm_repo successful"
    ccb select projects os_project=test-00-${date_name} -f to_delete | grep to_delete
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project -f to_delete successful"
    ccb select projects os_project=test-00-${date_name} -f users | grep users
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project -f users successful"
    ccb select projects os_project=test-00-${date_name} -f create_time | grep create_time
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project -f create_time successful"
    ccb select projects os_project=test-00-${date_name} -f build_env_macros | grep build_env_macros
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project -f build_env_macros successful"
    ccb select projects os_project=test-00-${date_name} -f spec_branch | grep spec_branch
    CHECK_RESULT $? 0 0 "check ccb select projects with os_project -f build_env_macros successful"
    ccb select projects os_project=test-00-${date_name} -f spec_name | grep spec_name
    CHECK_RESULT $? 1 0 "check ccb select projects with os_project -f spec_name required failed"
    LOG_INFO "End to run test."
}

# 后置处理，恢复测试环境
function post_test() {
    LOG_INFO "Start to restore the test environment."
    ccb update projects test-00-${date_name} -j ../data/json/del.json
    LOG_INFO "End to restore the test environment."
}

main "$@"
