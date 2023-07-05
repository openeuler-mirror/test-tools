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
source "${tool_root_dir}"/conf/config
source "${tool_root_dir}"/bin/common/remote.sh

echo "you will uninstall hive,please input 'yes' to confirm"
read -r yes

if [ "${yes}" = yes ];then
    # 先停止集群                              
    bash "${tool_root_dir}"/bin/switch/stop.sh
    echo "Hive will be uninstalled"

    # 删除mysql数据库中的hive数据库
    mysql -u"${db_user}" -p"${db_pswd}" -e "drop database hive;"

    # 删除hive相关的目录
    rm -rf "${hive_dir}"/hive 
    rm -rf "${hive_dir}"/"${package%.tar*}"
    hadoop fs -rm -r /tmp
    hadoop fs -rm -r /user/hive/warehouse

    # 恢复mysql配置文件
    \cp /etc/my.cnf_origin_backup /etc/my.cnf
    \cp /etc/my.cnf.d/mysql-clients.cnf_origin_backup /etc/my.cnf.d/mysql-clients.cnf
    if [[ "${os}" != openEuler* ]]; then
        \cp /etc/my.cnf.d/client.cnf_origin_backup /etc/my.cnf.d/client.cnf
    fi
fi
