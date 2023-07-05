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
    echo "[Usage] bash ${0##*/} prepare | sql1.sql | sql2.sql | sql3.sql | sql4.sql | sql5.sql | sql6.sql | sql7.sql | sql8.sql | sql9.sql | sql10.sql"
    exit 1
fi

############################# 运行环境准备 ###############################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
tool_root_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
app_dir=${tool_root_dir}
source "${tool_root_dir}"/conf/config
source "${tool_root_dir}"/../tools/commonConfig
tpcds_dir=${tool_root_dir}/../../testtools/${tpcds_file}
setting_dir=${tool_root_dir}/conf/sql/sql_setting
sql_dir=${tool_root_dir}/conf/sql/tpcds_sql_file/

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

logPath='/tmp/dataCollection/'
#source ${logPath}dataCollect.sh

hive_home=$(command -v hive)
beeline_cmd=${hive_home%/*}/beeline
echo "[INFO] beeline path: ${beeline_cmd}"

# 判断日志log路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/log
log_file=${app_dir}/log/hive_tpcds.log
log_file_tmp=${app_dir}/log/hive_tpcds_tmp.log
echo "" > "${log_file_tmp}"

# 判断输出report路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/report
report_file=${app_dir}/report/hive_tpcds_log.report
tmp_file=${app_dir}/report/hive_tpcds_new.report

############################# 生成断言标志位 ####################################################
flag_dir=${app_dir}/report/flag.report
echo "" > "${flag_dir}"

#################################### 方法封装 ##################################################
function gen_data
{
  echo "[INFO] Check test data..."
  tpcds_dir=${1}
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
   # return 0
  fi

  echo "[INFO] Table ${database_prefix}${data_size} miss..."

  if [ ! "${generatedata_switch}" == "true" ]; then
    echo "[INFO] generatedata_switch has been set false, please check config file"
    return 0
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
  ${command_prefix} hadoop fs -mkdir -p "${text_output_dir}"
  ${command_prefix} hadoop fs -chmod +x "${text_output_dir}"

  # 执行TPC-DS工具脚本，生成对应数据量的测试数据
  echo "[INFO] Start to generate data" | tee -a "${log_file}"
  cd "${tpcds_dir}"||exit 1
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
  
  start_collect -t 'TPC-DS' -c 'Hive'
  echo "[WARNING] The execution may fail in an earlier version of the HIVE :sql7 sql9 , could replace substr with column name" | tee -a "${log_file}" "${log_file_tmp}"
  # 执行测试 ${beeline_user}不能加双引号,会导致报错,标准化(语法检查)忽略该处
  ${command_prefix} ${beeline_user} -i "${setting_file}" -f "${sql_file}" 2>&1 | tee -a "${log_file}" "${log_file_tmp}"

  # 结果格式化输出
  if [ $? -eq 0 ]; then
    RESULT=$(cat "${log_file_tmp}" | grep "selected" |tail -n 1 | awk -F " " '{print $4}' | awk -F "(" '{print $2}')
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
        gen_data "${tpcds_dir}" "${orc_database_prefix}" "${data_size}" "${text_output_dir}"
        ;;
    sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql)  
        # 执行测试
        execute_query "${setting_dir}"/"${inputParameter}"_hive.setting "${sql_dir}""${inputParameter}" "${orc_database_prefix}""${data_size}" "${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} prepare | sql1.sql | sql2.sql | sql3.sql | sql4.sql | sql5.sql | sql6.sql | sql7.sql | sql8.sql | sql9.sql | sql10.sql"
        exit 1
        ;;
esac
