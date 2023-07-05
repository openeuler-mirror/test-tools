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

############################################################ 参数数量合法性检查 ####################################################################
if [[ $# -ne 1 ]] || [[ ${1} != "tar" ]] && [[ ${1} != "ambari" ]]; then
    echo "Usage: bash ${0##*/} tar|ambari"
    exit 1
fi

########################################################### 运行环境准备 ###########################################################################
scripts_dir=$(cd "$(dirname "$0")/../.." || exit 1;pwd)
commonConfig_file=${scripts_dir}/tools/commonConfig
if [ ! -f "${commonConfig_file}" ]; then
    echo "[ERROR] ${commonConfig_file} config file not exit"
    exit 1
fi

############################# 依据系统不同,解析configlistCentos/configlistOpenEuler文件内容 适配对应的组件 ##########################################
function modify_conf()
{
    filename=${1}
    filename_dir=${scripts_dir}/tools/systemconfigadjust/${filename}
    echo "[INFO] analyse config file: ${filename_dir}"
    if [ ! -f "${filename_dir}" ]; then
        echo "[ERROR] ${filename_dir}  config file not exit"
        exit 1
    fi

    grep -v "^#" "${filename_dir}" | sed '/^\s*$/d' | while read -r line
    do
        component_name=$(echo "$line" | awk -F ";" '{print $1}')
        config_path=$(echo "$line" | awk -F ";" '{print $2}')
        config_key_value=$(echo "$line" | awk -F ";" '{print $3}')
        analytic_parameter "${component_name}" "${config_path}" "${config_key_value}"
    done
}


function analytic_parameter()
{
    component_name=${1}
    config_path=${2}
    config_key_value=${3}
    modify_file=${scripts_dir}/${component_name}/${config_path}

    if [ ! -f "${modify_file}" ]; then
        echo "[ERROR] ${scripts_dir}/${component_name}/${config_path} config file not exit"
        exit 1
    fi

    ########## 替换全文制表符
    sed -i 's!\t! !g' "${modify_file}"

    if [[ ${config_key_value} =~ "=" ]];then
        replace_key=$(echo "${config_key_value}" | awk -F "=" '{print $1}')
        if [[ $(grep "^${replace_key}=" "${modify_file}") != "" ]];then
            sed -i "s!^${replace_key}=.*!${config_key_value}!g" "${modify_file}"
            echo "[INFO] modify key value: --${config_key_value}-- in ${modify_file}"
        else
            echo "[ERROR] ${replace_key} not exist, please check ${modify_file}"
            exit 1
        fi
    elif [[ ${config_key_value} =~ " " ]];then
        replace_key=$(echo "${config_key_value}" | awk -F " " '{print $1}')
        if [[ $(grep "^${replace_key} " "${modify_file}") != "" ]];then
            sed -i "s!^${replace_key} .*!${config_key_value}!g" "${modify_file}"
            echo "[INFO] modify key value: --${config_key_value}-- in ${modify_file}"
        else
            echo "[ERROR] ${replace_key} not exist, please check ${modify_file}"
            exit 1
        fi
    else
        echo "[ERROR] no such type，please check your config"
        exist 1
    fi
}

############################################################# 配置解析 ##############################################################
inputParameter=${1}

#################################判断操作系统类型根据文件参数配置内容修改对应配置文件###################################################
case ${inputParameter} in
   ambari|tar)
        ########### 修改commonConfig文件deploy_mode的配置项#######################
        analytic_parameter "tools" "commonConfig" "deploy_mode=${inputParameter}"
        modify_conf configlist_"${inputParameter}"
        ;;
   *)  echo "[Usage] bash ${0##*/} tar|ambari"
       exit 1
       ;;
esac
