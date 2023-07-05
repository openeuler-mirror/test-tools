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

DATABASE=$1
NUM=$2

SQL_1_LOG=count_1.log
SQL_2_LOG=count_2.log


TBS="call_center catalog_page catalog_returns catalog_sales customer customer_address customer_demographics date_dim household_demographics income_band inventory item promotion reason ship_mode store store_returns store_sales time_dim warehouse web_page web_returns web_sales web_site"

FACTS="store_sales store_returns web_sales web_returns catalog_sales catalog_returns inventory"

# Generate command_prefix according to the deploy_type
deploy_mode=$3

hive_home=$(command -v hive)
beeline_cmd=$(echo ${hive_home%/*}/beeline)
echo "[INFO] beeline path: ${beeline_cmd}"

case ${deploy_mode} in
    tar)
        beeline_command_prefix="${beeline_cmd} -n root -u jdbc:hive2://localhost:10000"
        ;;
    ambari)
        beeline_command_prefix="${beeline_cmd} -n hdfs -p admin"
        ;;
    *)
        echo "[ERROR] unknown deploy mode!"
        exit 1
esac


function runcommand {
  if [ "X$DEBUG_SCRIPT" != "X" ]; then
          $1  >>"${SQL_1_LOG}"
  else
          $1  >>"${SQL_1_LOG}" 2>>"${SQL_2_LOG}"
  fi
}

rm -rf $SQL_1_LOG
rm -rf $SQL_2_LOG

merge_table()
{
  num_merge=$1
  # TBS
  for tb in ${TBS}
  do
    Command="${beeline_command_prefix} -i example/${DATABASE}/testbench_${num_merge}.settings -e 'ALTER TABLE $tb CONCATENATE;' "
    echo "the cmd:" $Command
    echo $Command >> ${SQL_1_LOG}
    ${beeline_command_prefix} -i example/${DATABASE}/testbench_${num_merge}.settings -e "ALTER TABLE ${tb} CONCATENATE;" >>${SQL_1_LOG} 2>>${SQL_2_LOG}
  done
}

analyse_table()
{
    num_analyse=$1
    ${beeline_command_prefix} -i example/${DATABASE}/testbench_${num_analyse}.settings  -f ddl-tpcds/bin_partitioned/analyze.sql 
}


merge_table $NUM
analyse_table $NUM

echo "Merge and Analyse Completed !"
