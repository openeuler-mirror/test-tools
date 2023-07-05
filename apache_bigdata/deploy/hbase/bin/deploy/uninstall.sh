#!/bin/bash
tool_root_dir=$(cd "$(dirname "$0")"/../..||exit 1;pwd)
source "${tool_root_dir}/conf/config"
source "${tool_root_dir}/bin/common/remote.sh"

echo "you will uninstall hbase,please input 'yes' to confirm"
read -r yes

if [ "${yes}" = yes ];then
    # 先停止集群
    bash "${tool_root_dir}/bin/switch/stop.sh"
    echo "hbase will be uninstalled"

   if [ "${platform}" = "HDP" ] ||  [ "${platform}" = "CDH" ] ||  [ "${platform}" = "APACHE" ]; then
       package_name=${package%-bin*}

   else
       echo "Unsupported platform!"
       exit 1;
   fi

    node_list="${master},${regionserver_list}"
    export IFS=","
    for node_host in ${node_list}
    do
        delete_remote "${hbase_dir}/hbase" "${node_host}" "root"
        delete_remote "${hbase_dir}/${package_name}" "${node_host}" "root"
        delete_remote "${hbase_dir}/${package_name}.tar.gz" "${node_host}" "root"
    done    
    echo "Hbase has successfully removed from your computer!"
else
    echo "cancel"
fi
