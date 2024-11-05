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
#@Desc          :   test ccb-select-snapshots
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
    ccb select snapshots os_project=test_for_ysc | grep os_project
    if [$? -eq 0]; then
      ccb select snapshots os_project=test_for_ysc | grep test_for_ysc
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project successful"
      ccb select snapshots os_project=test | grep test
      CHECK_RESULT $? 1 0 "check ccb select snapshots with os_project not exist required failed"
      ccb select snapshots os_project=test_for_ysc --fied snapshot_id | grep snapshot_id
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project --field snapshot_id successful"
      ccb select snapshots os_project=test_for_ysc -f snapshot_id | grep snapshot_id
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f snapshot_id successful"
      ccb select snapshots -f snapshot_id os_project=test_for_ysc | grep snapshot_id
      CHECK_RESULT $? 0 0 "check ccb select snapshots with different order options required successful"
      ccb select snapshots os_project=test_for_ysc -f is_trunk | grep is_trunk
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f is_trunk successful"
      ccb select snapshots os_project=test_for_ysc -f prev_snapshot_id | grep prev_snapshot_id
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f prev_snapshot_id successful"
      ccb select snapshots os_project=test_for_ysc -f create_time | grep create_time
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f create_time successful"
      ccb select snapshots os_project=test_for_ysc -f spec_branch | grep spec_branch
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f spec_branch successful"
      ccb select snapshots os_project=test_for_ysc -f build_targets | grep build_targets
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f build_targets successful"
      ccb select snapshots os_project=test_for_ysc -f ground_projects | grep ground_projects
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f ground_projects successful"
      ccb select snapshots os_project=test_for_ysc -f spec_commits | grep spec_commits
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f spec_commits successful"
      ccb select snapshots os_project=test_for_ysc -f bootstrap_rpm_repo | grep bootstrap_rpm_repo
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f bootstrap_rpm_repo successful"
      ccb select snapshots os_project=test_for_ysc -f submit_user | grep submit_user
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f submit_user successful"
      ccb select snapshots os_project=test_for_ysc -f build_env_macros | grep build_env_macros
      CHECK_RESULT $? 0 0 "check ccb select snapshots with os_project -f build_env_macros successful"
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

