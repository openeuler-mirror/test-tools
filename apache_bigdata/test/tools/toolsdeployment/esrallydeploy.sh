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

#rpm pkg name
git_rpm_name="git-2.21.0-1.el7.aarch64"
python3_rpm_name="python-3.7.5-1.el7.aarch64"
#esrally config
esrally_version=1.0.0
teams_version=6.1
tracks_version=6

tool_dir=$(cd "$(dirname "$0")/.." || exit 1;pwd)
depstools_dir=${tool_dir}/../../testtools/esDepsTools
tmp_dir=${depstools_dir}/tmp
git_dir=${depstools_dir}/git

function install_init()
{
   # 判断依赖工具是否存在，不存在，直接停止脚本
   if [ ! -d "${depstools_dir}" ]; then
     echo "[ERROR] Es Dependencies tool doesn't exist, please upload to ${depstools_dir}."
     exit
   fi

   # 判断依赖工具包安装中间路径Tmp是否存在，如果不存在则先创建
   mkdir -p "${tmp_dir}"

   echo "[INFO] install dependents yum packages: openssl glibc libffi sqlite zlib python openssl glibc perl"
   yum install -y openssl glibc libffi sqlite zlib python openssl glibc perl > /dev/null 2>&1
}

function check_install_rpm()
{
   pkg_name=$1
   #check if already install
   install_info=$(rpm -qa | grep "${pkg_name}")
   if [ -n "${install_info}"  ]; then
      echo "[INFO] rpm ${pkg_name} has been installed"
      return
   fi
   rpm -ivh "${depstools_dir}"/rpms/"${pkg_name}".rpm
}

function install_esrally
{
   if [ -f "$(command -v esrally)" ]; then
      if [ ! -L /usr/bin/esrally ]; then
         ln -s "$(command -v esrally)" /usr/bin/esrally
      fi
      echo "[INFO] esrally has been installed"
      return
   fi
   rally_version=$1
   tar -zxf "${depstools_dir}"/esrally/"${rally_version}"/esrally-dist-"${rally_version}".tar.gz -C "${tmp_dir}"
   bash "${tmp_dir}"/esrally-dist-"${rally_version}"/install.sh 2>&1
   if [ ! -L /usr/bin/esrally ]; then
      ln -s "$(command -v esrally)" /usr/bin/esrally
   fi
   #config
   esrally configure
   #clean
   rm -rf "${tmp_dir}"/esrally-dist-"${rally_version}"
}

function install_rally_tracks
{
   tracks_version=$1
   if [ -d ~/.rally/benchmarks/tracks ]; then
      echo "[INFO] rally tracks has been installed"
      return
   fi
   mkdir -p ~/.rally/benchmarks/tracks/default
   cd ~/.rally/benchmarks/tracks/default || exit 1
   git init
   unzip -d "${tmp_dir}"/  "${depstools_dir}"/rally-tracks/"${tracks_version}"/rally-tracks-"${tracks_version}".zip
   cp -rd "${tmp_dir}"/rally-tracks-"${tracks_version}"/geonames ~/.rally/benchmarks/tracks/default/
   git add geonames/.*
   git commit -m "init tracks"
   #modify tracks default url
   sed -i "s/https:\/\/github.com\/elastic\/rally-tracks/~\/.rally\/benchmarks\/tracks\/default/g" ~/.rally/rally.ini
   #back
   cd - || exit 1
   #clean
   rm -rf "${tmp_dir}"/rally-tracks-"${tracks_version}"
}

function install_rally_teams
{
   teams_version=$1
   if [ -d ~/.rally/benchmarks/teams ]; then
      echo "[INFO] rally teams has been installed"
      return
   fi
   mkdir -p ~/.rally/benchmarks/teams/default
   cd ~/.rally/benchmarks/teams/default || exit 1
   git init
   unzip -d "${tmp_dir}"/  "${depstools_dir}"/rally-teams/"$teams_version"/rally-teams-"${teams_version}".zip
   cp -rd "${tmp_dir}"/rally-teams-"${teams_version}"/cars  ~/.rally/benchmarks/teams/default/
   git add cars
   git commit -m "init teams"
   #modify teams default url
   sed -i "s/https:\/\/github.com\/elastic\/rally-teams/~\/.rally\/benchmarks\/teams\/default/g" ~/.rally/rally.ini
   #back
   cd - || exit 1
   #clean
   rm -rf "${tmp_dir}"/rally-teams-"${teams_version}"
}

function install_rally_data
{
  if [ -f ~/.rally/benchmarks/data/geonames/documents-2.json.bz2 ]; then
     echo "[INFO] rally data has been installed"
     return
  fi
  mkdir -p ~/.rally/benchmarks/data/geonames
  cp "${depstools_dir}"/rally-data/documents-2.json.bz2 ~/.rally/benchmarks/data/geonames/
}

function install_git
{
    git_get=$(git --version | awk '{print$3}' | sed "s/\.//g")
    git=${git_get}000
    if [ "${git:0:3}" -lt "190" ]; then
        echo -e "\E[1;36m[INFO]\E[0m git --version updata"
        yum -y install curl-devel expat-devel gettext-devel openssl-devel zlib-devel
        cd "${git_dir}" || exit 1
        cpu_name=$(lscpu | grep Architecture | awk '{print $2}')
        if [ ${cpu_name} == "aarch64" ];then
            git_v="git-1.9.5"
        else
            git_v="git-2.9.5"
        fi
        tar -zxvf ${git_v}.tar.gz
        cd ${git_v} || exit 1
        make configure
        ./configure --prefix=/usr/local/
        make -j8 && make install
        \cp -rf /usr/local/bin/git /usr/bin
        echo -e "\E[1;36m[INFO]\E[0m install git ok "
    else
        echo -e "\E[1;36m[INFO]\E[0m git --version check ok "
fi
}

#install require rpms
echo "[INFO] install init"
install_init
echo "[INFO] check rpm"
check_install_rpm ${git_rpm_name}
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
echo "[INFO] install rpm"
name=$(command -v python3)
if [[ -n "${name}" ]]; then
    echo "python3 已存在"

else
    check_install_rpm ${python3_rpm_name}
fi

#install esrally
echo "[INFO] install esrally"
install_esrally ${esrally_version}
echo "[INFO] install rally teams"
install_rally_teams "${teams_version}"
echo "[INFO] install rally tracks"
install_rally_tracks "${tracks_version}"
echo "[INFO] install rally data"
install_rally_data
echo "[INFO] install elastic search done!"
install_git
