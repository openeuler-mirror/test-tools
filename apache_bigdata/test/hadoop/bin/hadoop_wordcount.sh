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
if [[ $# -ne 1 ]] || [[ ${1} != "wordcount" ]] && [[ ${1} != "prepare" ]]; then
    echo "[Usage] bash ${0##*/} [wordcount|prepare]"
    exit
fi


############################# 运行环境准备 ####################################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
app_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
source "${app_dir}"/conf/wordcount_config
source "${app_dir}"/../tools/commonConfig

# 判断日志log路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/log
log_file=${app_dir}/log/hadoop_wordcount.log

# 判断输出report路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/report
report_file=${app_dir}/report/hadoop_wordcount.report
report_file_tmp=${app_dir}/report/hadoop_wordcount_tmp.report

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
log_file_tpm=${app_dir}/log/hadoop_wordcount_tem.log
echo "" > "${log_file_tpm}"
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
    # elapsed_time=$(curl http://localhost:8088/cluster/app/${app_id} 2>/dev/null | grep -A 4 Elapsed | grep sec | sed "s/\ //g" | tr -d "a-zA-Z" | tr ',' ' ')
    cost_time=0
    for num in "${elapsed_time[@]}"
    do
        ((cost_time="${cost_time}"*60+"${num}"))
    done
    echo "${cost_time}"
}


function prepare_test(){
    # 删除wordcount结果目录
    echo "[INFO] Delete old wordcount output dir" | tee -a "${log_file}"
    ${test_user} hadoop fs -rm -r "${data_hdfs_output_dir}" > /dev/null 2>&1

    # 如果hdfs指定目录没有测试文件，则上传
    echo "[INFO] checkout wordcount input data..."
    echo "[INFO] hadoop fs -ls ${data_hdfs_input_dir}/${data_local_file##*/}"
    hdfs_file_existed=$(hadoop fs -ls "${data_hdfs_input_dir}"/"${data_local_file##*/}" > /dev/null 2>&1; echo $?)
    if [ $((hdfs_file_existed)) -ne 0 ]; then
        echo "[INFO] hdfs path: ${data_hdfs_input_dir}/${data_local_file##*/} doesn't exist" | tee -a "${log_file}"
        echo "[INFO] upload test data ..." | tee -a "${log_file}"
        echo "[INFO] ${test_user} hadoop fs -put ${app_dir}/${data_local_file} ${data_hdfs_input_dir}"
        ${test_user} hadoop fs -mkdir -p "${data_hdfs_input_dir}"
        ${test_user} hadoop fs -put "${app_dir}"/"${data_local_file}" "${data_hdfs_input_dir}"
        echo "[INFO] upload test data OK" | tee -a "${log_file}"
    else
        echo "[INFO] check OK!" | tee -a "${log_file}"
    fi
}


function execute_test(){
    echo "[INFO] checkout wordcount input data..."
    echo "[INFO] hadoop fs -ls ${data_hdfs_input_dir}/${data_local_file##*/}"
    hdfs_file_existed=$(hadoop fs -ls "${data_hdfs_input_dir}"/"${data_local_file##*/}" > /dev/null 2>&1; echo $?)
    if [ $((hdfs_file_existed)) -ne 0 ]; then
        echo "[ERROR] check failed!" | tee -a "${log_file}"
        echo "failed" > "${flag_dir}"
        exit 1
    else
        echo "[INFO] check OK!" | tee -a "${log_file}"
    fi

    # 获取测试数据量，单位Byte
    data_size=$(${test_user} hadoop fs -ls "${data_hdfs_input_dir}"/"${data_local_file##*/}" | grep "${data_local_file##*/}" | awk -F" " '{print $5}')
    echo "[INFO] test data size ${data_size} Byte" | tee -a "${log_file}"
    # 执行wordcount，并记录耗时
    echo "[INFO] Start to execute wordcount" | tee -a "${log_file}"
    # start_time=`date +%s%N`
    ${test_user} hadoop jar ${jar_file} wordcount "${data_hdfs_input_dir}" "${data_hdfs_output_dir}" 2>&1 | tee -a "${log_file}" "${log_file_tpm}"
    # end_time=`date +%s%N`
    # duration=$(((${end_time}-${start_time})/1000000000))
    application_id=$(cat < "${log_file_tpm}" | grep "Submitted application" | awk '{print $NF}' | tail -n 1)
    duration=$(get_elapsed_time "${application_id}")
    final_status=$(get_final_status "${application_id}")
    if [ "${final_status}" != "SUCCEEDED" ] ; then
        echo "failed" > "${flag_dir}"
        exit 1
    fi
    throuput=$(echo "scale=2;${data_size}/1024/1024/${duration}" | bc)
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${throuput} =~ ${regular_marchNum} ]] ; then
        echo "$(date) DataSize ${data_size}*100 byte, RunTime ${duration} sec, test failed!" > "${report_file_tmp}"
        echo "failed" > "${flag_dir}"
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
    wordcount)
        execute_test
        ;;
    *)
        echo "[Usage] bash ${0##*/} [wordcount|prepare]"
        exit 1
        ;;
esac
