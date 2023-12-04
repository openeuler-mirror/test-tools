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
#@Desc          :   test ccb-select-jobs
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
    ccb select jobs os_project=test_for_ysc | grep os_project
    if [$? -eq 0]; then
      ccb select jobs os_project=test_for_ysc | grep test_for_ysc
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project successful"
      ccb select jobs os_project=test | grep test
      CHECK_RESULT $? 1 0 "check ccb select jobs with os_project not exist required failed"
      ccb select jobs os_project=test_for_ysc --fied build_id | grep build_id
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project --field build_id successful"
      ccb select jobs os_project=test_for_ysc -f build_id | grep build_id
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f build_id successful"
      ccb select jobs os_project=test_for_ysc -f category | grep category
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f category successful"
      ccb select jobs os_project=test_for_ysc -f package | grep package
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f package successful"
      ccb select jobs os_project=test_for_ysc -f textbox | grep textbox
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f textbox successful"
      ccb select jobs os_project=test_for_ysc -f spec_file_name | grep spec_file_name
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f spec_file_name successful"
      ccb select jobs os_project=test_for_ysc -f my_account | grep my_account
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f my_account successful"
      ccb select jobs os_project=test_for_ysc -f snapshot_id | grep snapshot_id
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f snapshot_id successful"
      ccb select jobs os_project=test_for_ysc -f build_type | grep build_type
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f build_type successful"
      ccb select jobs os_project=test_for_ysc -f os_arch | grep os_arch
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f os_arch successful"
      ccb select jobs os_project=test_for_ysc -f os_version | grep os_version
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f os_version successful"
      ccb select jobs os_project=test_for_ysc -f snapshot_create_time | grep snapshot_create_time
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f snapshot_create_time successful"
      ccb select jobs os_project=test_for_ysc -f spec_branch | grep spec_branch
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f spec_branch successful"
      ccb select jobs os_project=test_for_ysc -f submit_id | grep submit_id
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f submit_id successful"
      ccb select jobs os_project=test_for_ysc -f submit_id | grep submit_id
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f submit_id successful"
      ccb select jobs os_project=test_for_ysc -f submit_date | grep submit_date
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f submit_date successful"
      ccb select jobs os_project=test_for_ysc -f memory | grep memory
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f memory successful"
      ccb select jobs os_project=test_for_ysc -f nr_cpu | grep nr_cpu
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f nr_cpu successful"
      ccb select jobs os_project=test_for_ysc -f ccache_clear | grep ccache_clear
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f ccache_clear successful"
      ccb select jobs os_project=test_for_ysc -f ccache_enable | grep ccache_enable
      CHECK_RESULT $? 0 0 "check ccb select jobs with os_project -f ccache_enable successful"
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
