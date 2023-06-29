#!/bin/bash

testItems=("Dhrystone 2 using register variables" "Double-Precision Whetstone" "Execl Throughput" "File Copy 1024 bufsize 2000 maxblocks" "File Copy 256 bufsize 500 maxblocks" "File Copy 4096 bufsize 8000 maxblocks" "Pipe Throughput" "Pipe-based Context Switching" "Process Creation" "Shell Scripts (1 concurrent)" "Shell Scripts (8 concurrent)" "System Call Overhead" "System Benchmarks Index Score")
cpu_cores=(1 `cat /proc/cpuinfo | grep "processor" |wc -l`)

declare -a var_1core
declare -a var_allcore
data_n=`ls unixbench_*.log | wc -l`
for i in $(seq $data_n);do
    for ((t=0;t<${#testItems[*]};t++))
    do
        var_1core[t]=`grep -A 29 "running ${cpu_cores[0]} parallel copy of tests" unixbench_$[$i-1].log |grep "${testItems[t]}" |tail -1 |awk '{print $NF}'`
    done
    echo "Index_Values_1core Dhrystone_2_using_register_variables Double-Precision_Whetstone Execl_Throughput File_Copy_1024_bufsize_2000_maxblocks File_Copy_256_bufsize_500_maxblocks File_Copy_4096_bufsize_8000_maxblocks Pipe_Throughput Pipe-based_Context_Switching Process_Creation Shell_Scripts_(1_concurrent) Shell_Scripts_(8_concurrent) System_Call_Overhead System_Benchmarks_Index_Score" >> unixbench${i}.txt
    echo "averge ${var_1core[*]}" >> unixbench${i}.txt
done

cat unixbench1.txt | head -1 >> unixbench.txt
txtname=`ls unixbench*.txt | grep -v unixbench.txt`
python ../../../../lib/datahandle.py $txtname >> unixbench.txt
rm -f ${txtname}

data_n=`ls unixbench_*.log | wc -l`
for i in $(seq $data_n);do
    for ((t=0;t<${#testItems[*]};t++))
    do
        var_allcore[t]=`grep -A 29 "running ${cpu_cores[1]} parallel copies of tests" unixbench_$[$i-1].log |grep "${testItems[t]}" |tail -1 |awk '{print $NF}'`
    done
    echo "Index_Values_${cpu_cores[1]}core Dhrystone_2_using_register_variables Double-Precision_Whetstone Execl_Throughput File_Copy_1024_bufsize_2000_maxblocks File_Copy_256_bufsize_500_maxblocks File_Copy_4096_bufsize_8000_maxblocks Pipe_Throughput Pipe-based_Context_Switching Process_Creation Shell_Scripts_(1_concurrent) Shell_Scripts_(8_concurrent) System_Call_Overhead System_Benchmarks_Index_Score" >> unixbench${i}.txt
    echo "averge ${var_allcore[*]}" >> unixbench${i}.txt
done

cat unixbench1.txt | head -1 >> unixbench.txt
txtname=`ls unixbench*.txt | grep -v unixbench.txt`
