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
#@Desc          :   test ebs-create-projects
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
    ccb -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb -h failed"
    ccb --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb --help failed"
    ccb select -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb select -h failed"
    ccb select --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb select --help failed"
    ccb create -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb create -h failed"
    ccb create --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb create --help failed"
    ccb build-single -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb build-single -h failed"
    ccb build-single --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb build-single --help failed"
    ccb download -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb download -h failed"
    ccb download --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb download --help failed"
    ccb log -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb log -h failed"
    ccb log --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb log --help failed"
    ccb build -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb build -h failed"
    ccb build --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb build --help failed"
    ccb cancel -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb cancel -h failed"
    ccb cancel --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb cancel --help failed"
    ccb ls -h | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb ls -h failed"
    ccb ls --help | grep Usage
    CHECK_RESULT $? 0 0 "Check ccb ls --help failed"
    ccb create projects test-01-${date_name} build_env_macros="unparsable_pkg_repo:\n- prel-libwww-perl\nccache_enable: y" | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with build_env_macros failed"
    ccb create projects test-02-${date_name} spec_branch="openEuler:22.03-LTS" | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with spec_branch failed"
    ccb create projects test-03-${date_name} emsx=ems1 | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create project with emsx failed"
    LOG_INFO "End to run test."
}

# 后置处理，恢复测试环境
function post_test() {
    LOG_INFO "Start to restore the test environment."
    ccb update projects test-01-${date_name} -j ../data/json/del.json
    ccb update projects test-02-${date_name} -j ../data/json/del.json
    ccb update projects test-03-${date_name} -j ../data/json/del.json
    LOG_INFO "End to restore the test environment."
}

main "$@"

