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
#@Desc          :   test ccb-select-rpm_repos
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
    ccb select rpm_repos os_project=test_for_ysc | grep os_project
    if [$? -eq 0]; then
      ccb select rpm_repos os_project=test_for_ysc | grep test_for_ysc
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project successful"
      ccb select rpm_repos os_project=test | grep test
      CHECK_RESULT $? 1 0 "check ccb select rpm_repos with os_project not exist required failed"
      ccb select rpm_repos os_project=test_for_ysc --fied repo_id | grep repo_id
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project --field repo_id successful"
      ccb select rpm_repos os_project=test_for_ysc -f repo_id | grep repo_id
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f repo_id successful"
      ccb select rpm_repos -f repo_id os_project=test_for_ysc | grep repo_id
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with different order options required successful"
      ccb select rpm_repos os_project=test_for_ysc -f repo_es_key_id | grep repo_es_key_id
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f repo_es_key_id successful"
      ccb select rpm_repos os_project=test_for_ysc -f os_variant | grep os_variant
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f os_variant successful"
      ccb select rpm_repos os_project=test_for_ysc -f snapshot_id | grep snapshot_id
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f snapshot_id successful"
      ccb select rpm_repos os_project=test_for_ysc -f architecture | grep architecture
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f architecture successful"
      ccb select rpm_repos os_project=test_for_ysc -f create_time | grep create_time
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f create_time successful"
      ccb select rpm_repos os_project=test_for_ysc -f rpm_repo_path | grep rpm_repo_path
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f rpm_repo_path successful"
      ccb select rpm_repos os_project=test_for_ysc -f rpm_count | grep rpm_count
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f rpm_count successful"
      ccb select rpm_repos os_project=test_for_ysc -f rpm_depends | grep rpm_depends
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f rpm_depends successful"
      ccb select rpm_repos os_project=test_for_ysc -f last_repo_id | grep last_repo_id
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f last_repo_id successful"
      ccb select rpm_repos os_project=test_for_ysc -f last_repo_es_key_ids | grep last_repo_es_key_ids
      CHECK_RESULT $? 0 0 "check ccb select rpm_repos with os_project -f last_repo_es_key_ids successful"
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
