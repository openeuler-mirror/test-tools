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
tool_root_dir=$(cd "$(dirname "$0")"||exit 1;cd ..||exit 1;pwd)
source "${tool_root_dir}/conf/config"

echo "version ${spark_version}"
if test -z "${spark_version}"
then
  echo "spark_version is not set!"
  exit 1
fi
if test -z "${hadoop_home}"
then
  echo "hadoop_home is not set!"
  exit 1
fi
if test -z "${spark_client}"
then
  echo "spark_client is not set!"
  exit 1
fi
if test -z "${scala_dir}"
then
  echo "scala_dir is not set!"
  exit 1
fi
if test -z "${spark_dir}"
then
  echo "spark_dir is not set!"
  exit 1
fi
if test -z "${scala_version}"
then
  echo "scala_version is not set!"
  exit 1
fi
if test -z "${spark_log_dir}"
then
  echo "spark_log_dir is not set!"
  exit 1
fi

#switch
cd "${tool_root_dir}"||exit 1
cmd=$1
case ${cmd} in
   deploy)
     echo "deploy spark"
     sh bin/deploy/deploy.sh
     ;;
   start)
      echo "start spark history server"
      sh bin/switch/start.sh
      ;;
   stop)
      echo "stop spark history server"
      sh bin/switch/stop.sh
      ;;
   restart)
      echo "restart spark history server"
      sh bin/switch/restart.sh
      ;;
   uninstall)
      echo "uninstall spark"
      sh bin/deploy/uninstall.sh
      ;;
   tar)
      echo "gen hadoop tarball"
      sh bin/tools/tarball.sh
      ;;
   *)
      echo "Usage:$(basename "${0}") deploy/start/stop/restart/uninstall/tar"
      exit 1 # Command to come out of the program with status 1
      ;;
esac
