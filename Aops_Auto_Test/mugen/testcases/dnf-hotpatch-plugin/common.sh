#!/usr/bin/bash

# Copyright (c) 2022. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   Classicriver_jia
# @Contact   :   classicriver_jia@foxmail.com
# @Date      :   2020-04-10
# @License   :   Mulan PSL v2
# @Desc      :   Enable periodic block discard
# ############################################
source ${OET_PATH}/libs/locallibs/common_lib.sh
function get_cve_and_patch () {
        cve=$(dnf hot-updateinfo list cve | grep patch | awk '{print $1}')
        cve_list=($cve)
	patch=$(dnf hot-updateinfo list cve | grep patch | awk '{print $4}')
        patch_list=($patch)

}

