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
tool_root_dir=$(cd "$(dirname "$0")"/../.. || exit 1;pwd)
source "${tool_root_dir}"/conf/config

if [ "${is_tezui_installed}" == "true" ]; then
    echo -e "\033[42;30m ====================Stop tez-ui==================== \033[0m"
    # 停止tomcat
    "${tomcat_dir}"/tomcat/bin/shutdown.sh
    
    # 停止timeline server
    yarn-daemon.sh stop timelineserver
fi
