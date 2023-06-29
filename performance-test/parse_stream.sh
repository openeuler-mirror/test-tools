#!/bin/bash

cpu_cores=(1 `cat /proc/cpuinfo | grep "processor" |wc -l`)

# 单核结果处理
data_n=`ls stream_*.log | wc -l`
for i in $(seq $data_n);do
	grep -A 18 "Number of Threads counted = ${cpu_cores[0]}" stream_$[$i-1].log |grep "Copy" -A 3|awk -F ':' '{printf $1 " " $2 "\n"}'|awk -F ' ' '{printf $1 " " $2 "\n"}' > log.txt
	echo "${cpu_cores[0]}_Core" `awk -F ' ' '{printf $1 " "}' log.txt` >> stream$i.txt
	echo "${cpu_cores[0]}_Core" `awk -F ' ' '{printf $2 " "}' log.txt` >> stream$i.txt
	rm -f log.txt
done

cat stream1.txt | head -1 >> stream.txt


# 多核结果处理
data_n=`ls stream_*.log | wc -l`
for i in $(seq $data_n);do
	grep -A 18 "Number of Threads counted = ${cpu_cores[1]}" stream_$[$i-1].log |grep "Copy" -A 3|awk -F ':' '{printf $1 " " $2 "\n"}'|awk -F ' ' '{printf $1 " " $2 "\n"}' > log.txt
	echo "${cpu_cores[1]}_Core" `awk -F ' ' '{printf $1 " "}' log.txt` >> stream$i.txt
	echo "${cpu_cores[1]}_Core" `awk -F ' ' '{printf $2 " "}' log.txt` >> stream$i.txt
	rm -f log.txt
done

cat stream1.txt | head -1 >> stream.txt
