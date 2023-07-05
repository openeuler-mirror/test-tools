#! /usr/bin
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
OPEN_JDK_NAME=$1

if [[ $# -ne 1 ]]; then
    echo -e "\033[1;4;5;31m[Usage1] bash ${0##*/} 请传入jdk文件参数 | agent1,agent2,agent3  \033[0m"
    exit 1

fi

ipStr="agent1,agent2,agent3"
read -r -a ipArry <<< "${ipStr//,/ }"
echo "[INFO] 需要执行的节点信息！！"

for ip in "${ipArry[@]}"
do
echo "[INFO] $ip"
scp  jdk_download.sh  ${ip}:/root
ssh $ip "bash jdk_download.sh ${OPEN_JDK_NAME};source /etc/profile || exit 1"
done
