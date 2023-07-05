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
    echo "[Usage] bash ${0##*/} sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql|Wordcount|Terasort|Bayes|Kmeans|tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql"
    exit 1
fi

###### 测试环境准备 ###########################
app_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
# component=spark
# tpcds_tmp_log=${app_dir}/report/spark_tpcds_tmp.report
# tpch_tmp_log=${app_dir}/report/spark_tpch_tmp.report
# hibench_tmp_log=${app_dir}/report/spark_hibench_tmp.report
inputParameter=${1}

source  ${app_dir}/../tools/commonConfig
# logPath='/tmp/dataCollection/'
# source ${logPath}dataCollect.sh

########### STEP 1 ############################
# 性能数据采集shell脚本
# logPath='/tmp/dataCollection/'
# source ${logPath}dataCollect.sh

########### STEP 2-1 prepare ##################
case ${inputParameter} in
    sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql)
        bash "${app_dir}"/bin/spark_tpcds.sh prepare
        ;;
    tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql)
        bash "${app_dir}"/bin/spark_tpch.sh prepare
        ;;
    Wordcount|Terasort|Bayes|Kmeans)
        bash "${app_dir}"/bin/spark_hibench.sh prepare_"${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql|Wordcount|Terasort|Bayes|Kmeans"
        exit 1
        ;;
esac

########### STEP 2-2 datacollect on ###########
# 判断上一条命令是否执行成功
if [ $? -ne 0 ]; then
    echo "[ERROR] prepare failed"
    exit 1
fi
# 基础性能数据采集开启
# data_collect --nmon -f 5 -c 60 -- --perf -n AmbariServer -s 5 -d 10 -T 0 --
# data_collect --nmon -f 5 -c 60 -- --local -p ${component} -s "${testcase}" --

########### STEP 2-3 testing ##################
case ${inputParameter} in
    sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql)
        bash "${app_dir}"/bin/spark_tpcds.sh "${inputParameter}"
        ;;
    tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql)
        bash "${app_dir}"/bin/spark_tpch.sh "${inputParameter}"
        ;;
    Wordcount|Terasort|Bayes|Kmeans)
        bash "${app_dir}"/bin/spark_hibench.sh "${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql|Wordcount|Terasort|Bayes|Kmeans"
        exit 1
        ;;
esac

########### STEP 3 ##################
# case ${inputParameter} in
#     sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql)
#        if [ ! -f "${tpcds_tmp_log}" ]; then
#            echo "[ERROR] ${tpcds_tmp_log} miss..."
#        else
#            result_costtime=$(cat < "${tpcds_tmp_log}" | grep "Result" | awk '{print $11}' | sed -n '1p')
#            data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name metrics performance_data unit -v "${component}" "TPC-DS-Kunpeng" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "耗时" "${result_costtime}" "s(时延)"
#         fi
#         ;;
#     tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql)
#         if [ ! -f "${tpch_tmp_log}" ]; then
#             echo "[ERROR] ${tpch_tmp_log} miss..."
#         else
#              result_costtime=$(cat < "${tpch_tmp_log}" | grep "Result" | awk '{print $11}' | sed -n '1p')
            # data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name performance_data unit -v "${component}" "TPC-H-Kunpeng" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "${result_costtime}" "s(时延)"
#         fi
#       ;;
#     Wordcount|Terasort|Bayes|Kmeans)
#         if [ ! -f "${hibench_tmp_log}" ]; then
#             echo "[ERROR] ${hibench_tmp_log} miss..."
#         else
#             result_throughput=$(cat < "${hibench_tmp_log}" | grep "throughput" | awk '{print $5}' | sed -n '1p')
            # data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name metrics performance_data unit -v "${component}" "HiBench-HiBench-7.0" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "吞吐量" "${result_throughput}" "GB\/min\/node(吞吐量)"
#         fi
#         ;;
#     *)  echo "[Usage] bash ${0##*/} sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql|Wordcount|Terasort|Bayes|Kmeans"
#         exit 1
#         ;;
# esac

########### STEP 4 ##################
# 性能数据采集停止
# data_collect stop
