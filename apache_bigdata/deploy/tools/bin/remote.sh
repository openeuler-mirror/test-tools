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

run_remote() {
  cmd_str=$1
  remote_ip=$2
  remote_pwd=$3
  remote_user=$4

  if ! check_ssh_key "${remote_ip}"; then
     # expect
     /usr/bin/expect <<EOF
     set timeout 60000
     spawn ssh -o "StrictHostKeyChecking=no" ${remote_user}@${remote_ip} "${cmd_str}"
     expect {
        "yes/no" { send "yes\r";exp_continue }
        "password" { send "${remote_pwd}\r";exp_continue }
        "]#" { send "\r"}
     }
EOF
  else
     #ssh -n -o "StrictHostKeyChecking=no" root@${remote_ip} "${cmd_str} > /dev/null 2>&1"
     #ssh -n -o "StrictHostKeyChecking=no" root@${remote_ip} "${cmd_str}"
     ssh -n -o "StrictHostKeyChecking=no" "${remote_user}"@"${remote_ip}" "${cmd_str}"
  fi
}

send_remote() {
    src_file=$1
    target_file=$2
    send_ip=$3
    send_pwd=$4
    send_user=$5

    if ! check_ssh_key "${send_ip}"; then
      # expect
      /usr/bin/expect <<-EOF
      set timeout 6000
      spawn scp -r -o "StrictHostKeyChecking=no" $src_file ${send_user}@$send_ip:$target_file
      expect "*word*"
      send "$send_pwd\r"
      expect eof
EOF
   else
      scp -r -o "StrictHostKeyChecking=no" "${src_file}" "${send_user}"@"${send_ip}":"${target_file}"
   fi
}

delete_remote() {
    delete_file=$1
    remote_ip=$2
    remote_pwd=$3
    remote_user=$4

    run_remote "rm -rf ${delete_file}" "${remote_ip}" "${remote_pwd}" "${remote_user}"
}

check_ssh_key() {
   hostno=$1
   #echo -e "$hostno\c" && ssh ${hostno} -o PreferredAuthentications=publickey -o StrictHostKeyChecking=no date > /dev/null 2>&1
   if ssh "${hostno}" -o PreferredAuthentications=publickey -o StrictHostKeyChecking=no date > /dev/null 2>&1; then
      return 0
   else
      return 1
   fi

}
