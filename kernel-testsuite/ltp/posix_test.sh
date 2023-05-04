#!/usr/bin/bash
yum install -y zlib zlib-devel bc httpd net-tools gcc-c++ m4 flex byacc bison keyutils-libs-devel lksctp-tools-devel xfsprogs-devel libacl-devel openssl-devel numactl-devel libaio-devel glibc-devel libcap-devel findutils libtirpc libtirpc-devel kernel-headers glibc-headers hwloc-devel patch numactl tar automake cmake time psmisc
echo 'export LANG=en_US.UTF-8' >> /root/.bashrc
source /root/.bashrc
hostnamectl set-hostname localhost
\cp ltp-20210927.zip /opt && cd /opt/
rm -rf ltp-20210927
unzip ltp-20210927.zip
cd ltp-20210927/testcases/open_posix_testsuite
make all
echo "----start All confromance test ----"
make conformance-test > /opt/posix_conformance_result.txt
pcnt=$(grep PASS /opt/posix_conformance_result.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
fcnt=$(grep FAIL /opt/posix_conformance_result.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
tcnt=$(grep TOTAL /opt/posix_conformance_result.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
echo "the success rate is:"
awk 'BEGIN{printf "%.3f%\n", ('$pcnt'/'$tcnt')*100}'
echo "---- End All confromance test ----"

echo "---- start Asynchronous I/O test ----"
cd bin
./run-all-posix-option-group-tests.sh AIO >/opt/AIO.txt
pcnt=$(grep PASS /opt/AIO.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
fcnt=$(grep FAIL /opt/AIO.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
tcnt=$(grep TOTAL /opt/AIO.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
echo "the success rate is:"
awk 'BEGIN{printf "%.3f%\n", ('$pcnt'/'$tcnt')*100}'
echo "---- End Asynchronous I/O test ----"
