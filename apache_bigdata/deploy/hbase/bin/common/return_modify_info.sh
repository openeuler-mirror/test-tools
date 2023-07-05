#!/bin/bash
tool_root_dir=$(cd $(dirname "$0")/../..||exit 1;pwd)
source ${tool_root_dir}/conf/config
# 将节点解析成数组
ips=${master},${regionserver_list}
# 获取去重后的节点列表
node_list=($(echo ${ips[*]}| sed 's/,/\n/g'| sort | uniq))
# 输出头结点和安装路径
echo "${node_list} ${hbase_dir}/hbase"

