ltpstress测试操作方法:<br/>
1.下载ltp的最新版本,git clone -b 20220121 https://github.com/linux-test-project/ltp.git<br/>
或者wget https://github.com/linux-test-project/ltp/archive/refs/tags/20220121.zip<br/>

2.从ltp-20280515版本取ltpstress.sh脚本和stress.part文件至对应目录<br/>
cp ltpstress.sh ./ltp/testscripts/ltpstress.sh<br/>
cp stress.part1 ./ltp/runtest/stress.part1<br/>
cp stress.part2 ./ltp/runtest/stress.part2<br/>
cp stress.part3 ./ltp/runtest/stress.part3<br/>

3.编译ltp:<br/>
yum install -y automake<br/>
make autotools<br/>
./configure<br/>
make -j16<br/>
make install<br/>

4.启动执行ltpstress<br/>
sh ./ltp/testscripts/ltpstress.sh -n -m 1024 -t 24<br/>
也可以使用默认参数sh ./ltp/testscripts/ltpstress.sh<br/>

具体的操作脚本见run_ltpstress.sh<br/>
