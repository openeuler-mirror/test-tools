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
if [[ $# -ne 1 ]] || [[ ${1} != "Wordcount" ]] && [[ ${1} != "Terasort" ]] && [[ ${1} != "Bayes" ]] && [[ ${1} != "Kmeans" ]] && [[ ${1} != "prepare_Wordcount" ]] && [[ ${1} != "prepare_Terasort" ]] && [[ ${1} != "prepare_Bayes" ]] && [[ ${1} != "prepare_Kmeans" ]]; then
    echo "[Usage] bash ${0##*/} [prepare_Wordcount|prepare_Terasort|prepare_Bayes|prepare_Kmeans|Wordcount|Terasort|Bayes|Kmeans]"
    exit 1
fi

############################# 运行环境准备 ####################################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
app_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
source "${app_dir}"/conf/hibench_config
hibench_dir=${app_dir}/../../testtools/${hibench_file}
HibenchConf_dir=${app_dir}/conf/HibenchConf
source "${app_dir}"/../tools/commonConfig

############################# 生成断言标志位 ####################################################
flag_dir=${app_dir}/report/flag.report
echo "" > "${flag_dir}"

############################# 修改配置文件 ####################################################
case ${deploy_mode} in
    tar)
        command_prefix_hdfs=$command_prefix_tar_hdfs
        ;;
    ambari)
        command_prefix_hdfs=$command_prefix_ambari_hdfs
        ;;
    *)
        echo "[ERROR] wrong system type, please check ${app_dir}/../tools/commonConfig"
        echo "failed" > "${flag_dir}"
        exit 1
        ;;
esac

# 判断Hibench工具是否存在，不存在，直接停止脚本（生成数据+测试）
if [ ! -d "${hibench_dir}" ]; then
  echo "[ERROR] Hibench tool doesn't exist, please upload to ${tpcds_dir}."
  echo "failed" > "${flag_dir}"
  exit 1
fi

# 判断日志log路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}/log"
log_file=${app_dir}/log/spark_hibench.log
err_file=${app_dir}/log/spark_hibench.err

# 判断输出report路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}/report"
report_file=${app_dir}/report/spark_hibench.report
report_file_tmp=${app_dir}/report/spark_hibench_tmp.report

PATH=${JAVA_HOME}/bin:${PATH}

component=spark
logPath='/tmp/dataCollection/'
#source ${logPath}dataCollect.sh
if [ "${install_platform}" == "ambari" ]; then
    bigdata_platform=HDP3.1.0
    test_model_version=spark-2.3.2
else
    bigdata_platform=Apache
    test_model_version=spark-$(cat /usr/local/spark/RELEASE | awk 'NR==1''{print$2}')
fi

case ${inputParameter} in
    Wordcount)
        testcase="WordCount"
        ;;
    Terasort)
        testcase="Terasort"
        ;;
    Kmeans)
        testcase="Kmeans"
        ;;
    Bayes)
        testcase="Bayes"
        ;;
esac

#################################### 方法封装 ##################################################
function test_prepare()
{
    case ${1} in
        prepare_Wordcount)
            prepare_script='bin/workloads/micro/wordcount/prepare/prepare.sh'
            test_type="Wordcount"
            ;;
        prepare_Terasort)
            prepare_script='bin/workloads/micro/terasort/prepare/prepare.sh'
            test_type="Terasort"
            ;;
        prepare_Bayes)
            prepare_script='bin/workloads/ml/bayes/prepare/prepare.sh'
            test_type="Bayes"
            ;;
        prepare_Kmeans)
            prepare_script='bin/workloads/ml/kmeans/prepare/prepare.sh'
            test_type="Kmeans"
            ;;
        *)  echo "[Usage] bash ${0##*/} [prepare_Wordcount|prepare_Terasort|prepare_Bayes|prepare_Kmeans|Wordcount|Terasort|Bayes|Kmeans]"
            echo "failed" > "${flag_dir}"
            exit 1
            ;;
    esac

    case ${deploy_mode} in
        tar)
            spark_shell_dir=$(command -v spark-shell)
            spark_dir=${spark_shell_dir%spark/*}
            spark_version=$(ls "${spark_dir}" | grep spark- |sed -n '1p'|awk -F "-" '{print $2}')
            if [[ "${spark_version}" == 1.* ]];then
                \cp "${hibench_dir}"/sparkbench/assembly/target/sparkbench-assembly-7.0-dist.jar.1.6.0.cdh "${hibench_dir}"/sparkbench/assembly/target/sparkbench-assembly-7.0-dist.jar
                echo "[INFO] sparkbench-assembly-7.0-dist.jar switch to version 1.6.0"
            elif [[ "${spark_version}" == 2.* ]];then
                \cp "${hibench_dir}"/sparkbench/assembly/target/sparkbench-assembly-7.0-dist.jar.2.3.2.hdp "${hibench_dir}"/sparkbench/assembly/target/sparkbench-assembly-7.0-dist.jar
                echo "[INFO] sparkbench-assembly-7.0-dist.jar switch to version 2.3.2"
            fi
            ;;
        ambari)
            \cp "${hibench_dir}"/sparkbench/assembly/target/sparkbench-assembly-7.0-dist.jar.2.3.2.hdp "${hibench_dir}"/sparkbench/assembly/target/sparkbench-assembly-7.0-dist.jar
            echo "[INFO] sparkbench-assembly-7.0-dist.jar switch to version 2.3.2"
            ;;
        *)
            echo "[ERROR] wrong system type, please check ${app_dir}/../tools/commonConfig"
            echo "failed" > "${flag_dir}"
            exit 1
            ;;
    esac

    spark_envtlog_path_hdfs=$(grep -R "^spark.eventLog.dir" "${HibenchConf_dir}"/spark.conf | awk -F " " '{print $2}' | awk -F "hdfs://" '{print $2}')
    ${command_prefix_hdfs} hdfs dfs -mkdir -p "${spark_envtlog_path_hdfs}"

    echo "[INFO] Hibench conf 配置文件COPY"
    echo "[INFO] cp -rf ${HibenchConf_dir}/* ${hibench_dir}/conf/"
    cp -rf "${HibenchConf_dir}"/* "${hibench_dir}"/conf/

    # 修改HiBench测试工具所有者
    # chown -R hdfs:hadoop ${hibench_dir}
    if [ "${deploy_mode}" = ambari ]; then
       chown -R hdfs:hadoop "${hibench_dir}"
    fi

    # 判断测试数据是否存在，不存在，则生成
    data_target_base_dir=$(sed -n '/hibench.hdfs.master/p' "${hibench_dir}"/conf/hadoop.conf | awk '{print $2}')
    data_target_dir=${data_target_base_dir}/HiBench/${test_type}
    is_data_existed=$(${command_prefix_hdfs} hadoop fs -ls "${data_target_dir}"/Input > /dev/null 2>&1; echo $?)
    if [[ "${regenerate_data}" == "true" ]] || [[ "${is_data_existed}" -ne 0 ]]; then
        echo "[INFO] ${test_type} data doesn't exist, start to generate..." | tee -a "${log_file}"

        # 避免用户无权限写目录的情况
       ${command_prefix_hdfs} hadoop fs -rm -r "${data_target_dir}"/Output
       ${command_prefix_hdfs} hadoop fs -mkdir -p "${data_target_base_dir}"/HiBench
       ${command_prefix_hdfs} hadoop fs -chmod -R 777 "${data_target_base_dir}"/HiBench

        # 生成测试数据
        bash "${hibench_dir}"/${prepare_script} 1>>"${log_file}" 2>>"${err_file}"
        echo "[INFO] ${test_type} generate data finish" | tee -a "${log_file}"
        # 睡眠一段时间，让数据均匀落盘
        echo "sleep ${sleep_time} seconds， waiting data flushing to disks..."
        sleep "${sleep_time}"
    else
        # 避免用户无权限写目录的情况
       ${command_prefix_hdfs} hadoop fs -rm -r "${data_target_dir}"/Output
       ${command_prefix_hdfs} hadoop fs -chmod -R 777 "${data_target_base_dir}"/HiBench
        echo "[INFO] ${test_type} data check OK!" | tee -a "${log_file}"
    fi


}

function test_execute()
{
    echo "[WARNING] make sure you have prepare this testcase: prepare_${1}"
    case ${1} in
        Wordcount)
            run_script='bin/workloads/micro/wordcount/spark/run.sh'
            ;;
        Terasort)
            run_script='bin/workloads/micro/terasort/spark/run.sh'
            ;;
        Bayes)
            run_script='bin/workloads/ml/bayes/spark/run.sh'
            ;;
        Kmeans)
            run_script='bin/workloads/ml/kmeans/spark/run.sh'
            ;;
        *)  echo "[Usage] bash ${0##*/} [prepare_Wordcount|prepare_Terasort|prepare_Bayes|prepare_Kmeans|Wordcount|Terasort|Bayes|Kmeans]"
            run_script=''
            echo "failed" > "${flag_dir}"
            exit 1
            ;;
    esac

    # 执行测试
    start_collect -t 'HiBench' -c 'Spark'
    echo "${1} start to execute test" | tee -a "${log_file}"
    echo "[INFO] ${hibench_dir}/${run_script}"
    bash "${hibench_dir}"/"${run_script}" 1>>"${log_file}" 2>>"${err_file}"

    # 结果格式化输出
    if [ $? -eq 0 ]; then
        # 格式化输出
        result_type=$(tail -n 1 "${hibench_dir}"/report/hibench.report | awk '{print $1}')
        result_date=$(tail -n 1 "${hibench_dir}"/report/hibench.report | awk '{print $2}')
        result_time=$(tail -n 1 "${hibench_dir}"/report/hibench.report | awk '{print $3}')
        result_throughput=$(tail -n 1 "${hibench_dir}"/report/hibench.report | awk '{print $7}')
        result_node_min_throughput=$(echo | awk "{print $result_throughput/1024/1024}")
        regular_marchNum='^[0-9]+([.][0-9]+)?$'
        if ! [[ ${result_node_min_throughput} =~ ${regular_marchNum} ]] ; then
            echo "${result_type} ${result_date} ${result_time} throughput: test failed!" > "${report_file_tmp}"
            echo "failed" > "${flag_dir}"
        else
            echo "${result_type} ${result_date} ${result_time} throughput: ${result_node_min_throughput} MB/Sec/Node" > "${report_file_tmp}"
            echo "success" > "${flag_dir}"
        fi
    else
        echo "$(date +"%Y-%m-%d %H:%M:%S")  test failed!" > "${report_file_tmp}"
        echo "failed" > "${flag_dir}"
    fi
data_record -k test_model tool_version bigdata_platform install_platform test_model_version testcase_name performance_data unit -v "${component}" "HiBench-HiBench-7.0" "${bigdata_platform}" "${install_platform}" "${test_model_version}" "${testcase}" "${result_node_min_throughput}" "GB\/min\/node(吞吐量)"
stop_collect
    cat < "${report_file_tmp}" | tee -a "${report_file}"
}

################################## 配置解析 #############################################
inputParameter=${1}

################################## 测试执行 ################################################
# deal yarn cmd timeout
source /etc/profile
yarn node -list 2> /dev/null | grep RUNNING

case ${inputParameter} in
    prepare_Wordcount|prepare_Terasort|prepare_Bayes|prepare_Kmeans)
        test_prepare "${inputParameter}"
        ;;
    Wordcount|Terasort|Bayes|Kmeans)
        test_execute "${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} [prepare_Wordcount|prepare_Terasort|prepare_Bayes|prepare_Kmeans|Wordcount|Terasort|Bayes|Kmeans]"
        exit 1
        ;;
esac
