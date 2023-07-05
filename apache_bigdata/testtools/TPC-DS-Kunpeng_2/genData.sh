#!/bin/bash
# Copyright (c) 2023. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   hekeming
# @Contact   :   hk16897@126.com
# @Date      :   2023/07/03
# @License   :   Mulan PSL v2
# @Desc      :   Test SSH link
# ############################################

num=$1
deploy_mode=$2

##################################参数合法性校验################################################
if [[ $# -ne 2 ]] || [[ ${deploy_mode} != "tar" ]] && [[ ${deploy_mode} != "ambari" ]]  ; then
        echo "[Usage] bash ${0##*/} [tar|ambari]"
        exit 1
fi

bash ./tpcds-setup-hive.sh $num orc $deploy_mode

\cp -fr testbench_${num}.settings example/tpcds_orc_hive_${num}/

bash ./tpcds-count-hive.sh tpcds_orc_hive_$num $num $deploy_mode

