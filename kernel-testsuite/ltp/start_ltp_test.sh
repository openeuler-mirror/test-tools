#!/usr/bin/bash
LTPVER="20240129"

install_rpm(){
    yum install -y zlib zlib-devel bc httpd net-tools gcc-c++ m4 flex byacc bison keyutils-libs-devel lksctp-tools-devel xfsprogs-devel libacl-devel openssl-devel numactl-devel libaio-devel glibc-devel libcap-devel findutils libtirpc kernel-headers glibc-headers elfutils-libelf-devel patch numactl tar automake cmake time psmisc vim git make
    dnf update -y
    echo 'export LANG=en_US.UTF-8' >> /root/.bashrc
    source /root/.bashrc
    hostnamectl set-hostname localhost
}

compile_ltp(){
    if [ ! -e "${LTPVER}.zip" ];then
        wget -c -t 30 https://github.com/linux-test-project/ltp/archive/refs/tags/${LTPVER}.zip
    fi
    #until (test -e "ltp")
    #do
    #    git clone -b ${LTPVER} https://github.com/linux-test-project/ltp.git
    #done
        
    unzip ${LTPVER}.zip && cd ltp-${LTPVER}
    make autotools
    ./configure
    make -j16
    make install
}

run_testcases(){
    cd /opt/ltp;
    ./runltp |tee ltp.log #默认执行全部，scenario_groups/default中配置调度文件
}

install_rpm
compile_ltp
run_testcases
