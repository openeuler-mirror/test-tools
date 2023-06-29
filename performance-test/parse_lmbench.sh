#!/bin/bash
# parse multiple lmbench result log with average
data_n=`ls lmbench3_*.log | wc -l`
#---------------------------------------------------------------------------------------------- 
for i in $(seq $data_n);do
echo "Processor_Processes  null_call null_io stat open_close slct_TCP sig_inst sig_hndl fork_proc exec_proc sh_proc" > lmbench3_$[$i-1].tmp
var1=`grep -w "Simple syscall" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var1 ];then var1=0;fi
var2=`grep -w "Simple read" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var2 ];then var2=0;fi
var3=`grep -w "Simple write" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var3 ];then var3=0;fi
var=`echo "scale=4;($var2+$var3)/2"|bc`
var4=`grep -w "Simple stat" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var4 ];then var4=0;fi
var5=`grep -w "Simple open/close" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var5 ];then var5=0;fi
var6=`grep -w "Select on 100 tcp fd's" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var6 ];then var6=0;fi
var7=`grep -w "Signal handler installation" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var7 ];then var7=0;fi
var8=`grep -w "Signal handler overhead" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var8 ];then var8=0;fi
var9=`grep -w "Process fork+exit" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var9 ];then var9=0;fi
var10=`grep -w "Process fork+execve" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var10 ];then var10=0;fi
var11=`grep -w "Process fork+/bin/sh" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var11 ];then var11=0;fi 
echo "Value $var1 $var $var4 $var5 $var6 $var7 $var8 $var9 $var10 $var11">>lmbench3_$[$i-1].tmp
#----------------------------------------------------------------------------------------------                                                                                                                   
echo "Context_switching_ctxsw 2p/0K 2p/16K 2p/64K 8p/16K 8p/64K 16p/16K 16p/64K " >> lmbench3_$[$i-1].tmp
var1=`grep -A 1 "size=0k ovr=" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var1 ];then var1=0;fi
var2=`grep -A 1 "size=16k ovr=" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var2 ];then var2=0;fi
var3=`grep -A 1 "size=64k ovr=" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var3 ];then var3=0;fi
var4=`grep -A 3 "size=16k ovr=" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var4 ];then var4=0;fi
var5=`grep -A 3 "size=64k ovr=" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var5 ];then var5=0;fi
var6=`grep -A 4 "size=16k ovr=" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var6 ];then var6=0;fi 
var7=`grep -A 4 "size=64k ovr=" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var7 ];then var7=0;fi 
echo "Value $var1 $var2 $var3 $var4 $var5 $var6 $var7 ">>lmbench3_$[$i-1].tmp
#----------------------------------------------------------------------------------------------
echo "Local_latencies Pipe AF_UNIX UDP  RPC/UDP TCP RPC/TCP TCP_conn " >> lmbench3_$[$i-1].tmp
var1=`grep -w "Pipe latency" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`       
if [ -z $var1 ];then var1=0;fi
var2=`grep -w "AF_UNIX sock stream latency" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`               
if [ -z $var2 ];then var2=0;fi
var3=`grep -w "UDP latency using localhost" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var3 ];then var3=0;fi
var4=`grep -w "RPC/udp latency using localhost" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var4 ];then var4=0;fi
var5=`grep -w "TCP latency using localhost" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var5 ];then var5=0;fi
var6=`grep -w "RPC/tcp latency using localhost" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var6 ];then var6=0;fi
var7=`grep -w "TCP/IP connection" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var7 ];then var7=0;fi
echo "Value $var1 $var2 $var3 $var4 $var5 $var6 $var7 ">>lmbench3_$[$i-1].tmp
#----------------------------------------------------------------------------------------------
#echo "File_&_VM_latencies 0K_File_Create 0K_File_Delete 10K_File_Create 10K_File_Delete Mmap_Latency Prot_Fault Page_Fault 100fd_selct" >> $2
echo "File_&_VM_latencies 0K_File_Create 0K_File_Delete 10K_File_Create 10K_File_Delete Mmap_Latency Prot_Fault Page_Fault 100fd_selct" >> lmbench3_$[$i-1].tmp
var1=`grep -A 1 "File system latency" lmbench3_$[$i-1].log|awk '{print $3}'|grep -Eo [0-9]+\.[0-9]+`
var1=$(echo "scale=2; 1000000 / $var1" | bc)
if [ -z $var1 ];then var1=0;fi
var2=`grep -A 1 "File system latency" lmbench3_$[$i-1].log|awk '{print $4}'|grep -Eo [0-9]+\.[0-9]+`
var2=$(echo "scale=2; 1000000 / $var2" | bc)
if [ -z $var2 ];then var2=0;fi
var3=`grep -A 4 "File system latency" lmbench3_$[$i-1].log|tail -1|awk '{print $3}'|grep -Eo [0-9]+\.[0-9]+`
var3=$(echo "scale=2; 1000000 / $var3" | bc)
if [ -z $var3 ];then var3=0;fi
var4=`grep -A 4 "File system latency" lmbench3_$[$i-1].log|tail -1|awk '{print $4}'|grep -Eo [0-9]+\.[0-9]+`
var4=$(echo "scale=2; 1000000 / $var4" | bc)
if [ -z $var4 ];then var4=0;fi
var5=`grep -A 11 "mappings" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var5 ];then var5=0;fi
var6=`grep -w "Protection fault" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var6 ];then var6=0;fi
var7=`grep -w "Pagefaults on /var/tmp/XXX" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var7 ];then var7=0;fi
var8=`grep -w "Select on 100 fd's" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var8 ];then var8=0;fi
echo "Value $var1 $var2 $var3 $var4 $var5 $var6 $var7 $var8">>lmbench3_$[$i-1].tmp
#----------------------------------------------------------------------------------------------
echo "Local_bandwidths Pipe AF_UNIX TCP File_reread Mmap_reread Bcopy(libc) Bcopy(hand) Mem_read Mem_write" >> lmbench3_$[$i-1].tmp
var1=`grep -w "Pipe bandwidth" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var1 ];then var1=0;fi
var2=`grep -w "AF_UNIX sock stream bandwidth" lmbench3_$[$i-1].log|awk -F ':' '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var2 ];then var2=0;fi
var3=`grep -A 8 "Socket bandwidth using localhost" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var3 ];then var3=0;fi
var4=`grep -A 21 "\"read bandwidth" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var4 ];then var4=0;fi
var5=`grep -A 21 "Mmap read bandwidth" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var5 ];then var5=0;fi
var6=`grep -A 20 "libc bcopy unaligned" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var6 ];then var6=0;fi
var7=`grep -A 20 "unrolled bcopy unaligned" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var7 ];then var7=0;fi
var8=`grep -A 21 "Memory read bandwidth" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var8 ];then var8=0;fi
var9=`grep -A 21 "Memory write bandwidth" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var9 ];then var9=0;fi
echo "Value $var1 $var2 $var3 $var4 $var5 $var6 $var7 $var8 $var9">>lmbench3_$[$i-1].tmp
#----------------------------------------------------------------------------------------------
echo "Memory_latencies  L1_$ L2_$ Main_mem Rand_mem " >> lmbench3_$[$i-1].tmp
var1=`grep -A 2 "\"stride=128" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var1 ];then var1=0;fi
var2=`grep -A 35 "\"stride=128" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var2 ];then var2=0;fi
var3=`grep -A 131 "\"stride=128" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var3 ];then var3=0;fi
var4=`grep -A 132 "Random load latency" lmbench3_$[$i-1].log|tail -1|awk '{print $2}'|grep -Eo [0-9]+\.[0-9]+`
if [ -z $var4 ];then var4=0;fi
echo "Value $var1 $var2 $var3 $var4 ">>lmbench3_$[$i-1].tmp
done
#----------------------------------------------------------------------------------------------
#data handle
#----------------------------------------------------------------------------------------------
for i in $(seq $data_n);do
cat lmbench3_$[$i-1].tmp|head -2>lmbench3$i.txt
done
cat lmbench31.txt | head -1 > lmbench3.txt
txtname=`ls lmbench3*.txt | grep -v lmbench3.txt`
