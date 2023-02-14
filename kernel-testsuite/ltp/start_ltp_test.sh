#!/usr/bin/bash

set_yum_env(){
    echo 'sslverify=false' >>/etc/yum.conf
    cp openEuler.repo /etc/yum.repos.d/openEuler.repo
    ver=$(cat /etc/openEuler-latest | grep openeulerversion | awk -F= '{print $2}')
    sed -i "s/branch/${ver}/g" /etc/yum.repos.d/openEuler.repo    
    yum makecache
}

install_rpm(){
    yum install -y zlib zlib-devel bc httpd net-tools gcc-c++ m4 flex byacc bison keyutils-libs-devel lksctp-tools-devel xfsprogs-devel libacl-devel openssl-devel numactl-devel libaio-devel glibc-devel libcap-devel findutils libtirpc kernel-headers glibc-headers elfutils-libelf-devel patch numactl tar automake cmake time psmisc vim git make
    dnf update -y
    sed -i '$a set number' /etc/vimrc
    echo 'export LANG=en_US.UTF-8' >> /root/.bashrc
    source /root/.bashrc
    hostnamectl set-hostname localhost
}

compile_ltp(){
    cd /opt;
    if [ ! -d "ltp" ];then
        #until (test -e "ltp")
        #do
        #    git clone https://github.com/linux-test-project/ltp.git
        #done
        wget -c -t 30 https://github.com/linux-test-project/ltp/archive/refs/tags/20220121.zip
        unzip 20220121.zip && cd ltp-20220121
        make autotools
        ./configure
        make -j16
        make install
    fi
}

run_testcases(){
    cd /opt/ltp;
    ./runltp |tee ltp.log #默认执行全部，scenario_groups/default中配置调度文件
}

set_yum_env
install_rpm
compile_ltp
run_testcases
