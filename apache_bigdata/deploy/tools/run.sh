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

tool_root_dir=$(cd "$(dirname "$0")" || exit 1;pwd)
source "${tool_root_dir}"/bin/utils.sh "${tool_root_dir}"

# 执行基本环境部署操作
basic_environment_deploy

echo -e "\033[31m ##########################################################################################\033[0m"
echo input_ssh_free
echo -e "\033[32m *********************************************************************************************\033[0m"

ip_list=${tool_root_dir}/conf/ip_hostname_map.list
read -r -a line <<< $(cat ${ip_list} |awk '{print $2}')
for ip in "${line[@]}"
do
ssh $ip "source /etc/profile;echo StrictHostKeyChecking no >> /etc/ssh/ssh_config;echo UserKnownHostsFile /dev/null >> /etc/ssh/ssh_config;service sshd restart"
done
echo -e "\033[33m ************************************************添加sshd免输yes success*****************************************\033[0m"


source /etc/profile
echo "basic_env is finished" > "/root/basic_env"
#########################################jdk
java_dir1=`ls    -l  /lib/jvm   | grep  java-1.8.0-openjdk-  |  cut -d  ' '   -f  9  | grep java`
java_dir2=`ls    -l  /lib/jvm   | grep  java-1.8.0-openjdk-  |  cut -d  ' '   -f  9  | grep java`
if  [[  -n  $java_dir1 ]]
then
	java_dir=$java_dir1
else
	java_dir=$java_dir2
fi
echo  "export JAVA_HOME=/usr/lib/jvm/$java_dir" >> /root/java.sh
echo  "export PATH=\$JAVA_HOME/bin:\$PATH " >>   /root/java.sh
tail -2   /root/java.sh   >   /root/jdk.sh
for   line     in   `tail  -n +3  /etc/hosts  |   awk   '{print   $2}'` ;
  do
          scp   /root/jdk.sh     $line:/etc/profile.d/
	  ssh   $line    "tail -n 2  /etc/profile.d/jdk.sh  >>  /etc/profile"
          ssh   $line    "source   /etc/profile"
 done
 rm  /root/java.sh    -f
 rm  /root/jdk.sh     -f
