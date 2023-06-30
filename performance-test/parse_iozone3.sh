#!/bin/bash
arch=$(uname -m)
# #parse multiple iozone result log with average
data_n=`ls iozone3_*.log | wc -l`
if [ $arch = "aarch64" ];then
	#Write---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "write_blocksize_16m 512g 256g 128g" > iozone3$i.txt
	var1=`sed -n '36p' iozone3_$[$i-1].log | awk '{print $3}'`
	var2=`sed -n '91p' iozone3_$[$i-1].log | awk '{print $3}'`
	var3=`sed -n '146p' iozone3_$[$i-1].log | awk '{print $3}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $3}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $3}'`
	echo "Write $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 > iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#ReWrite---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "rewrite_blocksize_16m 512g 256g 128g" > iozone3$i.txt
	var1=`sed -n '36p' iozone3_$[$i-1].log | awk '{print $4}'`
	var2=`sed -n '91p' iozone3_$[$i-1].log | awk '{print $4}'`
	var3=`sed -n '146p' iozone3_$[$i-1].log | awk '{print $4}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $4}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $4}'`
	echo "ReWrite $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 >> iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#Read---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "read_blocksize_16m 512g 256g 128g" > iozone3$i.txt
	var1=`sed -n '36p' iozone3_$[$i-1].log | awk '{print $5}'`
	var2=`sed -n '91p' iozone3_$[$i-1].log | awk '{print $5}'`
	var3=`sed -n '146p' iozone3_$[$i-1].log | awk '{print $5}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $5}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $5}'`
	echo "Read $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 >> iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#ReRead---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "reread_blocksize_16m 512g 256g 128g" > iozone3$i.txt
	var1=`sed -n '36p' iozone3_$[$i-1].log | awk '{print $6}'`
	var2=`sed -n '91p' iozone3_$[$i-1].log | awk '{print $6}'`
	var3=`sed -n '146p' iozone3_$[$i-1].log | awk '{print $6}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $6}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $6}'`
	echo "ReRead $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 >> iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#Random_Read---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "randread_blocksize_16m 512g 256g 128g" > iozone3$i.txt
	var1=`sed -n '36p' iozone3_$[$i-1].log | awk '{print $7}'`
	var2=`sed -n '91p' iozone3_$[$i-1].log | awk '{print $7}'`
	var3=`sed -n '146p' iozone3_$[$i-1].log | awk '{print $7}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $7}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $7}'`
	echo "Random_Read $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 >> iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#Random_Write---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "randwrite_blocksize_16m 512g 256g 128g" > iozone3$i.txt
	var1=`sed -n '36p' iozone3_$[$i-1].log | awk '{print $8}'`
	var2=`sed -n '91p' iozone3_$[$i-1].log | awk '{print $8}'`
	var3=`sed -n '146p' iozone3_$[$i-1].log | awk '{print $8}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $8}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $8}'`
	echo "RANDOM_WRITE $var1 $var2 $var3" >> iozone3$i.txt
	done
else
	#Write---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "write_blocksize_16m 768g 384g 192g" > iozone3$i.txt
	var1=`sed -n '52p' iozone3_$[$i-1].log | awk '{print $3}'`
	var2=`sed -n '107p' iozone3_$[$i-1].log | awk '{print $3}'`
	var3=`sed -n '162p' iozone3_$[$i-1].log | awk '{print $3}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $3}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $3}'`
	echo "Write $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 > iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#ReWrite---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "rewrite_blocksize_16m 768g 384g 192g" > iozone3$i.txt
	var1=`sed -n '52p' iozone3_$[$i-1].log | awk '{print $4}'`
	var2=`sed -n '107p' iozone3_$[$i-1].log | awk '{print $4}'`
	var3=`sed -n '162p' iozone3_$[$i-1].log | awk '{print $4}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $4}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $4}'`
	echo "ReWrite $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 >> iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#Read---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "read_blocksize_16m 768g 384g 192g" > iozone3$i.txt
	var1=`sed -n '52p' iozone3_$[$i-1].log | awk '{print $5}'`
	var2=`sed -n '107p' iozone3_$[$i-1].log | awk '{print $5}'`
	var3=`sed -n '162p' iozone3_$[$i-1].log | awk '{print $5}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $5}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $5}'`
	echo "Read $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 >> iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#ReRead---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "reread_blocksize_16m 768g 384g 192g" > iozone3$i.txt
	var1=`sed -n '52p' iozone3_$[$i-1].log | awk '{print $6}'`
	var2=`sed -n '107p' iozone3_$[$i-1].log | awk '{print $6}'`
	var3=`sed -n '162p' iozone3_$[$i-1].log | awk '{print $6}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $6}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $6}'`
	echo "ReRead $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 >> iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#Random_Read---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "randread_blocksize_16m 768g 384g 192g" > iozone3$i.txt
	var1=`sed -n '52p' iozone3_$[$i-1].log | awk '{print $7}'`
	var2=`sed -n '107p' iozone3_$[$i-1].log | awk '{print $7}'`
	var3=`sed -n '162p' iozone3_$[$i-1].log | awk '{print $7}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $7}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $7}'`
	echo "Random_Read $var1 $var2 $var3" >> iozone3$i.txt
	done
	cat iozone31.txt | head -1 >> iozone3.txt
	txtname=`ls iozone3*.txt | grep -v iozone3.txt`
	python ../../../../lib/datahandle.py $txtname >> iozone3.txt
	rm -f ${txtname}
	#Random_Write---------------------------------------------------------
	for i in $(seq $data_n);do
	echo "randwrite_blocksize_16m 768g 384g 192g" > iozone3$i.txt
	var1=`sed -n '52p' iozone3_$[$i-1].log | awk '{print $8}'`
	var2=`sed -n '107p' iozone3_$[$i-1].log | awk '{print $8}'`
	var3=`sed -n '162p' iozone3_$[$i-1].log | awk '{print $8}'`
	var4=`sed -n '114p' iozone3_$[$i-1].log | awk '{print $8}'`
	var5=`sed -n '143p' iozone3_$[$i-1].log | awk '{print $8}'`
	echo "RANDOM_WRITE $var1 $var2 $var3" >> iozone3$i.txt
	done
fi
cat iozone31.txt | head -1 >> iozone3.txt
txtname=`ls iozone3*.txt | grep -v iozone3.txt`
