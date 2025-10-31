#!/usr/bin/bash
yum install -y zlib zlib-devel bc httpd net-tools gcc-c++ m4 flex byacc bison keyutils-libs-devel lksctp-tools-devel xfsprogs-devel libacl-devel openssl-devel numactl-devel libaio-devel glibc-devel libcap-devel findutils libtirpc libtirpc-devel kernel-headers glibc-headers hwloc-devel patch numactl tar automake cmake time psmisc
echo 'export LANG=en_US.UTF-8' >> /root/.bashrc
source /root/.bashrc
hostnamectl set-hostname localhost
LTPVER="20250930"
if [ ! -e "ltp-${LTPVER}.zip" ];then
        wget -c -t 30 https://github.com/linux-test-project/ltp/archive/refs/tags/${LTPVER}.zip
fi
cp ltp-${LTPVER}.zip /opt && cd /opt/
rm -rf ltp-${LTPVER}
unzip ltp-${LTPVER}.zip
cd ltp-${LTPVER}/testcases/open_posix_testsuite
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

pcnt=$(grep -c -E "^Test PASSED$" /opt/AIO.txt)
fcnt=$(grep -c -E "^FAIL:*" /opt/AIO.txt)
tcnt=$((count_passed + count_failed))

if [ $total_tests -eq 0 ]; then
    echo "未找到符合要求的测试结果"
    echo "支持的格式:"
    echo "  Test PASSED"
    echo "  FAIL"
    exit 1
fi

success_rate=$(echo "scale=2; ($pcnt / $total_tests)*100" | bc)

echo "=== 测试结果统计 ==="
echo "通过测试: $pcnt"
echo "失败测试: $fcnt"
echo "总测试数: $tcnt"
echo "成功率: $success_rate%"

#pcnt=$(grep PASS /opt/AIO.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
#fcnt=$(grep FAIL /opt/AIO.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
#tcnt=$(grep TOTAL /opt/AIO.txt | awk '{print $2}' | awk '{sum +=$1}; END {print sum}')
#echo "the success rate is:"
#awk 'BEGIN{printf "%.3f%\n", ('$pcnt'/'$tcnt')*100}'
echo "---- End Asynchronous I/O test ----"
