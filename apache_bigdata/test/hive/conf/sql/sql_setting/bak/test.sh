jvm_conf=/root/bigdata_auto/scripts/hive/conf/sql/sql_setting/
abs=`ls -l /usr/local/  | grep bisheng |  awk '{print $9}' `
abb=`echo ${abs:0:7}`
abd=`arch`
#[[ $abb= "bisheng" ]] &&  [[ $abd = "aarch64" ]]
if  [[ $abb = "bisheng" ]] &&  [[ $abd = "aarch64" ]]
then
      for i  in {1..10}
      do  sed  -i '$s/#*//'   $jvm_conf/sql$i.sql_hive.setting
      done  

else
     for i  in {1..10}
      do  sed  -i '$s/^/#/'   $jvm_conf/sql$i.sql_hive.setting
      done
echo $abb
echo $abd
fi
