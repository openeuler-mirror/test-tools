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
if [[ $# -ne 1 ]] || [[ ${1} != "terasort" ]] && [[ ${1} != "prepare" ]]; then
    echo "[Usage] bash ${0##*/} [terasort|prepare]"
    exit
fi

############################# 运行环境准备 ####################################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
app_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
source "${app_dir}"/conf/terasort_config
source "${app_dir}"/../tools/commonConfig

# 判断日志log路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/log
log_file=${app_dir}/log/hadoop_terasort.log

# 判断输出report路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/report
report_file=${app_dir}/report/hadoop_terasort.report
report_file_tmp=${app_dir}/report/hadoop_terasort_tmp.report

case ${deploy_mode} in
    tar)
        test_user=${command_user_tar}
        ;;
    ambari)
        test_user=${command_user_ambari}
        ;;
    *)
        echo "[ERROR] wrong system type, please check ${app_dir}/../tools/commonConfig"
        echo "failed" > "${flag_dir}"
        exit 1
        ;;
esac

############################# 生成断言标志位 ####################################################
flag_dir=${app_dir}/report/flag.report
prepare_log=${app_dir}/log/prepare.log
log_file_tmp=${app_dir}/log/hadoop_terasort_tmp.log
echo "" > "${log_file_tmp}"
echo "" > "${flag_dir}"

#################################### 方法封装 ##################################################
function get_final_status()
{
    app_id=$1
    final_status=$(curl http://localhost:8088/cluster/app/"${app_id}" 2>/dev/null | grep -A 3 "FinalStatus" | grep SUCCEEDE | sed "s/\ //g")
    echo "${final_status}"
}

function get_elapsed_time()
{
    app_id=$1
    read -r -a elapsed_time <<< "$(curl http://localhost:8088/cluster/app/"${app_id}" 2>/dev/null | grep -A 4 Elapsed | grep sec | sed "s/\ //g" | tr -d "a-zA-Z" | tr ',' ' ')"
    # elapsed_time=$(curl http://localhost:8088/cluster/app/"${app_id}" 2>/dev/null | grep -A 4 Elapsed | grep sec | sed "s/\ //g" | tr -d "a-zA-Z" | tr ',' ' ')
    cost_time=0
    for num in "${elapsed_time[@]}"
    do
        ((cost_time="${cost_time}"*60+"${num}"))
    done
    echo "${cost_time}"
}

function prepare_test(){
    # 删除terasort结果目录
    echo "[INFO] Delete old terasort output file" | tee -a "${log_file}"
    ${test_user} hadoop fs -rm -r "${terasort_output_data}" > /dev/null 2>&1

    # 如果hdfs指定目录没有测试数据，则生成
    echo "[INFO] checkout terasort input data..."
    echo "[INFO] ${test_user} hadoop fs -ls ${terasort_input_data}"
    hdfs_file_existed=$(${test_user} hadoop fs -ls "${terasort_input_data}" > /dev/null 2>&1; echo $?)
    if [ $((hdfs_file_existed)) -ne 0 ]; then
        echo "[INFO] hdfs path: ${terasort_input_data} doesn't exist" | tee -a "${log_file}"
        echo "[INFO] generate test data ..." | tee -a "${log_file}"
        echo "[INFO] ${test_user} hadoop jar ${jar_file} teragen -Dmapred.map.tasks=${map_tasks} ${data_size} terasort/${data_size}-input"
        # ${jar_file} 不能加引号，checkstyle忽略
        ${test_user} hadoop jar ${jar_file} teragen -Dmapred.map.tasks="${map_tasks}" "${data_size}" terasort/"${data_size}"-input 2>&1 | tee "${prepare_log}"
        application_id=$(cat < "${prepare_log}" | grep "Submitted application" | awk '{print $NF}' | tail -n 1)
        final_status=$(get_final_status "${application_id}")
        if [ "${final_status}" != "SUCCEEDED" ] ; then
            echo "failed" > "${flag_dir}"
        exit 1
        fi
        echo "[INFO] generate test data OK" | tee -a "${log_file}"
    else
        echo "[INFO] check OK!" | tee -a "${log_file}"
    fi
}

function execute_test(){
    # 执行terasort，并记录耗时
    echo "[INFO] Start to execute terasort" | tee -a "${log_file}"
    # start_time=`date +%s%N`
    # ${jar_file} 不能加引号，checkstyle忽略
    ${test_user} hadoop jar ${jar_file} terasort -Dmapred.reduce.tasks="${reduce_tasks}" "${terasort_input_data}" "${terasort_output_data}" 2>&1 | tee -a "${log_file}" "${log_file_tmp}"
    # end_time=`date +%s%N`
    # duration=$(((${end_time}-${start_time})/1000000000))
    application_id=$(cat < "${log_file_tmp}" | grep "Submitted application" | awk '{print $NF}' | tail -n 1)
    duration=$(get_elapsed_time "${application_id}")
    final_status=$(get_final_status "${application_id}")
    if [ "${final_status}" != "SUCCEEDED" ] ; then
        echo "failed" > "${flag_dir}"
        exit 1
    fi
    throuput=$(echo "scale=2;${data_size}*100/1024/1024/${duration}" | bc)
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${throuput} =~ ${regular_marchNum} ]] ; then
        echo "$(date) DataSize ${data_size}*100 byte, RunTime ${duration} sec, test failed!" > "${report_file_tmp}"
        echo "failed" > "${flag_dir}"
        exit 1
    else
        echo "$(date) DataSize ${data_size}*100 byte, RunTime ${duration} sec, Throughput ${throuput} MB/sec" > "${report_file_tmp}"
        echo "success" > "${flag_dir}"
    fi
    cat < "${report_file_tmp}" | tee -a "${report_file}"
}

#################################### 测试执行 ##################################################
inputParameter=${1}

case ${inputParameter} in
    prepare)
        prepare_test
        ;;
    terasort)
        execute_test
        ;;
    *)
        echo "[Usage] bash ${0##*/} [terasort|prepare]"
        exit 1
        ;;
esac
