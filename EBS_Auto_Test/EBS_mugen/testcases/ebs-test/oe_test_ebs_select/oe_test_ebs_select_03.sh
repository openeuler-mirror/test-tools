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
#@Desc          :   test ccb-select-builds
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
    ccb select builds os_project=test_for_ysc | grep os_project
    if [$? -eq 0]; then
      ccb select builds os_project=test_for_ysc | grep test_for_ysc
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project successful"
      ccb select builds os_project=test | grep test
      CHECK_RESULT $? 1 0 "check ccb select builds with os_project not exist required failed"
      ccb select builds os_project=test_for_ysc --fied build_id | grep build_id
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project --field build_id successful"
      ccb select builds os_project=test_for_ysc -f build_id | grep build_id
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f build_id successful"
      ccb select builds -f build_id os_project=test_for_ysc | grep build_id
      CHECK_RESULT $? 0 0 "check ccb select builds with different order options required successful"
      ccb select builds os_project=test_for_ysc -f status | grep status
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f status successful"
      ccb select builds os_project=test_for_ysc -f build_type | grep build_type
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f build_type successful"
      ccb select builds os_project=test_for_ysc -f build_target | grep build_target
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f build_target successful"
      ccb select builds os_project=test_for_ysc -f submit_user | grep submit_user
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f submit_user successful"
      ccb select builds os_project=test_for_ysc -f submit_roles | grep submit_roles
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f submit_roles successful"
      ccb select builds os_project=test_for_ysc -f emsx | grep emsx
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f emsx successful"
      ccb select builds os_project=test_for_ysc -f select_pkgs | grep select_pkgs
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f select_pkgs successful"
      ccb select builds os_project=test_for_ysc -f bootstrap_rpm_repo | grep bootstrap_rpm_repo
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f bootstrap_rpm_repo successful"
      ccb select builds os_project=test_for_ysc -f ground_projects | grep ground_projects
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f ground_projects successful"
      ccb select builds os_project=test_for_ysc -f repo_id | grep repo_id
      CHECK_RESULT $? 0 0 "check ccb select builds with os_project -f repo_id successful"
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

