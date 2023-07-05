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
if [[ $# -ne 1 ]] || [[ ${1} != "prepare" ]] && [[ ${1} != "randomWrite" ]] && [[ ${1} != "randomRead" ]] && [[ ${1} != "scanRange100" ]]; then
    echo "[Usage] bash ${0##*/} [prepare|randomWrite|randomRead|scanRange100]"
    exit 1
fi

############################# 运行环境准备 ####################################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
tool_root_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
app_dir=${tool_root_dir}
source "${tool_root_dir}"/conf/pe_config

pe_conf_dir=${tool_root_dir}/conf/PE
source "${app_dir}"/../tools/commonConfig

############################# 生成断言标志位 ####################################################
flag_dir=${app_dir}/report/flag.report
echo "" > "${flag_dir}"

############################# 修改配置文件 ####################################################
case ${deploy_mode} in
    tar)
        command_prefix_hbase=${command_prefix_tar_hbase}
        ;;
    ambari)
        command_prefix_hbase=${command_prefix_ambari_hbase}
        ;;
    *)
        echo "[ERROR] wrong system type, please check ${app_dir}/../tools/commonConfig"
        echo "failed" > "${flag_dir}"
        exit 1
        ;;
esac

# 判断日志log路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/log
log_dir=${tool_root_dir}/log/
check_log=${log_dir}/compaction_progress.log

# 判断输出report路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/report
report_file=${tool_root_dir}/report/hbase_pe.report
report_tmp=${tool_root_dir}/report/hbase_pe_tmp.report

logPath='/tmp/dataCollection/'
#source ${logPath}dataCollect.sh
component=hbase
tools_v=PE
if [ "${install_platform}" == "ambari" ]; then
    bigdata_platform=HDP3.1.0
    test_model_version=hbase-2.0.2
else
    bigdata_platform=Apache
    test_model_version=hbase-$(cat /usr/local/hbase/NOTICE.txt  | grep Gson | head -1 | awk '{print $2}'| sed 's/.$//')
fi

case ${inputParameter} in
    randomWrite)
        testcase=RandomWrite
        ;;
    randomRead)
        testcase=RandomRead
        ;;
    scanRange100)
        testcase=ScanRange100
        ;;
esac

#################################### 方法封装 ##################################################
function file_is_exsit()
{
  file=$1
  if [ ! -f "$file" ]; then
    echo "[INFO] $file is not exsit! Please check the file path!"
    return 1
  fi
  return 0
}

function get_final_status()
{
    app_id=$1
    final_status=$(curl http://localhost:8088/cluster/app/"${app_id}" 2>/dev/null | grep -A 3 "FinalStatus" | grep SUCCEEDE | sed "s/\ //g")
    echo "${final_status}"
}

function data_prepare(){
    echo "[INFO] randomRead/scanRange prepare job start"
    # Write data when table does not exist
    echo -e "exists '${pre_write_table}'" > "${app_dir}"/conf/table_is_existed.tmp
    if cat < "${app_dir}"/conf/table_is_existed.tmp | ${command_prefix_hbase} hbase shell 2> /dev/null | grep "does not exist" > /dev/null; then
        echo "[INFO] test data${pre_write_table} does not exist, generating test data..."
        echo "${pre_command}"
        ${pre_command} 1>"${log_dir}"/"${motion}".log 2>"${log_dir}"/"${motion}".err

        #获取id判断yarn任务是否成功
        application_id_log=$(cat < "${log_dir}"/"${motion}".log | grep "Submitted application" | awk '{print $NF}' | tail -n 1)
        application_id_err=$(cat < "${log_dir}"/"${motion}".err | grep "Submitted application" | awk '{print $NF}' | tail -n 1)
        prepare_status_log=$(get_final_status "${application_id_log}")
        if [ "${prepare_status_log}" != "SUCCEEDED" ] ; then
          prepare_status_err=$(get_final_status "${application_id_err}")
          if [ "${prepare_status_err}" != "SUCCEEDED" ] ; then
              echo "prepare data failed"
              exit 1
          fi
        fi
        echo "prepare data success"

        # Merge table before test
        if [ "${merge_table_flag}"x == "true"x ]; then
            echo "[INFO] Merge table ${pre_write_table}"
            echo -e "major_compact '${pre_write_table}'" > "${app_dir}"/conf/merge_table.tmp
            cat < "${app_dir}"/conf/merge_table.tmp | ${command_prefix_hbase} hbase shell
        fi

        # 判断compation progress是否为100.00%
        ((progressflag=1))
        while [ "${progressflag}" -eq 1 ]
        do
            echo "[INFO] $(date), sleep 10s" | tee -a "${check_log}"
            echo "[WARNING] first time to merge the table, wait for compaction progress maybe a log time, you could cancel this and check Ambari web manualy later" | tee -a "${check_log}"
            check_compaction_progress
            progressflag=${?}
            sleep 10
        done
    else
      echo "[INFO] check ok, ${pre_write_table} exist"
    fi
}

function check_compaction_progress()
{
    echo "[INFO] check url for Ambari web: http://server1:16010/master-status#compactStas" | tee -a "${check_log}"
    read -r -a progressArr <<< "$(curl http://server1:16010/master-status 2>/dev/null | grep "**.**%" |awk -F "<" '{print $2}'|awk -F ">" '{print $2}'|tr '\n' ' ')"
    # progressArr=$(curl http://server1:16010/master-status 2>/dev/null | grep "**.**%" |awk -F "<" '{print $2}'|awk -F ">" '{print $2}'|tr '\n' ' ')
    i=0
    for progress in "${progressArr[@]}"
    do
        ((i++))
        echo "[INFO] agent${i} Compaction Progress ${progress}" | tee -a "${check_log}"
    done
    for progress in "${progressArr[@]}"
    do
        if [ "${progress}" != 100.00% ];then
            echo "[WARNING] Compaction Progress is not prepared" | tee -a "${check_log}"
            return 1
        fi
    done
    echo "[INFO] Compaction Progress is prepared" | tee -a "${check_log}"
    return 0
}

function check_testdata()
{
    echo -e "exists '${pre_write_table}'" > "${app_dir}"/conf/table_is_existed.tmp
    if cat < "${app_dir}"/conf/table_is_existed.tmp | ${command_prefix_hbase} hbase shell 2> /dev/null | grep "does exist" > /dev/null; then
        check_compaction_progress
        echo "[INFO] check ok, ${pre_write_table} exist"
    else
        echo "[ERROR] test data${pre_write_table} does not exist"
        echo "failed" > "${flag_dir}"
        exit 1
    fi
}

function random_write()
{
    check_compaction_progress
    #Random Write
    input_file=check_alive_hbase_input
    # clear file
    echo 'disable "${}"' > ${input_file}
    echo 'drop "${}"' >> ${input_file}
    echo 'exit' >> ${input_file}
    hbase shell ${input_file}>${output_file} 2>/dev/null
    rm -f ${input_file}

    echo "[INFO] ${test_command}"
    
    echo "" > "${log_dir}"/"${motion}"_tmp.log
    start_collect -t 'PE' -c 'HBase'
    ${test_command} 2>&1 | tee -a "${log_dir}"/"${motion}".log "${log_dir}"/"${motion}"_tmp.log

    nomapred_flag=$(echo "${test_command}" | grep nomapred > /dev/null 2>&1; echo $?)
    if [ "${nomapred_flag}" == "0" ]; then
           duration_w=`grep   duration   ${log_dir}${motion}_tmp.log    | awk   '{print $14}'   | tr  -d "[a-z]" `
	   duration_t=$duration_w
	   duration_w=`echo    "scale=4;102400000/3/$duration_w"  | bc`
	   duration=$duration_w
	   echo $duration
    else
        echo "[ERROR] mapred mod not support, should be nomapred, please check ${pe_conf_dir}/${motion}.setting!"
        echo "failed" > "${flag_dir}"
        exit 1
    fi

    if echo "${test_command}" | grep "\-\-size" > /dev/null; then
       size=$(echo "${test_command}" | awk -F "--size=" '{print $2}' | awk -F " " '{print $1}')
       rows=$((size*1024*1024))
    elif echo "${test_command}" | grep "\-\-rows" > /dev/null; then
       rows=$(echo "${test_command}" | awk -F "--rows=" '{print $2}' | awk -F " " '{print $1}')
    fi

    # Get throughput of random write
    #let write_throughput=${rows}/${duration}/${node_num}
    write_throughput=$(echo "scale=2;${rows}/${duration}/${node_num}" | bc)
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${write_throughput} =~ ${regular_marchNum} ]] ; then
        echo "$(date)  ${motion}: Row = ${rows}, Duration(s) = ${duration}, Node num = ${node_num}, test failed!" > "${report_tmp}"
        echo "failed" > "${flag_dir}"
    else
        echo "$(date)  ${motion}: Row = ${rows}, Duration(s) = ${duration_t}, Node num = ${node_num}, Throughput(Mb/node/s) = ${duration}" > "${report_tmp}"
        echo "success" > "${flag_dir}"
    fi
    cat < "${report_tmp}" | tee -a "${report_file}"
    data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name performance_data unit -v "${component}" "${tools_v}" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "${write_throughput}" "ops\/node\/s(吞吐量)"
    stop_collect
}

function random_read()
{
    # check test data exist
    check_testdata

    # Random Read
    echo "[INFO] ${test_command}"
    echo "" > "${log_dir}"/"${motion}"_tmp.log
    start_collect -t 'PE' -c 'HBase'
    ${test_command} 2>&1 | tee -a "${log_dir}"/"${motion}".log "${log_dir}"/"${motion}"_tmp.log

    nomapred_flag=$(echo "${test_command}" | grep nomapred > /dev/null 2>&1; echo $?)
    if [ "${nomapred_flag}" == "0" ]; then
    	duration_r=`grep   duration   ${log_dir}${motion}_tmp.log    | awk   '{print $14}'   | tr  -d "[a-z]" `
        duration_t=$duration_r
        duration_r=`echo    "scale=4;102400000/3/$duration_r"  | bc`
        duration=$duration_r
    else
        echo "[ERROR] mapred mod not support, should be nomapred, please check ${pe_conf_dir}/${motion}.setting!"
        echo "failed" > "${flag_dir}"
        exit 1
    fi

    #rows=`tail -n 2 ${log_dir}/${motion}.log | grep ROWS | awk -F "=" '{print $2}'`
    if echo "${test_command}" | grep "\-\-size" > /dev/null; then
      size=$(echo "${test_command}" | awk -F "--size=" '{print $2}' | awk -F " " '{print $1}')
      rows=$((size*1024*1024))
    elif echo "${test_command}" | grep "\-\-rows" > /dev/null; then
      rows=$(echo "${test_command}" | awk -F "--rows=" '{print $2}' | awk -F " " '{print $1}')
    fi

    # Get throughput of random read
    #let read_throughput=${rows}/${duration}/${node_num}*${client_num}
    clientNum=$(cat < "${pe_conf_dir}"/randomRead.setting | grep "\-\-client" | awk -F "=" '{print $2}')
    read_throughput=$(echo "scale=2;${rows}/${duration}/${node_num}*${clientNum}" | bc)
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${read_throughput} =~ ${regular_marchNum} ]] ; then
        echo "$(date)  ${motion}: Row = ${rows}, Duration(s) = ${duration}, Node num = ${node_num}, test failed" > "${report_tmp}"
        echo "failed" > "${flag_dir}"
    else
        echo "$(date)  ${motion}: Row = ${rows}, Duration(s) = ${duration_t}, Node num = ${node_num}, Throughput(Mb/node/s) = ${duration}" > "${report_tmp}"
        echo "success" > "${flag_dir}"
    fi
    cat < "${report_tmp}" | tee -a "${report_file}"
    data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name performance_data unit -v "${component}" "${tools_v}" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "${read_throughput}" "ops\/node\/s(吞吐量)"
    stop_collect
}

function scan_range100()
{
    # check test data exist
    check_testdata

    # Scan Range 100
    "[INFO] ${test_command}"
    echo "" > "${log_dir}"/"${motion}"_tmp.log
    ${test_command} 2>&1 | tee -a "${log_dir}"/"${motion}".log "${log_dir}"/"${motion}"_tmp.log

    nomapred_flag=$(echo "${test_command}" | grep nomapred > /dev/null 2>&1; echo $?)
    if [ "${nomapred_flag}" == "0" ]; then
        duration=$(tail -n 50 "${log_dir}"/"${motion}"_tmp.log | grep Avg: | tail -n 1 | awk -F 'Avg: ' '{print $2}' | awk -F 'ms' '{print $1}')
        duration=$(echo "scale=2;${duration}/1000" | bc)
    else
        echo "[ERROR] mapred mod not support, should be nomapred, please check ${pe_conf_dir}/${motion}.setting!"
        echo "failed" > "${flag_dir}"
        exit 1
    fi

    #rows=`tail -n 2 ${log_dir}/${motion}.log | grep ROWS | awk -F "=" '{print $2}'`
    if echo "${test_command}" | grep "\-\-size" > /dev/null; then
      size=$(echo "${test_command}" | awk -F "--size=" '{print $2}' | awk -F " " '{print $1}')
      rows=$((size*1024*1024))
    elif echo "${test_command}" | grep "\-\-rows" > /dev/null; then
      rows=$(echo "${test_command}" | awk -F "--rows=" '{print $2}' | awk -F " " '{print $1}')
    fi

    # Get throughput of random read
    #let scan_throughput=${rows}/${duration}/${node_num}${client_num}
    scan_throughput=$(echo "scale=2;${rows}/${duration}/${node_num}*${client_num}" | bc)
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${scan_throughput} =~ ${regular_marchNum} ]] ; then
        echo "$(date)  ${motion}: Row = ${rows}, Duration(s) = ${duration}, Node num = ${node_num}, Client num = ${client_num}, test failed!" > "${report_tmp}"
        echo "failed" > "${flag_dir}"
    else
        echo "$(date)  ${motion}: Row = ${rows}, Duration(s) = ${duration}, Node num = ${node_num}, Client num = ${client_num}, Throughput(ops/node/s) = ${scan_throughput}" > "${report_tmp}"
        echo "success" > "${flag_dir}"
    fi
    cat < "${report_tmp}" | tee -a "${report_file}"
}

################################## 配置解析 #############################################
motion=$1

# PE Part Command
if [ "${motion}" == "randomWrite" ] || [ "${motion}" == "randomRead" ] || [ "${motion}" == "scanRange100" ]; then
    motion_setting=$1.setting
    file_is_exsit "${pe_conf_dir}"/"${motion_setting}"
    if [ $? -eq 1 ]; then
        echo "${pe_conf_dir}/${motion_setting} doesn't exist"
        echo "failed" > "${flag_dir}"
        exit 1
    fi

    start_time=$(date +"%Y-%m-%d-%H:%M:%S")
    echo -e "\033[32m#####################START TIME####################\033[0m"
    echo -e "\033[32m---------------${start_time}----------------\033[0m"
    echo -e "\033[32m###################################################\033[0m"
    echo -e "\033[32m#####################HBASE SETTING####################\033[0m"
    cat < "${pe_conf_dir}"/"${motion_setting}"
    echo -e "\033[32m##################################################### \033[0m"
    echo -e "\033[32m${motion} is executing............. \033[0m"

    test_command="${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation"

    motion_list=$(cat < "${pe_conf_dir}"/"${motion_setting}")
    for para in ${motion_list}
    do
        para_name=$(echo "${para}" | awk -F "=" '{print $1}')
        #if [ `echo ${para} | awk -F "=" '{print $1}'` == "--client" ]; then
        if [ "${para_name}" == "--client" ]; then
            client_num=$(echo "${para}" | awk -F "=" '{print $2}')
        else
            test_command="${test_command} ${para}"
        fi
    done
    test_command="${test_command} ${motion} ${client_num}"
fi

# Motion Read or Scan nead 300GRegion Data
if [ "${motion}" == "prepare" ] || [ "${motion}" == "randomRead" ] || [ "${motion}" == "scanRange100" ]; then
    pre_command="${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation"

    motion_list=$(cat "${pe_conf_dir}"/pre-sequentialWrite.setting)
    for para in ${motion_list}
    do
        para_name=$(echo "${para}" | awk -F "=" '{print $1}')
        #if [ `echo ${para} | awk -F "=" '{print $1}'` == "--client" ]; then
        if [ "${para_name}" == "--client" ]; then
            client_num=$(echo "${para}" | awk -F "=" '{print $2}')
        else
            pre_command="${pre_command} ${para}"

            if [ "$(echo "${para}" | awk -F "=" '{print $1}')" == "--table" ]; then
                pre_write_table=$(echo "${para}" | awk -F "=" '{print $2}')
            fi
        fi
    done
    pre_command="${pre_command} sequentialWrite ${client_num}"
fi

################################## 测试执行 ################################################
case ${motion} in
    prepare)
        data_prepare
        ;;
    randomWrite)
        random_write
        ;;
    randomRead)
        random_read
        ;;
    scanRange100)
        scan_range100
        ;;
    *)
        echo "[Usage] bash ${0##*/} [prepare|randomWrite|randomRead|scanRange100]"
        exit 1
        ;;
esac

rm -rf "${app_dir}"/conf/*.tmp
