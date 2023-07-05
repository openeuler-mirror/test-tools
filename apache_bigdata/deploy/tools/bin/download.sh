#!/bin/sh
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
cd $(dirname "$0") || exit 1
tool_root_dir=$(cd ../ || exit 1;pwd)
source "${tool_root_dir}"/conf/config

has_wget=$(command -v wget)
if [ "${has_wget}" == "" ]; then
  echo "Please install wget first!"
  exit 1
fi

mkdir -p "${tool_root_dir}/deps/"

# Download os iso file

if [ "${local_iso_flag}" == "true" ];then
    if [ ! -f "${tool_root_dir}"/deps/"${os_iso}" ]; then
        echo "Download ${os_iso}!"
        if ! wget -O "${tool_root_dir}"/deps/"${os_iso}" "${download_url}"/os-iso/"${os_iso}" ; then
            echo "Failed to download ${os_iso}, please check your configure!"
            exit 1;
        fi
    fi
fi
# Download jdk file
if [ ! -f "${tool_root_dir}"/deps/"${jdk_package}" ]; then
    echo "Download ${jdk_package}!"
    if ! wget -O "${tool_root_dir}"/deps/"${jdk_package}" "${download_url}"/jdk/"${jdk_package}" ; then
        echo "Failed to download ${jdk_package}, please check your configure!"
        exit 1;
    fi
fi
