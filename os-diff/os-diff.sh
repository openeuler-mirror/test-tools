#!/usr/bin/bash

# Copyright (c) 2020. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   zengcongwei
# @Contact   :   735811396@qq.com
# @Date      :   2020/8/10
# @License   :   Mulan PSL v2
# @Desc      :   public library
# #############################################

OS_DIFF_PATH=$(
    cd "$(dirname "$0")" || exit 1

    pwd
)

current_path=$(pwd)
rm -rf ${OS_DIFF_PATH}/rpmlist/results/

function get_rpm_list() {
    list_file=$1
    path1=$2
    path2=$3
    url1=$4
    url2=$5
    #处理地址格式
    echo "$url1" | grep "/$" && repo_url1=${url1%?} || repo_url1=$url1
    echo "$url2" | grep "/$" && repo_url2=${url2%?} || repo_url2=$url2  
    #处理目录格式
    echo "$list_file" | grep '^\/' && list_file=${current_path}/$1   
    echo "$path1" | grep '^\/' && local_path1=$path1 || local_path1=$current_path/$path1   
    echo "$path2" | grep '^\/' && local_path2=$path2 || local_path2=$current_path/$path2   
    
    if echo "$@" | grep "\-p" | grep "\-a" >/dev/null 2>&1; then
        bash $OS_DIFF_PATH/rpmlist/rpmlist.sh -a $local_path1 $local_path2 -p
    elif echo "$@" | grep "\-p" | grep "\-l" >/dev/null 2>&1; then
        bash $OS_DIFF_PATH/rpmlist/rpmlist.sh -l $local_path1 $local_path2 -p $list_file
    elif echo "$@" | grep "\-r" | grep "\-a" >/dev/null 2>&1; then
        bash $OS_DIFF_PATH/rpmlist/rpmlist.sh -a $repo_url1 $repo_url2 -r
    elif echo "$@" | grep "\-r" | grep "\-l" >/dev/null 2>&1; then
        bash $OS_DIFF_PATH/rpmlist/rpmlist.sh -l $repo_url1 $repo_url2 -r $list_file
    elif echo "$@" | grep "\-s" >/dev/null 2>&1; then
        bash $OS_DIFF_PATH/rpmlist/rpmlist.sh -s $repo_url1 $repo_url2 
    fi
}

list_file=list_file
local_path1=local_path
local_path2=local_path
repo_url1=""
repo_url2=""
while getopts "hal:s:S:p:P:r:R:" arg; do
    case $arg in
    a)
        echo "all packages"
        ;;
    l)
        list_file=$OPTARG
        ;;
    s)
        repo_url1=$OPTARG
        ;;
    S)
        repo_url2=$OPTARG
        ;;
    p)
        local_path1=$OPTARG
        ;;
    P)
        local_path2=$OPTARG
        ;;
    r)
        repo_url1=$OPTARG
        ;;
    R)
        repo_url2=$OPTARG
        ;;
    *)
        echo "
Usage:
    bash os-diff.sh [-a] [-l <list_file>] [-s <old package>] [-S <new package>] 
                        [-p <old path>] [-P <new path>] [-r <old url>] [-R <new url>]

Example:
    sh os-diff.sh -a -r old_url -R new_url
    sh os-diff.sh -a -p old_dir -P new_dir
    sh os-diff.sh -l list_file -r old_url -R new_url
    sh os-diff.sh -s old_pkg -S old_pkg
        "
        exit 1
        ;;
    esac
done

get_rpm_list $list_file $local_path1 $local_path2 $repo_url1 $repo_url2 "$@"
