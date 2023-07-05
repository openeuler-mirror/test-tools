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
tool_root_dir=$(cd "$(dirname "$0")"/../..||exit 1;pwd)
source "${tool_root_dir}/conf/config"

if [ "${platform}" = "HDP" ] ||  [ "${platform}" = "CDH" ] || [ "${platform}" = "APACHE" ]; then
    package_name=${package%-bin*}

else
    echo "Unsupported platform!"
    exit 1;
fi

bash "${hbase_dir}/${package_name}/bin/stop-hbase.sh"
echo "hbase will be stopped!"
