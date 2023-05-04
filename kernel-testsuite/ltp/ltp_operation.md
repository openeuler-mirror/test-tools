1.使用iso镜像文件安装机器。<br/>
2.拷贝ltp目录下open*.repo和start_ltp_test.sh等至目标机器/home目录,或者直接下载 https://gitee.com/hanson_fang/ltpstress-for-openeuler.git<br/>
3.sh start_ltp_test.sh 启动执行：包括配置yum源，安装依赖包，编译ltp，运行用例<br/>
4.分析ltp的执行结果：grep FAIL results/LTP*.log,如果有失败的用例，再次用./runltp -s casename执行一次，如果再失败找开发分析，确认是问题提单跟踪。<br/>
5.使用casename在ltp.log中查询具体用例的执行记录，分析用例执行情况	<br/>
6.备份执行产生的相关日志至蓝云机器，如：scp /opt/ltp/results/LTP*.log xxx@172.168.131.217:/data/*/xxx/<br/>

