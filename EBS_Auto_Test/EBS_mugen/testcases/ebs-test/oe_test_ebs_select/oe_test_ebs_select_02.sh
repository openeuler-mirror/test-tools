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
#@Desc          :   test ccb-select-rpms
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
    ccb select projects os_project=test_for_ysc | grep test_for_ysc
    if [$? -eq 0]; then
      ccb select rpms os_project=test_for_ysc | grep test_for_ysc
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project successful"
      ccb select rpms os_project=test | grep test
      CHECK_RESULT $? 1 0 "check ccb select rpms with os_project not exist required failed"
      ccb select rpms os_project=test_for_ysc --fied job_id | grep job_id
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project --field job_id successful"
      ccb select rpms os_project=test_for_ysc -f job_id | grep job_id
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project -f job_id successful"
      ccb select rpms -f job_id os_project=test_for_ysc | grep job_id
      CHECK_RESULT $? 0 0 "check ccb select rpms with different order options required successful"
      ccb select rpms os_project=test_for_ysc -f build_id | grep build_id
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project -f build_id successful"
      ccb select rpms os_project=test_for_ysc -f build_type | grep build_type
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project -f build_type successful"
      ccb select rpms os_project=test_for_ysc -f start_build_time | grep start_build_time
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project -f start_build_time successful"
      ccb select rpms os_project=test_for_ysc -f rpm_path | grep rpm_path
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project -f rpm_path successful"
      ccb select rpms os_project=test_for_ysc -f os_variant | grep os_variant
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project -f os_variant successful"
      ccb select rpms os_project=test_for_ysc -f rpms | grep rpms
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project -f rpms successful"
      ccb select rpms os_project=test_for_ysc -f spec_commit | grep spec_commit
      CHECK_RESULT $? 0 0 "check ccb select rpms with os_project -f spec_commit successful"
      ccb select rpms os_project=test_for_ysc -f spec_commit_time | grep spec_commit_time
      CHECK_RESULT $? 0 0 "check ccb select rpms with spec_commit_time successful"
      ccb select rpms os_project=test_for_ysc -f repo_name | grep repo_name
      CHECK_RESULT $? 0 0 "check ccb select os_project -f repo_name successful"
      ccb select rpms os_project=test_for_ysc -f spec_name | grep spec_name
      CHECK_RESULT $? 0 0 "check ccb select os_project -f spec_name successful"
      ccb select rpms os_project=test_for_ysc -f snapshot_id | grep snapshot_id
      CHECK_RESULT $? 0 0 "check ccb select os_project -f snapshot_id successful"
      ccb select rpms os_project=test_for_ysc -f submit_time | grep submit_time
      CHECK_RESULT $? 0 0 "check ccb select os_project -f submit_time successful"
      ccb select rpms os_project=test_for_ysc -f architecture | grep architecture
      CHECK_RESULT $? 0 0 "check ccb select os_project -f architecture successful"
      ccb select rpms os_project=test_for_ysc -f rpms_detail | grep rpms_detail
      CHECK_RESULT $? 0 0 "check ccb select os_project -f rpms_detail successful"
      ccb select rpms os_project=test_for_ysc -f rpms_build_env | grep rpms_build_env
      CHECK_RESULT $? 0 0 "check ccb select os_project -f rpms_build_env successful"
      ccb select rpms os_project=test_for_ysc -f repo_id | grep repo_id
      CHECK_RESULT $? 0 0 "check ccb select os_project -f repo_id successful"
      ccb select rpms os_project=test_for_ysc -f rpm_repo | grep rpm_repo
      CHECK_RESULT $? 0 0 "check ccb select os_project -f rpm_repo successful"
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
