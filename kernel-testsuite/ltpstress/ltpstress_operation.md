ltpstress测试操作方法:<br/>
1.下载所需版本ltp,wget -c https://github.com/linux-test-project/ltp/archive/refs/tags/20240129.zip<br/>

*其中ltp所用版本参照如下：<br/>
kernel-4.19和kernel-5.10系列版本用ltp-20220121；<br/>
kernel-6.6系列版本用ltp-20240129;<br/>*

2.从ltp-20180515版本获取ltpstress.sh脚本和stress.part文件至对应目录<br/>
cp ltpstress.sh ./ltp/testscripts/ltpstress.sh<br/>
cp stress.part1 ./ltp/runtest/stress.part1<br/>
cp stress.part2 ./ltp/runtest/stress.part2<br/>
cp stress.part3 ./ltp/runtest/stress.part3<br/>

3.编译ltp:<br/>
make autotools<br/>
./configure<br/>
make -j16<br/>
make install<br/>

4.启动执行ltpstress<br/>
使用默认参数：sh ./ltpstress.sh<br/>
也可指定参数：sh ./ltpstress.sh -n -m ${TOTALMEM} -t 168<br/>

*内存指定方法如下：<br/>
TOTALMEM=lscpu的核数x指定压力百分比x1024+512 #单位是M*

具体的操作脚本见run_ltpstress.sh<br/>
