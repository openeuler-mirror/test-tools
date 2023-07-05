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
rpm -ivh libffi-3.1-28.fc34.$(arch).rpm --force --nodeps
rpm -ivh openssl-libs-1.0.2k-19.el7.$(arch).rpm --force --nodeps
rpm -ivh redhat-rpm-config-182-1.fc34.noarch.rpm --force --nodeps

yum remove -y expect nfs-utils-help dhcp
yum install -y tar python2
# snappy adapter
rpm -e snappy --nodeps
rpm -ivh snappy-1.1.8-5.fc34.$(arch).rpm --force --nodeps

# install pip
tar -xzf pip-9.0.1.tar.gz
cd pip-9.0.1/setuptools-36.6.0/
python2 setup.py install
cd ..
python2 setup.py install
yum remove -y mkpasswd python3-sssd
}

install_bcache_tools()
{
  cd ${current_path}
  yum install -y tar libblkid-devel gcc make
  tar -xzf bcache-tools-1.1.tar.gz
  cd bcache-tools-1.1
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

check()
{
flag=0
rpm -qa|grep libffi-3.1-28.fc34 &>/dev/null
if [ $? -ne  0 ];then
    flag=1
    echo "libffi-3.1-28.fc34 install failed"
fi

rpm -qa|grep openssl-libs-1.0.2k-19.el7 &>/dev/null
if [ $? -ne  0 ];then
    flag=1
    echo "openssl-libs-1.0.2k-19.el7 install failed"
fi
pip2 -V &>/dev/null
if [ $? -ne  0 ];then
    flag=1
    echo "pip2 install failed"
fi


if [ ${flag} -eq  0 ];then
  echo "adapter success"
else
  echo "adapter failed"
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
