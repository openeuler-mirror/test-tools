#/bin/bash

WORKDIR=$(cd `dirname $0`;pwd)
NEWVER="20240129"
OLDVER="20180515"

download_ltp_pkg(){
    yum install -y vim tar git make automake gcc pkgconf autoconf bison flex m4 kernel-headers glibc-headers clang findutils libtirpc libtirpc-devel pkg-config

    if [ ! -e "${NEWVER}.zip" ];then
        wget -c -t 30 https://github.com/linux-test-project/ltp/archive/refs/tags/${NEWVER}.zip
    fi

    if [ ! -e "${OLDVER}.zip" ];then
        wget -c -t 10 https://github.com/linux-test-project/ltp/archive/refs/tags/${OLDVER}.zip
    fi
    unzip ${OLDVER}.zip
    unzip ${NEWVER}.zip
    cp ltp-${OLDVER}/runtest/stress.part* ltp-${NEWVER}/runtest
    cp ltp-${OLDVER}/testscripts/ltpstress.sh ltp-${NEWVER}/testscripts    
}

compile_ltp(){
    cd $WORKDIR/ltp-${NEWVER}
    make autotools
    ./configure
    make -j16
    make install
}

run_ltpstress(){
    cd /opt/ltp/testscripts;
    CPU_NUM=$(lscpu | grep -E "^CPU:|^CPU\(s\):" | awk '{print $2}')
    CORE_NUM=$(echo "scale=0;$CPU_NUM*0.7" | bc)
    TOTALMEM=$((${CORE_NUM%.*} * 1024 + 512))
    sh ltpstress.sh -n -p -m ${TOTALMEM} -t 168 
}

download_ltp_pkg
compile_ltp
run_ltpstress
