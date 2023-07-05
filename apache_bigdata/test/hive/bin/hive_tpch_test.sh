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
    echo "[Usage] bash ${0##*/} prepare |tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|
    tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|
    tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|
    tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql]"
    exit 1
fi

############################# 运行环境准备 ###############################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
tool_root_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
app_dir=${tool_root_dir}
source "${tool_root_dir}"/conf/tpch_config
source "${tool_root_dir}"/../tools/commonConfig
tpch_dir=${tool_root_dir}/../../testtools/${tpch_file}
setting_dir=${tool_root_dir}/conf/sql/sql_setting
sql_dir=${tool_root_dir}/conf/sql/tpch_sql_file/

# 解析系统类型
case ${deploy_mode} in
    tar)
        command_prefix=${command_prefix_tar_hdfs}
        ;;
    ambari)
        command_prefix=${command_prefix_ambari_hdfs}
        ;;
    *)
        echo "[ERROR] wrong system type, please check ${tool_root_dir}/../tools/commonConfig"
        exit 1
        ;;
esac

hive_home=$(command -v hive)
beeline_cmd=${hive_home%/*}/beeline
echo "[INFO] beeline path: ${beeline_cmd}"

component=hive

install_platform=${deploy_mode}
if [ ${install_platform} == "ambari" ]; then
    bigdata_platform=HDP3.1.0
    test_model_version=hive-3.1.0
else
    bigdata_platform=Apache
    test_model_version=hive-$(hive --version | grep Hive |awk '{print $2}')
fi

case ${inputParameter} in
    tpch_query1.sql)
        testcase="TPC-H Sql1"
        ;;
    tpch_query2.sql)
        testcase="TPC-H Sql2"
        ;;
    tpch_query3.sql)
        testcase="TPC-H Sql3"
        ;;
    tpch_query4.sql)
        testcase="TPC-H Sql4"
        ;;
    tpch_query5.sql)
        testcase="TPC-H Sql5"
        ;;
    tpch_query6.sql)
        testcase="TPC-H Sql6"
        ;;
    tpch_query7.sql)
        testcase="TPC-H Sql7"
        ;;
    tpch_query8.sql)
        testcase="TPC-H Sql8"
        ;;
    tpch_query9.sql)
        testcase="TPC-H Sql9"
        ;;
    tpch_query10.sql)
        testcase="TPC-H Sql10"
        ;;
    tpch_query11.sql)
        testcase="TPC-H Sql11"
        ;;
    tpch_query12.sql)
        testcase="TPC-H Sql12"
        ;;
    tpch_query13.sql)
        testcase="TPC-H Sql13"
        ;;
    tpch_query14.sql)
        testcase="TPC-H Sql14"
        ;;
    tpch_query15.sql)
        testcase="TPC-H Sql15"
        ;;
    tpch_query16.sql)
        testcase="TPC-H Sql16"
        ;;
    tpch_query17.sql)
        testcase="TPC-H Sql17"
        ;;
    tpch_query18.sql)
        testcase="TPC-H Sql18"
        ;;
    tpch_query19.sql)
        testcase="TPC-H Sql19"
        ;;
    tpch_query20.sql)
        testcase="TPC-H Sql20"
        ;;
    tpch_query21.sql)
        testcase="TPC-H Sql21"
        ;;
    tpch_query22.sql)
        testcase="TPC-H Sql22"
        ;;
esac

# 判断日志log路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/log
log_file=${app_dir}/log/hive_tpch.log
log_file_tmp=${app_dir}/log/hive_tpch_tmp.log
echo "" > "${log_file_tmp}"

# 判断输出report路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/report
report_file=${app_dir}/report/hive_tpch.report
tmp_file=${app_dir}/report/hive_tpch_tmp.report

logPath='/tmp/dataCollection/'
source ${logPath}dataCollect.sh

############################# 生成断言标志位 ####################################################
flag_dir=${app_dir}/report/flag.report
echo "" > "${flag_dir}"

#################################### 方法封装 ##################################################
function gen_data
{
  echo "[INFO] Check test data..."
  tpch_dir=${1}
  database_prefix=${2}
  data_size=${3}
  text_output_dir=${4}

  ${command_prefix} echo 'show databases;' > query_database.sql

  case ${deploy_mode} in
    tar)
        beeline_user="${beeline_cmd} -n root -u jdbc:hive2://server1:10000"
        ;;
    ambari)
        chown hdfs:hadoop query_database.sql
        beeline_user="${beeline_cmd} -n hdfs -p admin"
        ;;
    *)
        echo "[ERROR] unknown system type!"
        exit 1
  esac

  # ${beeline_user}不能加双引号,会导致报错,标准化(语法检查)忽略该处
  is_table_existed=$(${command_prefix} ${beeline_user} < query_database.sql 2>/dev/null | grep "${database_prefix}${data_size}" > /dev/null 2>&1; echo $?)

  rm -rf query_database.sql

  # 查看表是否存在，存在则退出，直接开始测试
  if [ "${is_table_existed}" -eq 0 ]; then
    echo "[INFO] Table ${database_prefix}${data_size} has existed!"
    return 0
  fi

  echo "[INFO] Table ${database_prefix}${data_size} miss..."

  if [ ! "${generatedata_switch}" == "true" ]; then
    echo "[INFO] generatedata_switch has been set false, please check config file"
    return 0
  fi

  # 判断TPCH工具是否存在，不存在，直接停止脚本（生成数据+测试）
  if [ ! -d "${tpch_dir}" ]; then
    echo "[ERROR] TPCDS tool doesn't exist, please upload to ${tpch_dir}."
    echo "failed" > "${flag_dir}"
    exit 1
  fi

  # 修改生成数据的配置文件
  if [ ! -f "${tpch_dir}/testbench_${data_size}.settings" ]; then
    echo "[INFO] Configuration file ${tpch_dir}/testbench_${data_size}.settings doesn't exist, start to generate file"
    cp "${tpch_dir}"/testbench_template.settings "${tpch_dir}"/testbench_"${data_size}".settings
  fi
  sed -i "s/template/${data_size}/g" "${tpch_dir}"/testbench_"${data_size}".settings

  # 修改TPC-DS工具目录所有者
  case ${deploy_mode} in
  tar)
      chown -R root:root "${tpch_dir}"
      ;;
  ambari)
      chown -R hdfs:hadoop "${tpch_dir}"
      ;;
  *)
      echo "[ERROR] unknown system type!"
      echo "failed" > "${flag_dir}"
      exit 1
  esac

  # 创建hdfs存放text格式数据的目录并添加可执行权限
  ${command_prefix} hadoop fs -mkdir -p "${text_output_dir}"
  ${command_prefix} hadoop fs -chmod +x "${text_output_dir}"

  # 执行TPC-DS工具脚本，生成对应数据量的测试数据
  echo "[INFO] Start to generate data" | tee -a "${log_file}"
  cd "${tpch_dir}"||exit 1
  echo "[INFO] ${command_prefix} bash genData.sh ${data_size} ${deploy_mode} 2>&1 | tee -a ${log_file}"
  ${command_prefix} bash genData.sh "${data_size}" "${deploy_mode}" 2>&1 | tee -a "${log_file}"
  cd -|| exit 1
}

function execute_query
{
  setting_file=${1}
  sql_file=${2}
  database_name=${3}
  sql_name=${4}

  echo "[INFO] Run ${sql_name}..."

  # 修改配置文件中的数据库名字
  sed -i "s/^use .*/use ${database_name};/g" "${setting_file}"

  # 解析系统类型
  case ${deploy_mode} in
    tar)
        beeline_user="${beeline_cmd} -n root -u jdbc:hive2://server1:10000"
        ;;
    ambari)
        beeline_user="${beeline_cmd} -n hdfs -p admin"
        ;;
    *)
        echo "[ERROR] unknown system type!"
        ;;
  esac

  start_collect -t 'TPC-H' -c 'Hive'
  echo "[WARNING] The execution may fail in an earlier version of the HIVE :sql7 sql9 , could replace substr with column name" | tee -a "${log_file}" "${log_file_tmp}"
  # 执行测试 ${beeline_user}不能加双引号,会导致报错,标准化(语法检查)忽略该处
  ${command_prefix} ${beeline_user} -i "${setting_file}" -f "${sql_file}" 2>&1 | tee -a "${log_file}" "${log_file_tmp}"

  # 结果格式化输出
  if [ $? -eq 0 ]; then
    RESULT=$(tail "${log_file_tmp}" | grep "selected" | awk -F " " '{print $4}' | awk -F "(" '{print $2}')
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${RESULT} =~ ${regular_marchNum} ]] ; then
        echo "failed" > "${flag_dir}"
        exit 1
    fi
    echo "Query time: $(date +"%Y-%m-%d %H:%M:%S")  Query SQL: ${sql_name} succcessfully commplete, Result: ${RESULT} seconds" > "${tmp_file}"
    echo "success" > "${flag_dir}"
  else
    echo "Query time: $(date +"%Y-%m-%d %H:%M:%S")  Query SQL: ${sql_name} execute failed !!!!!!" > "${tmp_file}"
    echo "failed" > "${flag_dir}"
  fi
  cat "${tmp_file}" >> "${report_file}"
  echo -e "\033[31m##############QUERY SQL STATEMENT#####################\033[0m"
  cat  "${sql_file}"
  echo -e "\033[31m######################################################\033[0m"
  echo -e "\033[32m*************QUERY TIME: ${RESULT}seconds******************* \033[0m"
  echo -e "\033[32m###################################################### \033[0m"
  ENDTIME=$(date +"%Y-%m-%d %H:%M:%S")
  echo -e "\033[32m---------------${ENDTIME}----------------\033[0m"
  echo -e "\033[32m###################################################\033[0m"
  data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name performance_data unit -v "${component}" "TPC-DS-Kunpeng" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "${RESULT}" "s(时延)"
  stop_collect

}

################################## 测试执行 #############################################
inputParameter=${1}
case ${inputParameter} in
    prepare) 
        ## 检查测试数据，如果数据不存在，则生成
        gen_data "${tpch_dir}" "${orc_database_prefix}" "${data_size}" "${text_output_dir}"
        ;;
    tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql)
        # 执行测试
        execute_query "${setting_dir}"/"${inputParameter}".sql.setting "${sql_dir}""${inputParameter}" "${orc_database_prefix}""${data_size}" "${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} prepare|sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql|tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql)
"
        exit 1
        ;;
esac
