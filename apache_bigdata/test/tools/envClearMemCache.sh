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
############################# 参数数量合法性检查 ##########################################
if [[ $# -ne 1 ]]; then
    echo "[Usage]: bash ${0##*/} server1,agent1,agent2,agent3 | ipArry"
    echo "[EXAMPLE]: bash ${0##*/} 127.0.0.1"
    exit 1
fi

tools_dir=$(cd "$(dirname "$0")" || exit 1;pwd)

source "${tools_dir}"/remoteTools.sh
passwd=Huawei12#$

ipStr=$1
read -r -a ipArry <<< "${ipStr//,/ }"
echo "[INFO] 测试环境清缓存。。。"

for ip in "${ipArry[@]}"
do
echo "[INFO] clear ${ip} mem cache"
run_remote_show_log "echo 3 > /proc/sys/vm/drop_caches" "${ip}" ${passwd}
done
