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

cat > /etc/yum.repos.d/fedora.repo << EOF
[arch_fedora_online]
name=arch_fedora
baseurl=https://repo.huaweicloud.com/fedora/releases/34/Everything/$(arch)/os/
enabled=1
gpgcheck=0
priority=3

EOF

rpm -ivh --force --nodeps rpms/python3-libs-3.9.2-1.fc34.$(arch).rpm
rpm -ivh --force --nodeps rpms/python3-lxml-4.6.2-2.fc34.$(arch).rpm
rpm -ivh --force --nodeps rpms/python3-cffi-1.14.5-1.fc34.$(arch).rpm
rpm -ivh --force --nodeps rpms/python3-markupsafe-1.1.1-10.fc34.$(arch).rpm
rpm -ivh --force --nodeps rpms/python3-cryptography-3.4.6-1.fc34.$(arch).rpm

rpm -ivh --force --nodeps rpms/python3-six-1.15.0-5.fc34.noarch.rpm
rpm -ivh --force --nodeps rpms/python3-idna-2.10-3.fc34.noarch.rpm
rpm -ivh --force --nodeps rpms/python3-requests-2.25.1-1.fc34.noarch.rpm

yum install redhat-rpm-config libffi-devel python2-devel -y

}



check()
{
flag=0
ls  /etc/yum.repos.d/fedora.repo &>/dev/null
if [ $? -ne  0 ];then
    flag=1
    echo "fedora.repo  config failed"
fi

if [ ${flag} -eq  0 ];then
  echo "adapter success"
else
  echo "adapter failed"
fi
}

install_bcache_tools()
{
  cd ${current_path}

  yum install -y tar libblkid-devel gcc libsmartcols-devel
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
