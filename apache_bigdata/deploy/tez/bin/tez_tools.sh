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

if [ $# != 1 ] ; then
  echo "USAGE: $0 cmd"
  echo " e.g.: $0 deploy"
  exit 1;
fi

#check param
tool_root_dir=$(cd "$(dirname "$0")" || exit 1;cd .. || exit 1;pwd)
#source $tool_root_dir/bin/common/env.sh
source ${tool_root_dir}/conf/config

echo "version $tez_version"
if test -z "$tez_version"
then
  echo "tez_version is not set!"
  exit 1
fi
if test -z "$tez_dir"
then
  echo "tez_dir is not set!"
  exit 1
fi
if test -z "$hadoop_home"
then
  echo "hadoop_home is not set!"
  exit 1
fi

#switch
cd "${tool_root_dir}" || exit 1
cmd=$1
case ${cmd} in
   deploy)
     echo "deploy tez"
     sh bin/deploy/deploy.sh
     ;;
   start)
      echo "start tez"
      sh bin/switch/start.sh
      ;;
   stop)
      echo "stop tez"
      sh bin/switch/stop.sh
      ;;
   restart)
      echo "restart tez"
      sh bin/switch/restart.sh
      ;;
   uninstall)
      echo "uninstall tez"
      sh bin/deploy/uninstall.sh
      ;;
   tar)
      echo "gen tez tarball"
      sh bin/tools/tarball.sh
      ;;
   *)
      echo "Usage:$(basename "${0}") deploy/start/stop/restart/format/uninstall/tar"
      exit 1 # Command to come out of the program with status 1
      ;;
esac
