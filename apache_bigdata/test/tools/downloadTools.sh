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
if [[ $# -ne 1 ]]; then
    echo "[Usage] bash ${0##*/} all|TPCDS|Benchmark|Hibench|EsDeps"
    exit
fi

########################################### 环境准备 #########################################
has_wget=$(command -v wget)
if [ "${has_wget}" == "" ]; then
    echo "[ERROR] Please install wget first!"
    exit 1
fi

automated_root_dir=$(cd "$(dirname "$0")/../.." || exit 1;pwd)
tools_dir=$(cd "$(dirname "$0")" || exit 1;pwd)
# 判断testtools目录是否存在，不存在则创建
mkdir -p "${automated_root_dir}"/testtools
testtools_dir=${automated_root_dir}/testtools
bash "${automated_root_dir}/scripts/tools/change_config.sh"
source "${automated_root_dir}"/scripts/tools/envConfig

############################################ 方法封装 #########################################
function checkAndDownloadTools()
{
    component=$1
    echo "[INFO] check dir :${automated_root_dir}/testtools/${tools_extract_dir}" |tee -a "${testtools_dir}"/download.log
    # 判断tools是否存在，存在则直接退出
    if [ -d "${automated_root_dir}/testtools/${tools_extract_dir}" ]; then
        echo "[INFO] ${tools_extract_dir} has been installed"
        return 0
    else
        downloadTools
        deploytools "${component}"
    fi
}

function downloadTools() 
{
    # Download testtools
    echo "[INFO] wget -P ${testtools_dir} ${tools_factory_url}" |tee -a "${testtools_dir}"/download.log
    if [ -f "${testtools_dir}/${toolsPackage}" ]; then
        echo "[INFO] delete old package ${testtools_dir}/${toolsPackage}" |tee -a "${testtools_dir}"/download.log
        \rm "${testtools_dir}"/"${toolsPackage}"
    fi
    wget -c -P "${testtools_dir}" "${tools_factory_url}" 2>&1 | tee -a "${testtools_dir}"/download.log
    # 工具解压缩
    cd "${testtools_dir}" || exit 1
    echo "[INFO] tar -xf ${toolsPackage}" |tee -a "${testtools_dir}"/download.log
    tar -xf "${toolsPackage}"
    echo "[INFO] 解压OK" |tee -a "${testtools_dir}"/download.log
}


####################################### 主流程方法 ###########################################
function install()
{
    componentStr=$1
    read -r -a componentArry <<< "$(echo "${componentStr}" | tr ',' ' ')"
    for component in "${componentArry[@]}"
    do
        # 下载
        echo "[INFO] -----------------${component}-----------------"
        case ${component} in
            TPCDS)
                toolsName=tpcds
                toolsPackage=${tpcds_package}
                tools_extract_dir=${tpcds_extract_dir}
                ;;
            Hibench)
                toolsName=hibench
                toolsPackage=${hibench_package}
                tools_extract_dir=${hibench_extract_dir}
                ;;
            Benchmark)
                toolsName=benchmark
                toolsPackage=${benchmark_package}
                tools_extract_dir=${benchmark_extract_dir}
                ;;
            EsDeps)
                toolsName=esDepsTools
                toolsPackage=${esdeps_package}
                tools_extract_dir=${esdeps_extract_dir}
                ;;
            *)  echo "[Usage] bash ${0##*/} TPCDS,Benchmark,Hibench,EsDeps"
                exit 1
                ;;
        esac
        # 指定远端仓库工具位置
        tools_factory_url=${download_url}/Tools/toolsFactory/${toolsName}/${arch}/${toolsPackage}
        checkAndDownloadTools "${component}"
    done
}

function deploytools() {
    # 安装
    component=${1}
    case ${component} in
        TPCDS|Hibench|Benchmark)
            echo "[INFO] install ${component}" |tee -a "${testtools_dir}"/download.log
            ;;
        EsDeps)
            bash "${tools_dir}"/toolsdeployment/esrallydeploy.sh | tee -a "${testtools_dir}"/download.log
            ;;
        *)  echo "[Usage] bash ${0##*/} TPCDS,Benchmark,Hibench,EsDeps"
            exit 1
            ;;
    esac
}

case ${1} in
    TPCDS|Hibench|Benchmark|EsDeps)
        install "${1}"
        ;;
    all)
        install TPCDS,Hibench,Benchmark,EsDeps
        ;;
    *)  echo "[Usage] bash ${0##*/} all|TPCDS|Benchmark|Hibench|EsDeps"
        exit 1
        ;;
esac
