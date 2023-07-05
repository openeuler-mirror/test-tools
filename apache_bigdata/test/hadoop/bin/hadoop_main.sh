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
if [[ $# -ne 1 ]] || [[ ${1} != "write" ]] && [[ ${1} != "read" ]] && [[ ${1} != "terasort" ]] && [[ ${1} != "wordcount" ]]; then
    echo "Usage: bash ${0##*/} read|write|terasort|wordcount"
    exit 1
fi

###### 测试环境准备 ###########################
app_dir=$(cd "$(dirname "${0}")"/..||exit 1;pwd)
component=hadoop
testcase=$1
dfsio_report_file_tmp=${app_dir}/report/hadoop_dfsio_tmp.report
terasort_report_file_tmp=${app_dir}/report/hadoop_terasort_tmp.report
wordcount_report_file_tmp=${app_dir}/report/hadoop_wordcount_tmp.report

inputParameter=${1}

########### STEP 1 ############################
# 性能数据采集shell脚本
logPath='/tmp/dataCollection/'
source ${logPath}dataCollect.sh


########### STEP 2-1 prepare ##################
case ${inputParameter} in
    terasort)
        bash "${app_dir}"/bin/hadoop_terasort.sh prepare
        ;;
    wordcount)
        bash "${app_dir}"/bin/hadoop_wordcount.sh prepare
        ;;
    read|write)
        echo "[INFO] scape prepare!"
        ;;
    *)  echo "[Usage] bash ${0##*/} read|write|terasort|wordcount"
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
data_collect --nmon -f 5 -c 60 -- --local -p ${component} -s "${testcase}" --


########### STEP 2-3 testing ##################
case ${inputParameter} in
    read|write)
        bash "${app_dir}"/bin/hadoop_dfsio.sh "${inputParameter}"
        ;;
    terasort)
        bash "${app_dir}"/bin/hadoop_terasort.sh "${inputParameter}"
        ;;
    wordcount)
        bash "${app_dir}"/bin/hadoop_wordcount.sh "${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} read|write|terasort|wordcount"
        exit 1
        ;;
esac


########### STEP 3 ##################
case ${inputParameter} in
    read|write)
        if [ ! -f "${dfsio_report_file_tmp}" ]; then
            echo "[ERROR] ${dfsio_report_file_tmp} miss..."
        else
            result_throughput=$(cat < "${dfsio_report_file_tmp}" | grep "Throughput" | awk '{print $10}' | sed -n '1p')
            data_record -k throughput -v "${result_throughput}"
        fi
        ;;
    terasort)
        if [ ! -f "${terasort_report_file_tmp}" ]; then
            echo "[ERROR] ${terasort_report_file_tmp} miss..."
        else
            result_throughput=$(cat < "${terasort_report_file_tmp}" | grep "Throughput" | awk '{print $14}' | sed -n '1p')
            data_record -k throughput -v "${result_throughput}"
        fi
        ;;
    wordcount)
        if [ ! -f "${wordcount_report_file_tmp}" ]; then
            echo "[ERROR] ${wordcount_report_file_tmp} miss..."
        else
            result_throughput=$(cat < "${wordcount_report_file_tmp}" | grep "Throughput" | awk '{print $14}' | sed -n '1p')
            data_record -k throughput -v "${result_throughput}"
        fi
        ;;
    *)  echo "[Usage] bash ${0##*/} read|write|terasort|wordcount"
        exit 1
        ;;
esac


# 性能数据采集停止
data_collect stop

