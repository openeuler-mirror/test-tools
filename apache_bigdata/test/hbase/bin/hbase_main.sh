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
# 性能采集参数

############################# 参数数量合法性检查 ##########################################
if [[ $# -ne 1 ]]; then
    echo "Usage: bash ${0##*/} randomWrite|randomRead|scanRange100|bulkload"
    exit 1
fi

###### 测试环境准备 ###########################
app_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
component=hbase
# pe_tmp_log=${app_dir}/report/hbase_pe_tmp.report
# bl_tmp_log=${app_dir}/report/hbase_bulkload_tmp.report
inputParameter=${1}

source  ${app_dir}/../tools/commonConfig
# install_platform=${deploy_mode}
# tools_v=PE
# if [ ${install_platform} == "ambari" ]; then
#     bigdata_platform=HDP3.1.0
#     test_model_version=hbase-2.0.2
# else
#    bigdata_platform=Apache
#    test_model_version=hbase-$(cat /usr/local/hbase/NOTICE.txt  | grep Gson | head -1 | awk '{print $2}'| sed 's/.$//')
# fi


########### STEP 1 ############################
# 性能数据采集shell脚本
# logPath='/tmp/dataCollection/'
# source ${logPath}dataCollect.sh

########### STEP 2-1 prepare ##################
case ${inputParameter} in
    randomWrite) 
        ;;
    randomRead|scanRange100) 
        bash "${app_dir}"/bin/hbase_pe.sh prepare
        ;;
    bulkload)
        bash "${app_dir}"/bin/hbase_bulkload.sh prepare
        ;; 
    *)  echo "[Usage] bash ${0##*/} randomWrite|randomRead|scanRange100|bulkload"
        exit 1
        ;;
esac

########### STEP 2-2 datacollect on ###########
# 判断上一条命令是否执行成功
if [ $? -ne 0 ]; then
    echo "[ERROR] prepare failed"
    exit 1
fi

source "${app_dir}"/../tools/envConfig
echo "[INFO] clean Mem Cache for this cluster: ${clusterip}"
bash "${app_dir}"/../tools/envClearMemCache.sh "${clusterip}"

# 基础性能数据采集开启
# data_collect --nmon -f 5 -c 60 -- --perf -n AmbariServer -s 5 -d 10 -T 0 --
data_collect --nmon -f 5 -c 60 -- --local -p ${component} -s "${testcase}" --

########### STEP 2-3 testing ##################
case ${inputParameter} in
    randomWrite|randomRead|scanRange100)
        bash "${app_dir}"/bin/hbase_pe.sh "${inputParameter}"
        ;;
    bulkload)
        bash "${app_dir}"/bin/hbase_bulkload.sh "${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} randomWrite|randomRead|scanRange100|bulkload"
        exit 1
        ;;
esac

########### STEP 3 ##################
# case ${inputParameter} in
#     randomWrite|randomRead)
#         if [ ! -f "${pe_tmp_log}" ]; then
#            echo "[ERROR] ${pe_tmp_log} miss..."
#         else
#             result_throughput=$(cat < "${pe_tmp_log}" | grep "Throughput" | awk '{print $20}' | sed -n '1p')
#            data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name metrics performance_data unit -v "${component}" "${tools_v}" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "吞吐量" "${result_throughput}" "ops\/node\/s(吞吐量)"
#         fi
#         ;;
#     scanRange100)
#         if [ ! -f "${pe_tmp_log}" ]; then
#             echo "[ERROR] ${pe_tmp_log} miss..."
#         else
#             result_throughput=$(cat < "${pe_tmp_log}" | grep "Throughput" | awk '{print $(NF)}')
#             echo  result_throughput $result_throughput
#             data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name metrics performance_data unit -v "${component}" "${tools_v}" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "吞吐量" "${result_throughput}" "ops\/node\/s(吞吐量)"
#         fi
#         ;;
#     bulkload)
#         if [ ! -f "${bl_tmp_log}" ]; then
#             echo "[ERROR] ${bl_tmp_log} miss..."
#         else
#             result_throughput=$(cat < "${bl_tmp_log}" | grep "Throughput" | awk '{print $19}' | sed -n '1p')
#             data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name metrics performance_data unit -v  "${component}" "${tools_v}" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "吞吐量" "${result_throughput}" "MB\/Node\/s(吞吐量)"
#         fi
#         ;;
#     *)  echo "[Usage] bash ${0##*/} randomWrite|randomRead|scanRange100|bulkload"
#         exit 1
#         ;;
# esac

# 性能数据采集停止
# data_collect stop
