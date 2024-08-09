#!/usr/bin/bash

# Copyright (c) [2021] Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# ##################################
# @CaseName  :   common_lib.sh
# @Author    :   zengcongwei/zhujinlong
# @Contact   :   735811396@qq.com
# @Date      :   2021/11/11
# @Version   :   V2.0
# @Desc      :   mock rpmbuild public libraries
# ##################################

require_pkgs="createrepo_c systemd-container tar python3-babel python3-markupsafe python3-chardet python3-idna python3-urllib3 python3-requests usermode distribution-gpg-keys python3-jinja2 python3-pyroute2 python3-templated-dictionary"
require_rpms="mock-3.5-2.fc38 mock-core-configs-38.3-1.fc38 mock-filesystem-3.5-2.fc38"
require_rpms_PATH="../common/rpms"
test -d $require_rpms_PATH || mkdir $require_rpms_PATH
wget https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/38/Everything/aarch64/os/Packages/m/mock-3.5-2.fc38.noarch.rpm -O "$require_rpms_PATH"/mock-3.5-2.fc38.noarch.rpm
wget https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/38/Everything/aarch64/os/Packages/m/mock-core-configs-38.3-1.fc38.noarch.rpm -O "$require_rpms_PATH"/mock-core-configs-38.3-1.fc38.noarch.rpm
wget https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/38/Everything/aarch64/os/Packages/m/mock-filesystem-3.5-2.fc38.noarch.rpm -O "$require_rpms_PATH"/mock-filesystem-3.5-2.fc38.noarch.rpm

function INSTALL_MOCK() {
    dnf install -y ${require_pkgs}
    rpm -ivh "$require_rpms_PATH"/*
    usermod -a -G mock root
}

function BUILD_PKG() {
    pkg=$1
    config_file=${2-0}
    build_user=$3
    yumdownloader --source --downloaddir=/tmp/srcrpms "$pkg"
    #add mockbuild user
    useradd ${build_user}
    #add user into mock group
    usermod -a -G mock ${build_user}
    pkg_name=$(ls /tmp/srcrpms/ | grep "^${pkg}.[0-9]")
    chmod 755 -R "$config_file" /tmp/srcrpms/
    (
        if ! su - ${build_user} -c "mock -q -r ${config_file} /tmp/srcrpms/${pkg_name}"; then
            echo "$pkg" >>fail_pkg.log
	    mkdir -p /home/mock/logs/${pkg}
	    cp -r /var/lib/mock/${pkg}_build_env/result /home/mock/logs/${pkg}
        fi
        su - ${build_user} -c "mock -r /tmp/${pkg}_build-$(arch).cfg --clean"
        userdel -r ${build_user}
        rm -rf "$config_file" "/tmp/srcrpms/${pkg_name}"
    ) &
}

function REMOVE_MOCK() {
    systemctl stop squid
    rpm -e ${require_rpms}
    dnf remove -y ${require_pkgs}
    rm -rf ${require_rpms_PATH}
}
