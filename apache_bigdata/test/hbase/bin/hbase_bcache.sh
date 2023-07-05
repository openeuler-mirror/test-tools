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

tool_root_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
app_dir=${tool_root_dir}
flag_dir=${app_dir}/report/flag.report
mkdir -p "${app_dir}"/report
report_file=${tool_root_dir}/report/hbase_pe.report
report_tmp=${tool_root_dir}/report/hbase_pe_tmp.report
mkdir -p "${app_dir}"/log
log_dir=${tool_root_dir}/log
echo "" > "${flag_dir}"

source "${app_dir}"/../tools/commonConfig
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

component=hbase
inputParameter=${1}
source  ${app_dir}/../tools/commonConfig
install_platform=${deploy_mode}
tools_v=PE
if [ ${install_platform} == "ambari" ]; then
    bigdata_platform=HDP3.1.0
    test_model_version=hbase-2.0.2
else
    bigdata_platform=Apache
    test_model_version=hbase-$(cat /usr/local/hbase/NOTICE.txt  | grep Gson | head -1 | awk '{print $2}'| sed 's/.$//')
fi
# 性能数据采集shell脚本
logPath='/tmp/dataCollection/'
source ${logPath}dataCollect.sh
case ${inputParameter} in
    sequential_write_16k)
        testcase=SequentialWrite-16Kb
        ;;
    sequential_write_32k)
        testcase=SequentialWrite-32Kb
        ;;
    sequential_write_64k)
        testcase=SequentialWrite-64Kb
        ;;
    sequential_read_16k)
        testcase=SequentialRead-16Kb
        ;;
    sequential_read_32k)
        testcase=SequentialRead-32Kb
        ;;
    sequential_read_64k)
        testcase=SequentialRead-64Kb
        ;;
esac

# 基础性能数据采集开启
# data_collect --nmon -f 5 -c 60 -- --perf -n AmbariServer -s 5 -d 10 -T 0 --
# data_collect --nmon -f 5 -c 60 -- --local -p ${component} -s "${testcase}" --

function read_16k(){
    check_data read_16k
    test read_16k
}
function read_32k(){
    check_data read_32k
    test read_32k
}
function read_64k(){
    check_data read_64k
    test read_64k
}

function write_16k(){
    test write_16k
}
function write_32k(){
    test write_32k
}
function write_64k(){
    test write_64k
}

function check_data(){
    pre_write_table=Tab_300G_$1
    echo -e "exists '${pre_write_table}'" > table_is_existed.tmp
    if cat < table_is_existed.tmp | hbase shell 2> /dev/null | grep "does not exist" > /dev/null; then
        echo "[INFO] test data${pre_write_table} does not exist, generating test data..."
        case ${1} in
            read_16k)
            ${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --size=300 --valueSize=16384 --table=${pre_write_table} --presplit=300 sequentialWrite 100
            ;;
            read_32k)
            ${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --size=300 --valueSize=32768 --table=${pre_write_table} --presplit=300 sequentialWrite 100
            ;;
            read_64k)
            ${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --size=300 --valueSize=65536 --table=${pre_write_table} --presplit=300 sequentialWrite 100
            ;;
            *)  echo "usage read_16k read_32k read_64k"
                exit 1
        esac
        ((progressflag=1))
        while [ "${progressflag}" -eq 1 ]
        do
            echo "[WARNING] first time to merge the table, wait for compaction progress maybe a log time, you could cancel this and check Ambari web manualy later"
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
    echo "[INFO] check url for Ambari web: http://server1:16010/master-status#compactStas"
    read -r -a progressArr <<< "$(curl http://server1:16010/master-status 2>/dev/null | grep "**.**%" |awk -F "<" '{print $2}'|awk -F ">" '{print $2}'|tr '\n' ' ')"
    # progressArr=$(curl http://server1:16010/master-status 2>/dev/null | grep "**.**%" |awk -F "<" '{print $2}'|awk -F ">" '{print $2}'|tr '\n' ' ')
    i=0
    for progress in "${progressArr[@]}"
    do
        ((i++))
        echo "[INFO] agent${i} Compaction Progress ${progress}"
    done
    for progress in "${progressArr[@]}"
    do
        if [ "${progress}" != 100.00% ];then
            echo "[WARNING] Compaction Progress is not prepared"
            return 1
        fi
    done
    echo "[INFO] Compaction Progress is prepared"
    return 0
}

function test(){
    case ${1} in
        read_16k)
        testtype="sequentialRead"
        test_command="${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --rows=192000 --table=Tab_300G_read_16k sequentialRead 100"
        ;;
        read_32k)
        testtype="sequentialRead"
        test_command="${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --rows=96000 --table=Tab_300G_read_32k sequentialRead 100"
        ;;
        read_64k)
        testtype="sequentialRead"
        test_command="${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --rows=48000 --table=Tab_300G_read_64k sequentialRead 100"
        ;;
        write_16k)
        testtype="sequentialWrite"
        test_command="${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --size=300 --valueSize=16384 --table=Tab_300G_write_16k --presplit=300 sequentialWrite 100"
        ;;
        write_32k)
        testtype="sequentialWrite"
        test_command="${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --size=300 --valueSize=32768 --table=Tab_300G_write_32k --presplit=300 sequentialWrite 100"
        ;;
        write_64k)
        testtype="sequentialWrite"
        test_command="${command_prefix_hbase} hbase org.apache.hadoop.hbase.PerformanceEvaluation --nomapred --size=300 --valueSize=65536 --table=Tab_300G_write_64k --presplit=300 sequentialWrite 100"
        ;;
        *)  echo "usage read_16k read_32k read_64k write_16k write_32k write_64k"
            exit 1
    esac

    echo "" > "${log_dir}"/bcache_tmp.log
    start_collect -t 'PE' -c 'HBase'
    ${test_command} 2>&1 | tee -a "${log_dir}"/bcache.log "${log_dir}"/bcache_tmp.log

    nomapred_flag=$(echo "${test_command}" | grep nomapred > /dev/null 2>&1; echo $?)
    if [ "${nomapred_flag}" == "0" ]; then
        duration=$(grep Avg: "${log_dir}"/bcache_tmp.log | tail -n 1 | awk -F 'Avg: ' '{print $2}' | awk -F 'ms' '{print $1}')
        duration=$(echo "scale=2;${duration}/1000" | bc)
    else
        echo "failed" > "${flag_dir}"
        exit 1
    fi

    #rows=$(tail -n 2 ${log_dir}/${motion}.log | grep ROWS | awk -F "=" '{print $2}')
    if echo "${test_command}" | grep "\-\-size" > /dev/null; then
      size=$(echo "${test_command}" | awk -F "--size=" '{print $2}' | awk -F " " '{print $1}')
      rows=$((size*1024*1024))
    elif echo "${test_command}" | grep "\-\-rows" > /dev/null; then
      rows=$(echo "${test_command}" | awk -F "--rows=" '{print $2}' | awk -F " " '{print $1}')
    fi

    # Get throughput of random read
    if [[ "${testtype}" = "sequentialRead" ]] ; then
        clientNum=100
        throughput=$(echo "scale=2;${rows}/${duration}/3*${clientNum}" | bc)
    fi
    if [[ "${testtype}" = "sequentialWrite" ]] ; then
        throughput=$(echo "scale=2;${rows}/${duration}/3" | bc)
    fi
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${throughput} =~ ${regular_marchNum} ]] ; then
        echo "$(date)  ${testtype} : Row = ${rows}, Duration(s) = ${duration}, Node num = 3, test failed" > "${report_tmp}"
        echo "failed" > "${flag_dir}"
    else
        echo "$(date)  ${testtype} : Row = ${rows}, Duration(s) = ${duration}, Node num = 3, Throughput(ops/node/s) = ${throughput}" > "${report_tmp}"
        echo "success" > "${flag_dir}"
        data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name performance_data unit -v  "${component}" "${tools_v}" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "${throughput}" "MB\/Node\/s(吞吐量)"
        stop_collect
    fi
    cat < "${report_tmp}" | tee -a "${report_file}"
}

case ${inputParameter} in
    sequential_write_16k)
        write_16k
        ;;
    sequential_write_32k)
        write_32k
        ;;
    sequential_write_64k)
        write_64k
        ;;
    sequential_read_16k)
        read_16k
        ;;
    sequential_read_32k)
        read_32k
        ;;
    sequential_read_64k)
        read_64k
        ;;
    *)  echo "[Usage] bash ${0##*/} sequential_write_16k|sequential_write_32k|sequential_write_64k|sequential_read_16k|sequential_read_32k|sequential_read_64k"
        exit 1
        ;;
esac

# 性能数据采集停止
# data_collect stop
