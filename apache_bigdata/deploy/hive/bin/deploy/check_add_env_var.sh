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

# Ìí¼Óµ½»·¾³±äÁ¿

if ! cat < "/etc/profile" | grep "^export HIVE_HOME=/usr/local/hive";then
    echo "export HIVE_HOME=/usr/local/hive" >> /etc/profile
fi

if ! cat < "/etc/profile" | grep "^export PATH=\${HIVE_HOME}/bin:\${PATH}";then
    echo "export PATH=\${HIVE_HOME}/bin:\${PATH}" >> /etc/profile
fi
