!/bin/bash
#parse multiple hackbench result log with average
data_n=`ls hackbench_*.log | wc -l`
cnt=$data_n*10
for i in $(seq $data_n);do
	for j in $(seq 10);do
		 echo "Pipe_Process_Number 40 80 120 200 400 800" > hackbench$[$i-1]_$j.txt
		 var1=`cat hackbench_$[$i-1].log |grep -A 20 "pipe process num=1"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		 var2=`cat hackbench_$[$i-1].log |grep -A 20 "pipe process num=2"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		 var3=`cat hackbench_$[$i-1].log |grep -A 20 "pipe process num=3"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
	         var5=`cat hackbench_$[$i-1].log |grep -A 20 "pipe process num=5"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		 var10=`cat hackbench_$[$i-1].log |grep -A 20 "pipe process num=10"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
	         var20=`cat hackbench_$[$i-1].log |grep -A 20 "pipe process num=20"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		 echo "Time   $var1 $var2 $var3 $var5 $var10 $var20">>hackbench$[$i-1]_$j.txt
	done
done

cat hackbench0_1.txt | head -1 > hackbench.txt
txtname=`ls hackbench*.txt | grep -v hackbench.txt`
python ../../../../lib/datahandle.py $txtname >> hackbench.txt
rm -f ${txtname}


for i in $(seq $data_n);do
        for j in $(seq 10);do
                 echo "Socket_Process_Number 40 80 120 200 400 800" > hackbench$[$i-1]_$j.txt
                 var1=`cat hackbench_$[$i-1].log |grep -A 20 "socket process num=1"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var2=`cat hackbench_$[$i-1].log |grep -A 20 "socket process num=2"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var3=`cat hackbench_$[$i-1].log |grep -A 20 "socket process num=3"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var5=`cat hackbench_$[$i-1].log |grep -A 20 "socket process num=5"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var10=`cat hackbench_$[$i-1].log |grep -A 20 "socket process num=10"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var20=`cat hackbench_$[$i-1].log |grep -A 20 "socket process num=20"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 echo "Time   $var1 $var2 $var3 $var5 $var10 $var20">>hackbench$[$i-1]_$j.txt
        done
done
cat hackbench0_1.txt | head -1 >> hackbench.txt
txtname=`ls hackbench*.txt | grep -v hackbench.txt`
python ../../../../lib/datahandle.py $txtname >> hackbench.txt
rm -f ${txtname}

for i in $(seq $data_n);do
	for j in $(seq 10);do
		echo "Pipe_Thread_Number 40 80 120 200 400 800" > hackbench$[$i-1]_$j.txt
		var1=`cat hackbench_$[$i-1].log |grep -A 20 "pipe thread num=1"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		var2=`cat hackbench_$[$i-1].log |grep -A 20 "pipe thread num=2"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		var3=`cat hackbench_$[$i-1].log |grep -A 20 "pipe thread num=3"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		var5=`cat hackbench_$[$i-1].log |grep -A 20 "pipe thread num=5"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		var10=`cat hackbench_$[$i-1].log |grep -A 20 "pipe thread num=10"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		var20=`cat hackbench_$[$i-1].log |grep -A 20 "pipe thread num=20"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
		echo "Time   $var1 $var2 $var3 $var5 $var10 $var20">>hackbench$[$i-1]_$j.txt
	done
done

cat hackbench0_1.txt | head -1 >> hackbench.txt
txtname=`ls hackbench*.txt | grep -v hackbench.txt`
python ../../../../lib/datahandle.py $txtname >> hackbench.txt
rm -f ${txtname}


for i in $(seq $data_n);do
        for j in $(seq 10);do
                 echo "Socket_Thread_Number 40 80 120 200 400 800" > hackbench$[$i-1]_$j.txt
                 var1=`cat hackbench_$[$i-1].log |grep -A 20 "socket thread num=1"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var2=`cat hackbench_$[$i-1].log |grep -A 20 "socket thread num=2"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var3=`cat hackbench_$[$i-1].log |grep -A 20 "socket thread num=3"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var5=`cat hackbench_$[$i-1].log |grep -A 20 "socket thread num=5"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var10=`cat hackbench_$[$i-1].log |grep -A 20 "socket thread num=10"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 var20=`cat hackbench_$[$i-1].log |grep -A 20 "socket thread num=20"  | grep ^Time | sed 's/^Time: //g' | head -$j | tail -1`
                 echo "Time   $var1 $var2 $var3 $var5 $var10 $var20">>hackbench$[$i-1]_$j.txt
        done
done
cat hackbench0_1.txt | head -1 >> hackbench.txt
