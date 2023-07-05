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
root_path=$(cd $(dirname $0)/../||exit 1;pwd)
source ${root_path}/conf/cluster_info.cfg
source ${root_path}/conf/fio.cfg
source ${root_path}/bin/lib.sh


usage()
{
 echo "Usage: $0 pre|clean"
 exit 1
}



case $1 in
pre)
  # check install fio
  install_fio
  # create image
  create_images
  # pg balance
  pg_balance
  ;;
clean)
  delete_pool
  ;;
*)
  usage
  ;;
esac


