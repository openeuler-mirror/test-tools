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

run_remote()
{
  cmd_str=$1
  remote_ip=$2
  remote_pwd=$3

  if ! check_ssh_key "${remote_ip}";
  then
     # expect
     /usr/bin/expect <<-EOF
     set timeout 60000
     spawn ssh -o "StrictHostKeyChecking=no" root@${remote_ip} "${cmd_str} > /dev/null 2>&1"
     expect "*word*"
     send "${remote_pwd}\r"
     expect eof
EOF
  else
     #echo "$cmd_str"
     ssh -n -o "StrictHostKeyChecking=no" root@"${remote_ip}" "${cmd_str} > /dev/null 2>&1"
  fi
}

run_remote_show_log()
{
  cmd_str=$1
  remote_ip=$2
  remote_pwd=$3

  if ! check_ssh_key "${remote_ip}";
  then
     # expect
     /usr/bin/expect <<-EOF
     set timeout 60000
     spawn ssh -o "StrictHostKeyChecking=no" root@${remote_ip} "${cmd_str}"
     expect "*word*"
     send "${remote_pwd}\r"
     expect eof
EOF
  else
     #echo "$cmd_str"
     ssh -n -o "StrictHostKeyChecking=no" root@"${remote_ip}" "${cmd_str}"
  fi
}

send_remote()
{
    src_file=$1
    target_file=$2
    send_ip=$3
    send_pwd=$4
    echo "${src_file}"

    if ! check_ssh_key "${send_ip}";
    then
      # expect
      /usr/bin/expect <<-EOF
      set timeout 6000
      spawn scp -r -o "StrictHostKeyChecking=no" $src_file root@${send_ip}:${target_file}
      expect "*word*"
      send "${send_pwd}\r"
      expect eof
EOF
   else
      scp -r -o "StrictHostKeyChecking=no" "${src_file}" root@"${send_ip}":"${target_file}"
   fi
}

get_remote()
{
    src_file=$1
    target_file=$2
    remote_ip=$3
    remote_pwd=$4
    echo "${src_file}"

    if ! check_ssh_key "${remote_ip}"; 
    then
      # expect
      /usr/bin/expect <<-EOF
      set timeout 6000
      spawn scp -r -o "StrictHostKeyChecking=no" root@${remote_ip}:${src_file} ${target_file}
      expect "*word*"
      send "${remote_pwd}\r"
      expect eof
EOF
   else
      scp -r -o "StrictHostKeyChecking=no" root@"${remote_ip}":"${src_file}" "${target_file}"
   fi
}

check_ssh_key(){
   hostno=$1
   #echo -e "$hostno\c" && ssh ${hostno} -o PreferredAuthentications=publickey -o StrictHostKeyChecking=no date > /dev/null 2>&1
   if ssh "${hostno}" -o PreferredAuthentications=publickey -o StrictHostKeyChecking=no date > /dev/null 2>&1; 
   then
      return 0
   else
      return 1
   fi

}
