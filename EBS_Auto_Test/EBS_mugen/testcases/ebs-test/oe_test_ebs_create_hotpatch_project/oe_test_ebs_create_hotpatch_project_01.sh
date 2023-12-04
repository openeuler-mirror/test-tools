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
    ccb create projects hotpatch-01-${date_name} -j  ../data/json/hotpatch_config.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create hotpatch projects failed"
    ccb create projects hotpatch_no_branch -j  ../data/json/config_by_no_branch.json | grep '\"code\": 4057'
    CHECK_RESULT $? 0 0 "create hotpatch projects with no spec branch required failed"
    ccb create projects hotpatch_no_patch -j ../data/json/config_by_no_patch.json | grep '\"code\": 4010'
    CHECK_RESULT $? 0 0 "create hotpatch projects with no hotpatch config required failed"
    ccb create projects hotpatch_no_pkg_repo -j ../data/json/config_no_pkg_repo.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "create hotpatch projects with no package_repo required failed" | grep '\"code\": 500'
    ccb create projects hotpatch_no_his_job_id -j ../data/json/config_no_pr_id.json | grep '\"code\": 4010'
    CHECK_RESULT $? 0 0 "create hotpatch projects with no history jobs required failed"
    ccb create projects hotpatch_err_spec_name -j ../data/json/config_err_spec_name.json | grep '\"code\": 4064'
    CHECK_RESULT $? 0 0 "create hotpatch projects with error spec name required failed"
    ccb create projects hotpatch_err_spec_name -j ../data/json/config_err_spec_url.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "create hotpatch projects with error spec url required failed"
    ccb create projects hotpatch_err_type -j ../data/json/config_err_type.json | grep '\"code\": 500'
    CHECK_RESULT $? 0 0 "create hotpatch projects with error project_type required failed"

    LOG_INFO "End to run test."
}

# 后置处理，恢复测试环境
function post_test() {

    LOG_INFO "Start to restore the test environment."
    ccb update projects hotpatch-01-${date_name} -j ../data/json/del.json
    LOG_INFO "End to restore the test environment."
}

main "$@"
