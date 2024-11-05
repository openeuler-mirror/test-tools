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
    ccb create projects test-01-${date_name} --json ../data/json/project-all-params.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "--json create project failed"
    ccb create projects test-02-${date_name} -j ../data/json/project-all-params.json | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "--j create project failed"
    ccb create projects test-03-${date_name} --yaml ../data/yaml/project-all-params.yaml | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "--yaml create project failed"
    ccb create projects test-04-${date_name} -y ../data/yaml/project-all-params.yaml | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "-y create project failed"
    ccb create projects test-05-${date_name} description=ysc_test05
    ccb select projects | grep ysc_test05
    CHECK_RESULT $? 0 0 "key-value parameter pass failed"
    ccb create projects test-06-${date_name} description=ysc_test06 --json ../data/json/project-all-params.json
    ccb select projects | grep ysc_test06
    CHECK_RESULT $? 0 0 "kv json create project failed"
    ccb create projects test-07-${date_name} description=ysc_test07 --yaml ../data/yaml/project-all-params.yaml
    ccb select projects | grep ysc_test07
    CHECK_RESULT $? 0 0 "kv yaml create project failed"
    ccb create projects description=ysc_test08
    CHECK_RESULT $? 1 0 "project required failed"
    ccb create projects test-01-${date_name} | grep "already exists"
    CHECK_RESULT $? 0 0 "create existed project failed "
    ccb create projects ${date_name} | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create short name project failed"
    ccb create projects 12345123451234512${date_name} | grep '\"code\": 0'
    CHECK_RESULT $? 0 0 "create long name project failed"
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
    ccb update projects ${date_name} -j ../data/json/del.json
    ccb update projects 12345123451234512${date_name} -j ../data/json/del.json
    LOG_INFO "End to restore the test environment."
}

main "$@"

