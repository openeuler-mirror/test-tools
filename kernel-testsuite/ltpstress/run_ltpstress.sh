#/bin/bash

WORKDIR=`pwd`
OLDVER="20180515"

download_ltp_pkg(){
    yum install -y vim tar git make automake gcc pkgconf autoconf bison flex m4 kernel-headers glibc-headers clang findutils libtirpc libtirpc-devel pkg-config

    if [ ! -d "ltp" ];then
        until(test -e "ltp")
        do
            git clone https://github.com/linux-test-project/ltp.git
        done
    fi

    #select ltpstress.sh and stress.part* file to newer ltp package
    until(test -e "${OLDVER}.zip")
    do
        wget -c -t 10 https://github.com/linux-test-project/ltp/archive/refs/tags/${OLDVER}.zip
    done
    unzip ${OLDVER}.zip
    cp ltp-${OLDVER}/runtest/stress.part* ltp/runtest/
    cp ltp-${OLDVER}/testscripts/ltpstress.sh ltp/testscripts/
    rm -rf /${WORKDIR}/ltp-${OLDVER}
}

compile_ltp(){
    cd $WORKDIR/ltp
    make autotools
    ./configure
    make -j16
    make install
}

run_ltpstress(){
    cd /opt/ltp/testscripts;
    sh ltpstress.sh -n -m 512 -t 24
}

download_ltp_pkg
compile_ltp
run_ltpstress
