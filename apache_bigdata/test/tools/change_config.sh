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
tools_config_dir=$(cd "$(dirname "$0")"||exit 1;pwd)
hive_config_dir=$(cd "$(dirname "$0")/../hive/conf"||exit 1;pwd)
type=$(lscpu | grep Architecture | awk '{print $2}')
if [ "${type}" == "x86_64" ];then
sed -i "s/^arch.*/arch=x86/g" "${tools_config_dir}/envConfig"
sed -i "s/^tpcds_package.*/tpcds_package=TPC-DS-x86_64.tar.gz/g" "${tools_config_dir}/envConfig"
sed -i "s/^tpcds_extract_dir.*/tpcds_extract_dir=TPC-DS-x86_64/g" "${tools_config_dir}/envConfig"
sed -i "s/^tpcds_file.*/tpcds_file=TPC-DS-x86_64/g" "${hive_config_dir}/config"
else
sed -i "s/^arch.*/arch=arm/g" "${tools_config_dir}/envConfig"
sed -i "s/^tpcds_package.*/tpcds_package=TPC-DS-Kunpeng.tar.gz/g" "${tools_config_dir}/envConfig"
sed -i "s/^tpcds_extract_dir.*/tpcds_extract_dir=TPC-DS-Kunpeng/g" "${tools_config_dir}/envConfig"
sed -i "s/^tpcds_file.*/tpcds_file=TPC-DS-Kunpeng/g" "${hive_config_dir}/config"
fi

if [ ! -d "/root/auto_deploy" ];then
sed -i "s/^hibench_package.*/hibench_package=HiBench-HiBench-7.0.tar.gz/g" "${tools_config_dir}/envConfig"
else
sed -i "s/^hibench_package.*/hibench_package=HiBench-HiBench-7.0_apache.tar.gz/g" "${tools_config_dir}/envConfig"
fi

echo "" > ${tools_config_dir}/../hbase/conf/destCsvFileListConf
read -r -a data_list <<< $(lsblk -f | grep /data | awk '{print $NF}' | xargs)
for i in ${data_list[@]}
do
echo ${i}/bulkload${i#*/data/data}.csv >> "${tools_config_dir}/../hbase/conf/destCsvFileListConf"
done
