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

############################# 参数数量合法性检查 ##############################################
if [[ $# -ne 1 ]] || [[ ${1} != "prepare" ]] && [[ ${1} != "sql1.sql" ]] && [[ ${1} != "sql2.sql" ]] && [[ ${1} != "sql3.sql" ]] && [[ ${1} != "sql4.sql" ]] && [[ ${1} != "sql5.sql" ]] && [[ ${1} != "sql6.sql" ]] && [[ ${1} != "sql7.sql" ]] && [[ ${1} != "sql8.sql" ]] && [[ ${1} != "sql9.sql" ]] && [[ ${1} != "sql10.sql" ]]; then
    echo "[Usage] bash ${0##*/} [prepare|sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql]"
    exit 1
fi

############################# 运行环境准备 ####################################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
app_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
source "${app_dir}"/conf/tpcds_config
tpcds_dir=${app_dir}/../../testtools/${tpcds_file}
spark_conf_file=${app_dir}/conf/${spark_conf_file}
setting_dir=${app_dir}/conf/setting/
sql_dir=${app_dir}/conf/sql/tpcds_sql_file/
source "${app_dir}"/../tools/commonConfig

############################# 生成断言标志位 ####################################################
flag_dir=${app_dir}/report/flag.report
echo "" > "${flag_dir}"

############################# 修改配置文件 ####################################################
case ${deploy_mode} in
    tar)
        command_prefix_hdfs=$command_prefix_tar_hdfs
        ;;
    ambari)
        command_prefix_hdfs=$command_prefix_ambari_hdfs
        ;;
    *)
        echo "[ERROR] wrong system type, please check ${app_dir}/../tools/commonConfig"
        echo "failed" > "${flag_dir}"
        exit 1
        ;;
esac

# 判断日志log路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/log
log_file=${app_dir}/log/spark_tpcds.log
log_file_tmp=${app_dir}/log/spark_tpcds_tmp.log
echo "" > "${log_file_tmp}"

# 判断输出report路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/report
report_file=${app_dir}/report/spark_tpcds.report
report_file_tmp=${app_dir}/report/spark_tpcds_tmp.report

component=spark
logPath='/tmp/dataCollection/'
#source ${logPath}dataCollect.sh
if [ "${install_platform}" == "ambari" ]; then
    bigdata_platform=HDP3.1.0
    test_model_version=spark-2.3.2
else
    bigdata_platform=Apache
    test_model_version=spark-$(cat /usr/local/spark/RELEASE | awk 'NR==1''{print$2}')
fi

case ${inputParameter} in
    sql1.sql)
        testcase="TPC-DS Sql1"
        ;;
    sql2.sql)
        testcase="TPC-DS Sql2"
        ;;
    sql3.sql)
        testcase="TPC-DS Sql3"
        ;;
    sql4.sql)
        testcase="TPC-DS Sql4"
        ;;
    sql5.sql)
        testcase="TPC-DS Sql5"
        ;;
    sql6.sql)
        testcase="TPC-DS Sql6"
        ;;
    sql7.sql)
        testcase="TPC-DS Sql7"
        ;;
    sql8.sql)
        testcase="TPC-DS Sql8"
        ;;
    sql9.sql)
        testcase="TPC-DS Sql9"
        ;;
    sql10.sql)
        testcase="TPC-DS Sql10"
        ;;
esac

#################################### 方法封装 ##################################################
function gen_data
{
  echo "[INFO] Check test data..."
  tpcds_dir=${1}
  database_prefix=${2}
  data_size=${3}
  text_output_dir=${4}

  ${command_prefix_hdfs} echo 'show databases;' > query_database.sql
#  chown hdfs:hadoop query_database.sql
  if [ "${deploy_mode}" = ambari ]; then
     chown hdfs:hadoop query_database.sql
  fi

  echo "[INFO] ${command_prefix_hdfs} spark-sql -f query_database.sql 2>/dev/null | grep "^${database_prefix}${data_size}$" > /dev/null 2>&1"
  is_table_existed=$(${command_prefix_hdfs} spark-sql -f query_database.sql 2>/dev/null | grep "^${database_prefix}${data_size}$" > /dev/null 2>&1; echo $?)
  rm -rf query_database.sql
  echo $is_table_existed
  # 查看表是否存在，存在则退出，直接开始测试
  if [ "${is_table_existed}" -eq 0 ]; then
    echo "Table ${database_prefix}${data_size} has existed!"
 #   return 0
  fi

  # 判断TPCDS工具是否存在，不存在，直接停止脚本（生成数据+测试）
  if [ ! -d "${tpcds_dir}" ]; then
    echo "[ERROR] TPCDS tool doesn't exist, please upload to ${tpcds_dir}."
    echo "failed" > "${flag_dir}"
    exit 1
  fi

  # 修改生成数据的配置文件
  if [ ! -f "${tpcds_dir}/testbench_${data_size}.settings" ]; then
    echo "[INFO] Configuration file ${tpcds_dir}/testbench_${data_size}.settings doesn't exist, start to generate file"
    cp "${tpcds_dir}"/testbench_template.settings "${tpcds_dir}"/testbench_"${data_size}".settings
  fi
  sed -i "s/template/${data_size}/g" "${tpcds_dir}"/testbench_"${data_size}".settings

  # 修改TPC-DS工具目录所有者
  case ${deploy_mode} in
  tar)
      chown -R root:root "${tpcds_dir}"
      ;;
  ambari)
      chown -R hdfs:hadoop "${tpcds_dir}"
      ;;
  *)
      echo "[ERROR] unknown system type!"
      echo "failed" > "${flag_dir}"
      exit 1
  esac


  # 创建hdfs存放text格式数据的目录并添加可执行权限
  ${command_prefix_hdfs} hadoop fs -mkdir -p "${text_output_dir}"
  ${command_prefix_hdfs} hadoop fs -chmod +x "${text_output_dir}"

  # 执行TPC-DS工具脚本，生成对应数据量的测试数据
  echo "[INFO] Start to generate data" 2>&1 | tee -a "${log_file}"
  cd "${tpcds_dir}"|| exit 1
  echo "[INFO] ${command_prefix_hdfs} bash tpcds-setup-spark.sh ${data_size} parquet ${spark_client_dir}/bin jdbc:hive2://127.0.0.1:10016/ 2>&1 | tee -a ${log_file}"
  ${command_prefix_hdfs} bash tpcds-setup-spark.sh "${data_size}" parquet "${spark_client_dir}"/bin jdbc:hive2://127.0.0.1:10016/ 2>&1 | tee -a "${log_file}"
  cd -|| exit 1
}

function execute_query
{
  setting_file=${1}
  sql_file=${2}
  database_name=${3}
  sql_name=${4}

  echo "[INFO] Run ${sql_name}..."

  # 读取当前sql语句对应的spark重要参数
  source "${setting_file}"

  # 执行测试
  start_collect -t 'TPC-DS' -c 'Spark'
  echo "[INFO] ${command_prefix_hdfs} spark-sql --master yarn --driver-memory ${driver_memory} --executor-memory ${executor_memory} --num-executors ${num_executors} --executor-cores ${executor_cores} --properties-file ${spark_conf_file} --database ${database_name} -f ${sql_file}"
  ${command_prefix_hdfs} spark-sql --master yarn --driver-memory "${driver_memory}" --executor-memory "${executor_memory}" --num-executors "${num_executors}" --executor-cores "${executor_cores}" --properties-file "${spark_conf_file}" --database "${database_name}" -f "${sql_file}" 2>&1 |tee -a "${log_file}" "${log_file_tmp}"

  # 结果格式化输出
  RESULT=$(cat "${log_file_tmp}" | grep "^Time taken:"|tail -n 1 | awk -F "Time taken: " '{print $2}'| awk -F " " '{print $1}')
  regular_marchNum='^[0-9]+([.][0-9]+)?$'
  if ! [[ ${RESULT} =~ ${regular_marchNum} ]] ; then
      echo "Query time: $(date +"%Y-%m-%d %H:%M:%S")  Query SQL: ${sql_name} execute failed !!!!!!" > "${report_file_tmp}"
      echo "failed" > "${flag_dir}"
  else
      echo "Query time: $(date +"%Y-%m-%d %H:%M:%S")  Query SQL: ${sql_name} succcessfully commplete, Result: ${RESULT} seconds" > "${report_file_tmp}"
      echo "success" > "${flag_dir}"
  fi
  cat < "${report_file_tmp}" | tee -a "${report_file}"
  echo -e "\033[31m##############QUERY SQL STATEMENT#####################\033[0m"
  cat  "${sql_file}"
  echo -e "\033[31m######################################################\033[0m"
  echo -e "\033[32m*************QUERY TIME: ${RESULT} seconds******************* \033[0m"
  echo -e "\033[32m###################################################### \033[0m"
  ENDTIME=$(date +"%Y-%m-%d %H:%M:%S")
  echo -e "\033[32m---------------$ENDTIME----------------\033[0m"
  echo -e "\033[32m###################################################\033[0m"
  data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name performance_data unit -v "${component}" "TPC-DS-Kunpeng" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "${RESULT}" "s(时延)"

}


################################## 配置解析 #############################################
inputParameter=${1}



################################## 测试执行 ################################################
case ${inputParameter} in
    prepare)
        gen_data "${tpcds_dir}" "${parquet_database_prefix}" "${data_size}" "${text_output_dir}"
        ;;
    sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql)
        execute_query "${setting_dir}"/"${inputParameter}".setting "${sql_dir}""${inputParameter}" "${parquet_database_prefix}${data_size}" "${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} prepare|sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql"
        echo "failed" > "${flag_dir}"
        exit 1
        ;;
esac
