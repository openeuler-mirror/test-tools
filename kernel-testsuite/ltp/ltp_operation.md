一、准备环境<br/>
1.使用目标iso镜像文件安装测试环境。<br/>
2.拷贝ltp目录下start_ltp_test.sh等文件至目标机器,或通过如下路径下载 https://gitee.com/openeuler/test-tools.git<br/>

二、执行测试用例<br/>
sh start_ltp_test.sh 启动执行用例；包括安装依赖包，下载并编译ltp，运行用例。<br/>

*其中ltp所用版本参照如下：<br/>
kernel-4.19和kernel-5.10系列版本用ltp-20220121；<br/>
kernel-6.6系列版本用ltp-20240129;<br/>*

*ltp测试套执行方法如下：<br/>
./runltp #执行所有用例<br/>
./runltp -s casename #执行单个用例<br/>
./runltp -p -f configfile #执行一个模块用例<br/>*

三、结果分析<br/>
1.查询ltp的执行结果中的失败用例：grep FAIL results/LTP*.log,如果有失败的用例，再次用./runltp -s casename执行一次，如果再失败找开发分析，确认是问题提单跟踪。<br/>
2.使用grep casename ltp.log查询用例的执行日志记录，分析用例执行情况。<br/>
