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

if [ $# != 1 ] ; then
  echo "USAGE: $0 cmd"
  echo " e.g.: $0 deploy"
  exit 1;
fi

#check param
tool_root_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
source "${tool_root_dir}"/bin/common/remote.sh
source "${tool_root_dir}"/conf/config

echo "version ${hadoop_version}"
if test -z "${hadoop_version}"
then
  echo "hadoop_version is not set!"
  exit 1
fi
if test -z "${hadoop_dir}"
then
  echo "hadoop_dir is not set!"
  exit 1
fi
if test -z "${namenode}"
then
  echo "namenode is not set!"
  exit 1
fi
if test -z "${datanode}"
then
  echo "datanode is not set!"
  exit 1
fi
if test -z "${datanode_dir}"
then
  echo "datanode_dir is not set!"
  exit 1
fi
if test -z "${namenode_dir}"
then
  echo "namenode_dir is not set!"
  exit 1
fi
if test -z "${hadoop_tmp_dir}"
then
  echo "hadoop_tmp_dir is not set!"
  exit 1
fi

#switch
cd "${tool_root_dir}" || exit 1
cmd=$1
case ${cmd} in
    deploy)
        echo "deploy hadoop"
        sh bin/deploy/deploy.sh
        #sh bin/deploy/sh_remote_excute.sh
        ;;
    start)
        echo "start hadoop"
        sh bin/switch/start.sh
        ;;
    stop)
        echo "stop hadoop"
        sh bin/switch/stop.sh
        ;;
    restart)
        echo "restart hadoop"
        sh bin/switch/restart.sh
        ;;
    format)
        echo "format and start hadoop"
        sh bin/deploy/format.sh
        ;;
    uninstall)
        echo "uninstall hadoop"
        sh bin/deploy/uninstall.sh
        ;;
    tar)
        echo "gen hadoop tarball"
        sh bin/tools/tarball.sh
        ;;
    *)
        echo "Usage:$(basename "${0}") deploy/start/stop/restart/format/uninstall/tar"
        exit 1 # Command to come out of the program with status 1
        ;;
esac
