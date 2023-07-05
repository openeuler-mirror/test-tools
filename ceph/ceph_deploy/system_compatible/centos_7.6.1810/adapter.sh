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
current_path=$(cd $(dirname $0)/..|exit 1; pwd)
option=$1

run()
{
cd ${current_path}
echo not adapter
}



check()
{
  echo "adapter success"
}

install_bcache_tools()
{
  cd ${current_path}
  yum install -y tar libblkid-devel gcc
  tar -xzf bcache-tools-1.0.8.tar.gz
  cd bcache-tools-1.0.8
  make
  make install
  # check
  command -v make-bcache
  if [ $? -eq 0 ];then
      echo "install bcache-tools success"
  else
      echo "install bcache-tools failed"
  fi

}


case "${option}" in
    run)
      run
      ;;
    check)
      check
      ;;
      bcache)
      install_bcache_tools
      ;;
    *)
      echo "Usage: bash ${0##*/} run|check|bcache"
      exit 1
      ;;
esac
