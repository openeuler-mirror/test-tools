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
file_path=$1
password=$2

tool_root_dir=$(cd $(dirname "$0")/../..||exit 1;pwd)
source ${tool_root_dir}/conf/config
ips=$master,${spark_client}
node_list=($(echo ${ips[*]}| sed 's/,/\n/g'| sort | uniq))
num=0
for agent in ${node_list[@]}
do
if [ $num == 0 ]
then
# ssh_agent为更新过文件的节点
ssh_agent=$agent
else
ssh $ssh_agent "expect <<EOF
set timeout 100
spawn scp -r ${file_path} root@${agent}:${file_path}
expect {
          \"yes/no\" { send \"yes\r\";exp_continue }
          \"password\" { send \"${password}\r\";exp_continue }
        }
EOF"
fi
((num++))
done 
