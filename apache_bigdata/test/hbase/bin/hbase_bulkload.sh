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

################################ 参数数量合法性检查 ###########################################
if [[ $# -ne 1 ]] || [[ ${1} != "prepare" ]] && [[ ${1} != "bulkload" ]]; then
    echo "Usage: bash ${0##*/} prepare|bulkload"
    exit 1
fi

################################## 运行环境准备 ###############################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
app_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
source "${app_dir}"/conf/bulkload_config
bulkload_conf=${app_dir}/conf/bulkload_config
hbaseshell_file=${app_dir}/bin/${hbase_cmd_file}
source "${app_dir}"/../tools/commonConfig

############################# 生成断言标志位 ####################################################
flag_dir=${app_dir}/report/flag.report
echo "" > "${flag_dir}"

############################# 修改配置文件 ####################################################
case ${deploy_mode} in
    tar)
        command_prefix_hdfs=${command_prefix_tar_hdfs}
        command_prefix_hbase=${command_prefix_tar_hbase}
        ;;
    ambari)
        command_prefix_hdfs=${command_prefix_ambari_hdfs}
        command_prefix_hbase=${command_prefix_ambari_hbase}
        ;;
    *)
        echo "[ERROR] wrong system type, please check ${app_dir}/../tools/commonConfig"
        echo "failed" > "${flag_dir}"
        exit 1
        ;;
esac

# 日志log路径，如果不存在则先创建
mkdir -p "${app_dir}/log"
log_file=${app_dir}/log/hbase_bulkload.log

# 输出report路径，如果不存在则先创建
mkdir -p "${app_dir}/report"
report_file=${app_dir}/report/hbase_bulkload.report
report_tmp=${app_dir}/report/hbase_bulkload_tmp.report

logPath='/tmp/dataCollection/'
#source ${logPath}dataCollect.sh
testcase=BulkLoad
tools_v=PE
component=hbase
if [ "${install_platform}" == "ambari" ]; then
    bigdata_platform=HDP3.1.0
    test_model_version=hbase-2.0.2
else
    bigdata_platform=Apache
    test_model_version=hbase-$(cat /usr/local/hbase/NOTICE.txt  | grep Gson | head -1 | awk '{print $2}'| sed 's/.$//')
fi

#################################### 方法封装 #################################################
gendata_command="python2 ${app_dir}/conf/bulkload/put1024.py"
csvconffile=${app_dir}/conf/destCsvFileListConf
csvlist=$(grep -v "^#" "${csvconffile}" | sed '/^\s*$/d')
csvpara=""

for para in ${csvlist}
do
    csvpara="${csvpara} ${para}"
done

totalsizeByte=0
csvcomplete="true"
csvdatafit="false"

function check_is_existed()
{
    if [ ! -f "$1" ]; then
        echo "[ERROR] ${1} not exist,please check ${csvconffile}"
        return 1
    else
        echo "[INFO] ${1} exist"
        return 0
    fi
}

function bulkload_mount()
{
total_num=$(cat "${app_dir}/conf/bulkload_disk"|grep '^/dev'|wc -l)
per_size=$(echo ${total_num} ${bulkloaddatasize}|awk '{printf "%.0f", $2/1024/1024/$1 + 1}')
for disk_info in  $(cat "${app_dir}/conf/bulkload_disk"|grep '^/dev')
do
    disk=$(echo ${disk_info}|awk -F '=' '{print $1}')
    mount_dir=$(echo ${disk_info}|awk -F '=' '{print $2}')

    disk_size=$(lsblk -l ${disk}|tail -n 1|awk '{print $4}')
    unit=$(echo ${disk_size}|grep -Eo '[a-zA-Z]+')
    size=$(echo ${disk_size}|grep -Eo '[0-9]+([.][0-9]+)?')
    if [[ "${unit}" == "G" ]]
    then
       disk_G_size=${size}
    elif [[ "${unit}" == "T" ]]
    then
       disk_G_size=$(echo ${size}|awk '{print $1*1024 }')
    else
       echo unit ${unit} is not support!!!
       exit 1
    fi
    flag=$(python3 -c "print(${per_size} < ${disk_G_size})")
    if [[ "${flag}" == "True" ]]
    then
        mkdir -p ${mount_dir}
        mount ${disk} ${mount_dir}
    else
        echo ${disk} size less than  ${per_size}G !!!!
        exit
    fi

done


}


function generate_csv_data()
{
    # 检查csv文件是否存在
    for csvdata in ${csvlist}
    do
        if ! check_is_existed "${csvdata}"; then
            csvcomplete="false"
        fi
    done

    # 如果csv存在且齐全，计算csv总大小单位:Byte
    if [ ${csvcomplete} == "true" ]; then
        csvdatasizelist=$(ls -l ${csvpara} |awk '{print $5}' )
        for num in ${csvdatasizelist}
        do
            ((totalsizeByte=totalsizeByte+"${num}"))
        done

        ((totalsizeKb=totalsizeByte/1024))
        if [ "${totalsizeKb}" -eq "${bulkloaddatasize}" ]; then
            echo "[INFO] check ok, csv data total size: ${totalsizeKb} KB"
            csvdatafit="true"
            return 0
        else
            csvdatafit="false"
            echo "[INFO] check failed, csv data total size: ${totalsizeKb} KB"
        fi
    fi
    
    bulkload_mount
    
    # 生成测试数据
    echo "[INFO] start generating csv data ..."
    gendata_command="${gendata_command} 1 ${bulkloaddatasize}"
    for para in ${csvlist}
    do
        gendata_command="${gendata_command} ${para}"
    done
    echo "[DEBUG] ${gendata_command}"
    if ${gendata_command};
    then
        csvdatafit="true"
        echo "[INFO] regenerate csv data finished"
        ls -l ${csvpara}
        return 0
    else
        csvdatafit="false"
        echo "[ERROR] regenerate csv data failed"
        return 1
    fi
}


function copy_csv_data_to_hadoopfs()
{
    if [ "${csvdatafit}" == "true" ]; then
        echo "[INFO] start copy csv data to hadoop fs"
        echo "[INFO] cat ${csvpara} | hdfs dfs -appendToFile /dev/fd/0 ${data_hdfs_file}"
        if cat ${csvpara} | hdfs dfs -appendToFile /dev/fd/0 "${data_hdfs_file}";
        then
            echo "[INFO] copy csv data to hadoop fs finished"
            return 0
        else
            echo "[ERROR] copy csv data to hadoop fs failed"
            return 1
        fi
    else
        echo "[INFO] csv regenerate data flag is false, don't generate csv data"
        return 1
    fi
}


function check_testdata()
{
    # 如果hdfs指定目录没有测试文件，则上传
    hdfs_file_existed=$(${command_prefix_hdfs} hadoop fs -ls "${data_hdfs_file}" > /dev/null 2>&1; echo $?)
    if [ $((hdfs_file_existed)) -ne 0 ]; then
        echo "[ERROR] hdfs path: ${data_hdfs_file} doesn't exist, please create it." | tee -a "${log_file}"
        echo "failed" > "${flag_dir}"
        exit 1
    else
        echo "[INFO] check ok, test data exist."
    fi
}


function prepare_testdata()
{
    # 如果hdfs指定目录没有测试文件，则上传
    hdfs_file_existed=$(${command_prefix_hdfs} hadoop fs -ls "${data_hdfs_file}" > /dev/null 2>&1; echo $?)
    if [ $((hdfs_file_existed)) -ne 0 ]; then
        echo "[INFO] hdfs path: ${data_hdfs_file} doesn't exist, upload test data to hdfs." | tee -a "${log_file}"
        data_hdfs_dir=${data_hdfs_file%/*}
        ${command_prefix_hdfs} hadoop fs -mkdir -p "${data_hdfs_dir}" | tee -a "${log_file}"
        # 避免用户无权限写目录的情况
        ${command_prefix_hdfs} hadoop fs -chmod -R 777 "${data_hdfs_dir}" | tee -a "${log_file}"
        if generate_csv_data; then
                if copy_csv_data_to_hadoopfs; then
                    echo "[INFO] prepare csv data OK"
                 else
                    echo "[ERROR] prepare csv data failed"
                    echo "failed" > "${flag_dir}"
                    exit 1
                fi
            else
                echo "[ERROR] prepare csv data failed"
                echo "failed" > "${flag_dir}"
                exit 1
            fi
    else
        if [ "true" == "${csvdataregenerateflag}" ]; then
            if generate_csv_data; then
                if copy_csv_data_to_hadoopfs; then
                    echo "[INFO] prepare csv data OK"
                 else
                    echo "[ERROR] prepare csv data failed"
                    echo "failed" > "${flag_dir}"
                    exit 1
                fi
            else
                echo "[ERROR] prepare csv data failed"
                echo "failed" > "${flag_dir}"
                exit 1
            fi
        else
            echo "[INFO] force regenerate csv data flag is <false>, don't generate csv data!"
        fi
        echo "[INFO] check ok, hadoop fs test data ${data_hdfs_file} exist."

    fi
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


function get_final_status()
{
    app_id=$1
    final_status=$(curl http://localhost:8088/cluster/app/"${app_id}" 2>/dev/null | grep -A 3 "FinalStatus" | grep SUCCEEDE | sed "s/\ //g")
    echo "${final_status}"
}


function bulkload_test()
{
    # check_testdata
    prepare_testdata
    # 准备工作：1)删除bulkload结果目录 ; 2) 建表
    echo "[INFO] Create table & delete old bulkload dir" | tee -a "${log_file}"
    ${command_prefix_hdfs} hadoop fs -rm -r "${bulk_output}" | tee -a "${log_file}"
    ${command_prefix_hbase} hbase shell "${hbaseshell_file}" | tee -a "${log_file}"

    # 获取测试数据量，单位Byte
    data_size=$(${command_prefix_hdfs} hadoop fs -ls "${data_hdfs_file}" | grep "${data_hdfs_file##*/}" | awk -F" " '{print $5}')
    # 执行Bulkload，并记录耗时
    start_collect -t 'PE' -c 'HBase'
    echo "[INFO] Start to execute bulkload" | tee -a "${log_file}"
    ${command_prefix_hdfs} hbase org.apache.hadoop.hbase.mapreduce.ImportTsv -Dimporttsv.columns=HBASE_ROW_KEY,f1:H_NAME,f1:ADDRESS -Dimporttsv.separator="," -Dimporttsv.skip.bad.lines=true -Dmapreduce.split.minsize="${mapreduce_split_minsize}" -Dimporttsv.bulk.output="${bulk_output}" ImportTable "${bulk_input}" 2>&1 | tee -a "${log_file}"

    # 获取Yarn Web对应Application任务的Elapsed时间
    application_id=$(cat < "${log_file}" | grep "Submitted application" | awk '{print $NF}' | tail -n 1)
    echo "[INFO] The application id is ${application_id}" | tee -a "${log_file}"
    duration=$(get_elapsed_time "${application_id}")
    final_status=$(get_final_status "${application_id}")
    if [ "${final_status}" != "SUCCEEDED" ] ; then
        echo "failed" > "${flag_dir}"
        exit 1
    fi
    result_throughput=$(printf "%.2f" "$(echo "scale=2;${data_size}/1024/1024/${duration}/${node_num}"|bc)")
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${result_throughput} =~ ${regular_marchNum} ]] ; then
        echo "$(date) Data size = ${data_size} byte, Run time = ${duration} sec, test failed!" | tee "${report_tmp}"
        echo "failed" > "${flag_dir}"
    else
        echo "$(date) Data size = ${data_size} byte, Run time = ${duration} sec, Throughput = ${result_throughput} MB/Node/s" | tee "${report_tmp}"
        echo "success" > "${flag_dir}"
    fi
    cat "${report_tmp}" >> "${report_file}"
    data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name performance_data unit -v  "${component}" "${tools_v}" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "${result_throughput}" "MB\/Node\/s(吞吐量)"
    stop_collect
}

#################################### 配置解析 #################################################
action=$1

#################################### 测试执行 #################################################
case ${action} in
    prepare)
        prepare_testdata
        ;;
    bulkload)
        bulkload_test
        ;;
    *)
        echo "[Usage] bash ${0##*/} prepare|bulkload"
        exit 1
        ;;
esac
