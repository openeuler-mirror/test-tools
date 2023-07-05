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
#jsa_file
set_dir=/home/bigdata_auto/test/hive/conf/sql/sql_setting
hive_dir=/home/bigdata_auto/test/hive/bin
hive_js()
{
for  i  in {1..3}
do
if  ssh agent$i test  -d  /home/test  
then  echo "exist";  
else
ssh agent$i  mkdir /home/test
fi
done
file=/home/script/hive.jsa
if  [  -f "$file" ]
then
scp $file   agent1:/home/test
scp $file   agent2:/home/test
scp $file   agent1:/home/test
else
echo  "list ok"
fi
 sed  -i  "/UseAppCDS/s/#*//"  $set_dir/sql1.sql_hive.setting
 sed  -i  "/UseAppCDS/s/^/#/"  $set_dir/sql1.sql_hive.setting
 sed  -i  "/DumpLoaded/s/#*//" $set_dir/sql1.sql_hive.setting
	sh  $hive_dir/hive_tpcds_test.sh  sql1.sql
       sleep  15
ssh   agent1  "cat  /home/test/hive-*   | sort  | uniq  >  /home/test/hive.lst"
scp  agent1:/home/test/hive.lst  /home/
scp /home/hive.lst   agent2:/home/test/
scp  /home/hive.lst   agent3:/home/test/

sed  -i "/DumpLoaded/s/^/#/"   $set_dir/sql1.sql_hive.setting
sed  -i "/SharedClassListFile/s/#*//"   $set_dir/sql1.sql_hive.setting
	sh $hive_dir/hive_tpcds_test.sh  sql1.sql  &{ sleep  120;kill  $! &}  &&  ps  -ef  | grep  sql  | grep -v grep   |awk  {'print $2'}  |  xargs  kill -9
	sleep  15
sed  -i "/SharedClassListFile/s/^/#/"   $set_dir/sql1.sql_hive.setting
sed  -i "/SharedArchiveFile/s/#*//"   $set_dir/sql1.sql_hive.setting
sed  -i "/SharedClassListFile/s/^/#/"   $set_dir/sql1.sql_hive.setting
	sh  $hive_dir/hive_tpcds_test.sh  sql1.sql
	sleep  15

ssh agent1  rm -f  /home/test/hive-*
ssh agent2  rm -f  /home/test/hive-*
ssh agent3 rm -f  /home/test/hive-*
}
hive_sql_set()
{
abs=`cat  /etc/os-release   | grep  PRETTY  | grep -oE "[\"].**[\"]"|grep -oE "[^\"].*[^\"]"  |  awk '{print $1}'`
#abb=`echo ${abs:0:7}`
abd=`arch`

if  [[ $abs = "openEuler" ]] &&  [[ $abd = "aarch64" ]]
then
     for  i  in {1..10}
     do
     sed -i "/UseAppCDS/s/#*//"  $set_dir/sql${i}.sql_hive.setting
    done
      
else
     echo  "############other  "
     for  i  in {1..10}
     do
     sed -i  "/UseAppCDS/s/^/#/"  $set_dir/sql${i}.sql_hive.setting
     done
     
fi
}
hive_sql_set
hive_js
