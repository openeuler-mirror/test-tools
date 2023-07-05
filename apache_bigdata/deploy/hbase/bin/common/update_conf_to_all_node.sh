#!/bin/bash
file_path=$1
password=$2

tool_root_dir=$(cd $(dirname "$0")/../..||exit 1;pwd)
source ${tool_root_dir}/conf/config

ips=${master},${regionserver_list}
node_list=($(echo ${ips[*]}| sed 's/,/\n/g'| sort | uniq))
num=0
for agent in ${node_list[@]}
do
if [ $num == 0 ]
then
# ssh_agent为更新过文件的节点
ssh_agent=$agent
else

ssh $ssh_agent "expect <<EOF
set timeout 100
spawn scp -r ${file_path} root@${agent}:${file_path}
expect {
          \"yes/no\" { send \"yes\r\";exp_continue }
          \"password\" { send \"${password}\r\";exp_continue }
        }
EOF"
fi
((num++))
done 
