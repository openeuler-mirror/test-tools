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
if [[ $# -ne 1 ]] || [[ ${1} != "write" ]] && [[ ${1} != "read" ]]; then
    echo "[Usage] bash ${0##*/} [write|read]"
    exit
fi

############################# 运行环境准备 ####################################################
echo "[WARNING] PLEASE MAKE SURE THE PARENT DIR ALL OF THE PATH HAS THE EXECUTE PERMISSION FOR OTHER USERS"
tool_root_dir=$(cd "$(dirname "${0}")"/..||exit 1;pwd)
app_dir=${tool_root_dir}
source "${tool_root_dir}"/conf/dfsio_config
source "${app_dir}"/../tools/commonConfig

dfsio_conf_dir=${tool_root_dir}/conf/dfsio
# 判断日志log路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/log
log_dir=${app_dir}/log/

# 判断输出report路径是否存在，如果不存在则先创建
mkdir -p "${app_dir}"/report
report_file=${app_dir}/report/hadoop_dfsio.report
report_file_tmp=${app_dir}/report/hadoop_dfsio_tmp.report

############################# 生成断言标志位 ####################################################
flag_dir=${app_dir}/report/flag.report
echo "" > "${flag_dir}"

################################ 判断类型 #######################################################
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

#################################### 方法封装 ##################################################
function get_final_status()
{
    app_id=$1
    final_status=$(curl http://localhost:8088/cluster/app/"${app_id}" 2>/dev/null | grep -A 3 "FinalStatus" | grep SUCCEEDE | sed "s/\ //g")
    echo "${final_status}"
}

function execute_motion()
{
    motion=$1
    motion_setting=$1.setting
    node_num=$2
    echo "" > "${log_dir}"/"${motion}"_tmp.log
    file_is_exsit "${dfsio_conf_dir}"/"${motion_setting}"
    if [ $? -eq 1 ]; then
        echo "[ERROR] ${dfsio_conf_dir}/${motion_setting} doesn't exist" | tee -a "${log_dir}"/"${motion}".log "${log_dir}"/"${motion}"_tmp.log
        exit 1
    fi

    start_time=$(date +"%Y-%m-%d-%H:%M:%S")
    echo -e "\033[32m#####################START TIME####################\033[0m"
    echo -e "\033[32m---------------${start_time}----------------\033[0m"
    echo -e "\033[32m###################################################\033[0m"
    echo -e "\033[32m####################HADOOP SETTING###################\033[0m"
    cat "${dfsio_conf_dir}"/"${motion_setting}"
    echo -e "\033[32m##################################################### \033[0m"
    echo -e "\033[32m${motion} is executing............. \033[0m"

    # DFSIO Part Command
    test_command="${test_user} hadoop jar ${jar_file} TestDFSIO -"${motion}
    test_command=$(get_test_para "${test_command}" "${motion_setting}")

    ${test_command} 2>&1 | tee -a "${log_dir}"/"${motion}".log "${log_dir}"/"${motion}"_tmp.log

    #获取id判断yarn任务是否成功
    application_id=$(cat < "${log_dir}"/"${motion}"_tmp.log | grep "Submitted application" | awk '{print $NF}' | tail -n 1)
    final_status=$(get_final_status "${application_id}")
    if [ "${final_status}" != "SUCCEEDED" ] ; then
          echo "failed" > "${flag_dir}"
          exit 1
    fi

    tail -n 9 "${log_dir}"/"${motion}"_tmp.log >> "${report_file}"
    Throughput=$(tail -n 9 "${log_dir}"/"${motion}"_tmp.log | sed -n '5p' | awk '{print $7}')
    regular_marchNum='^[0-9]+([.][0-9]+)?$'
    if ! [[ ${Throughput} =~ ${regular_marchNum} ]] ; then
        echo "${1} $(date) result: test failed!" | tee "${report_file_tmp}"
        echo "failed" > "${flag_dir}"
        exit 1
    else
        echo "${1} $(date) result: Throughput ${Throughput} MB/S" | tee "${report_file_tmp}"
        echo "success" > "${flag_dir}"
    fi
}

function get_test_para()
{
    test_command=${1}
    motion_setting=${2}

    para_list=$(cat "${dfsio_conf_dir}"/"${motion_setting}")
    for para in ${para_list}
    do
        test_command="${test_command} ${para}"
    done

    echo "${test_command}"
}

function file_is_exsit()
{
  file=$1
  if [ ! -f "${file}" ]; then
    echo "[ERROR] ${file} is not exsit! Please check the file path!"
    return 1
  fi
  return 0
}


#################################### 测试执行 ##################################################
inputParameter=${1}

case ${inputParameter} in
    read|write)
        execute_motion "${inputParameter}" "${node_num}"
        ;;
    *)
        echo "[Usage] bash ${0##*/} [write|read]"
        exit 1
        ;;
esac