#!/usr/bin/bash

# Copyright (c) 2020. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   zengcongwei
# @Contact   :   735811396@qq.com
# @Date      :   2020/8/10
# @License   :   Mulan PSL v2
# @Desc      :   public library
# #############################################

ADDR1=$2
ADDR2=$3
PARA=$4
LIST_FILE=$5

RPM_LIST_PATH=$(
    cd "$(dirname "$0")" || exit 1
    pwd
)

while getopts alsrp arg; do
    case $arg in
    a)
        bash $RPM_LIST_PATH/func/rpminfo.sh $PARA $ADDR1 $ADDR2 all 
        ;;
    l)
        bash $RPM_LIST_PATH/func/rpminfo.sh $PARA $ADDR1 $ADDR2 list $LIST_FILE 
        ;;
    s)
        bash $RPM_LIST_PATH/func/rpminfo.sh -s $ADDR1 $ADDR2 single
        ;;
    r)
        ;;
    p)
        ;;
    *)
        exit 1
        ;;
    esac
done
