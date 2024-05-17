#!/usr/bin/bash

# Copyright (c) 2021. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
#@Author    	:   lemon.higgins
#@Contact   	:   lemon.higgins@aliyun.com
#@Date      	:   2020-04-09 09:39:43
#@License   	:   Mulan PSL v2
#@Desc      	:   Take the test ls command as an example
#####################################

source ${OET_PATH}/libs/locallibs/common_lib.sh

function pre_test() {
    LOG_INFO "Start to prepare the test environment."

    DNF_INSTALL "aops-ceres"


    LOG_INFO "End to prepare the test environment."
}

function run_test() {
    LOG_INFO "Start to run test."
    aops-ceres register -f non-exist.json 2>&1 | grep "No such file or directory: 'non-exist.json'"
    CHECK_RESULT $? 0 0 "Test register host with non-exist file failed"
    aops-ceres register -f 2>&1 | grep "error: argument -f/--path: expected one argument"
    CHECK_RESULT $? 0 0 "Test register -f without parameter failed"
    aops-ceres register -f /opt/aops/register_example.json | grep "Register Success"
    CHECK_RESULT $? 0 0 "Test register valid host failed"
    aops-ceres register -f /opt/aops/register_example.json 2>&1 | grep '{"code":"1105","label":"Data.Exist","message":"data has existed"}'
    CHECK_RESULT $? 0 0 "Test register host multiple times failed"
    aops-ceres register -d '{"ssh_user": "root","password": "openEuler12#$","zeus_ip": "172.168.71.131","zeus_port": 11111,"host_name": "host1","host_group_name": "register_group","management": false,"ssh_port":22,"access_token":"token-string"}' 2>&1 | grep '{"code":"1000","label":"Param.Error","message":"request parameter error"}'
    CHECK_RESULT $? 0 0 "Test register host with invalid parameter failed"
    aops-ceres register -d 2>&1 | grep "argument -d/--data: expected one argument"
    CHECK_RESULT $? 0 0 "Test register -f  without parameter failed"
    aops-ceres register 2>&1 | grep "one of the arguments -f/--path -d/--data is required"
    CHECK_RESULT $? 0 0 "Test register without parameter failed"
    LOG_INFO "End to run test."
}

function post_test() {
    LOG_INFO "Start to restore the test environment."

    DNF_REMOVE

    LOG_INFO "End to restore the test environment."
}

main "$@"
