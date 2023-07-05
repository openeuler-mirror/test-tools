#!/bin/bash
# Copyright (c) 2023. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   hekeming
# @Contact   :   hk16897@126.com
# @Date      :   2023/07/03
# @License   :   Mulan PSL v2
# @Desc      :   Test SSH link
# ############################################
jsa_file()
{
ssh agent1  "rm /home/test  -rf"
ssh agent2  "rm /home/test  -rf"
ssh agent3  "rm /home/test  -rf"
rm  /home/*.lst
}
jsa_file
for  i  in {1..3}
do
if  ssh agent$i test  -d  /home/test
then  echo "exist";
else
ssh agent$i  mkdir /home/test
fi
done
test_dir=/home/bigdata_auto/test/spark/conf
test_bin=/home/bigdata_auto/test/spark/bin


sed -i "/UseNUMA/ s/#*//" ${test_dir}/spark-defaults.conf
sed -i "/UseNUMA/ s/^/#/" ${test_dir}/spark-defaults.conf
jvm_1=`grep  -n   'UseNUMA'  ${test_dir}/spark-defaults.conf    |  cut -d ":" -f 1 |  awk 'NR==1{print}'`
jvm_2=`grep  -n   'UseNUMA'  ${test_dir}/spark-defaults.conf    |  cut -d ":" -f 1 |  awk 'NR==2{print}'`
jvm_3=`grep  -n   'UseNUMA'  ${test_dir}/spark-defaults.conf    |  cut -d ":" -f 1 |  awk 'NR==3{print}'`
jvm_4=`grep  -n   'UseNUMA'  ${test_dir}/spark-defaults.conf    |  cut -d ":" -f 1 |  awk 'NR==4{print}'`
jvm_5=`grep  -n   'UseNUMA'  ${test_dir}/spark-defaults.conf    |  cut -d ":" -f 1 |  awk 'NR==5{print}'`
jvm_6=`grep  -n   'UseNUMA'  ${test_dir}/spark-defaults.conf    |  cut -d ":" -f 1 |  awk 'NR==6{print}'`
jvm_7=`grep  -n   'UseNUMA'  ${test_dir}/spark-defaults.conf    |  cut -d ":" -f 1 |  awk 'NR==7{print}'`
spark_list()
{
sh  ${test_bin}/spark_tpcds.sh  sql4.sql  &{ sleep  100;kill  $! &}  &&  ps  -ef  | grep  sql4  | grep -v grep   |awk  {'print $2'}  |  xargs  kill -9
}
spark_jsa()
{
file=/home/script/spark.jsa
if  [  -f "$file" ]
then
scp $file   agent1:/home/test
scp $file   agent2:/home/test
scp $file   agent1:/home/test
else

sed -i  "${jvm_5}s/#*//"  $test_dir/spark-defaults.conf
sh  ${test_bin}/spark_tpcds.sh   sql4.sql
sleep  15
ssh  agent1  "cat   /home/test/spark-*   | sort  | uniq  >  /home/test/spark.lst"
scp  agent1:/home/test/spark.lst  /home/
scp /home/spark.lst   agent2:/home/test/
scp  /home/spark.lst   agent3:/home/test/
sed -i  "${jvm_5}s/^/#/"  $test_dir/spark-defaults.conf
sed -i  "${jvm_6}s/#*//"  $test_dir/spark-defaults.conf
sh  ${test_bin}/spark_tpcds.sh  sql4.sql  &{ sleep  100;kill  $! &}  &&  ps  -ef  | grep  sql4  | grep -v grep   |awk  {'print $2'}  |  xargs  kill -9
sleep  15
sed -i  "${jvm_6}s/^/#/"  $test_dir/spark-defaults.conf
sed -i  "${jvm_7}s/#*//"  $test_dir/spark-defaults.conf
sh ${test_bin}/spark_tpcds.sh   sql4.sql
       sleep  15
fi
ssh agent1  rm   /home/test/spark-* -f
ssh agent2  rm   /home/test/spark-* -f
ssh agent3  rm   /home/test/spark-* -f
}

abs=`cat  /etc/os-release   | grep  PRETTY  | grep -oE "[\"].**[\"]"|grep -oE "[^\"].*[^\"]"  |  awk '{print $1}'`
#abb=`echo ${abs:0:7}`
abd=`arch`

if   [[ $abs = "openEuler" ]] &&  [[ $abd = "aarch64" ]]
then
      echo  "openEuler"
      spark_jsa

else
       echo "other"
fi
num0()
{
 sed -i   '38s/^/#/'            ${test_dir}/spark-defaults.conf
 sed -i   '39s/^/#//'            ${test_dir}/spark-defaults.conf
 sed -i   '40s/^/#/'            ${test_dir}/spark-defaults.conf
 sed -i   '41s/^/#/'            ${test_dir}/spark-defaults.conf
 sed -i   '47s/#*//'            ${test_dir}/spark-defaults.conf
}
num1()
{
 sed -i   '38s/^/#/'            ${test_dir}/spark-defaults.conf
 sed -i   '39s/^/#/'            ${test_dir}/spark-defaults.conf
 sed -i   '40s/#*//'            ${test_dir}/spark-defaults.conf
 sed -i   '41s/#*//'            ${test_dir}/spark-defaults.conf
 sed -i   '47s/^/#/'            ${test_dir}/spark-defaults.conf
}
num2()
{
 sed -i   '38s/#*//'            ${test_dir}/spark-defaults.conf
 sed -i   '39s/#*//'            ${test_dir}/spark-defaults.conf
 sed -i   '40s/^/#/'            ${test_dir}/spark-defaults.conf
 sed -i   '41s/^/#/'            ${test_dir}/spark-defaults.conf
 sed -i   '47s/^/#/'            ${test_dir}/spark-defaults.conf
}

if   [[ $abs = "openEuler" ]] &&  [[ $abd = "aarch64" ]]
then
     echo  "openEuler"

else
      echo  "########################other"
fi
