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
yum install python2 openssl-devel -y

rpm -ivh liboath-2.6.6-2.fc34.$(arch).rpm --force --nodeps
rpm -ivh python3-3.7.9-18.oe1.$(arch).rpm --force --nodeps
rpm -ivh libffi-3.3-8.oe1.$(arch).rpm --force --nodeps
rpm -ivh python2-cherrypy-3.5.0-13.oe1.noarch.rpm --force --nodeps

cat > /etc/yum.repos.d/sp3_everything.repo <<EOF
[sp3_everything]
name=sp3_everything
baseurl=http://121.36.84.172/dailybuild/openEuler-20.03-LTS-SP3/test_openeuler-2022-01-01-11-20-51/everything/$(arch)
gpgcheck=0
enable=1
priority=2

EOF


}



check()
{
  echo "adapter success"
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
