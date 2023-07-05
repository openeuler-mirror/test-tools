#!/bin/bash
tool_root_dir=$(cd "$(dirname "$0")/../.."||exit 1;pwd)
source "${tool_root_dir}/conf/config"
source "${tool_root_dir}/bin/common/remote.sh"

add_env_var() {
    ip=$1
    user=$2
    add_env_var_script=$3

    echo -e "\033[42;30m ====================Check & add environment variables to /etc/profile [${ip}]==================== \033[0m"

    send_remote "${add_env_var_script}" "/tmp/${add_env_var_script##*/}" "${ip}" "${user}"

    run_remote "bash /tmp/${add_env_var_script##*/}" "${ip}" "${user}"

    delete_remote "/tmp/${add_env_var_script##*/}" "${ip}" "${user}"

}

modify_conf() {
    conf_dir=${hbase_dir}/${package_name}/conf
    \cp "${tool_root_dir}/conf/hbase-conf/${platform}/${hbase_version}"/* "${conf_dir}"

    # 修改hbase-env.sh
    jdk_env_var=$(cat < /etc/profile | grep "^export JAVA_HOME=")
    echo "${jdk_env_var}" >> "${conf_dir}/hbase-env.sh"
    echo "export HBASE_MANAGES_ZK=false" >> "${conf_dir}/hbase-env.sh"
    echo "export HBASE_LIBRARY_PATH=${hadoop_home}/lib/native" >> "${conf_dir}/hbase-env.sh"
    
    # 修改hbase-site.xml
    sed -i "s/{master}/${master}/g" "${conf_dir}/hbase-site.xml"
    sed -i "s%{hbase_tmp_dir}%${hbase_tmp_dir}%g" "${conf_dir}/hbase-site.xml"
    sed -i "s/{hbase_zookeeper_quorum}/${hbase_zookeeper_quorum}/g" "${conf_dir}/hbase-site.xml"

    # 修改regionservers文件
    rm -rf "${conf_dir}/regionservers"
    export IFS=","
    for ip in ${regionserver_list}
    do
        echo "${ip}" >> "${conf_dir}/regionservers"
    done
    
    # 拷贝hadoop的hdfs-site.xml至hbase conf目录
    cp "${hadoop_home}/etc/hadoop/hdfs-site.xml" "${hbase_dir}/hbase/conf/hdfs-site.xml"
}

add_env_var_script=${tool_root_dir}/bin/deploy/check_add_env_var.sh

# 下载安装包
if [ "${is_online}" == "true" ]; then
    if ! bash "${tool_root_dir}/bin/download/download.sh"; then
        echo "Download deps fail!"
        exit 1
    fi
fi

# 解压压缩包
tar -zxf "${tool_root_dir}/deps/${platform}/${hbase_version}/${package}" -C "${hbase_dir}"

if [ "${platform}" = "HDP" ] ||  [ "${platform}" = "CDH" ] ||  [ "${platform}" = "APACHE" ]; then
    package_name=${package%-bin*}

else
    echo "Unsupported platform!"
    exit 1;
fi



# 建立软链接
ln -s "${hbase_dir}/${package_name}" "${hbase_dir}/hbase"

# 添加环境变量
bash "${add_env_var_script}"

# 替换hbase配置文件
modify_conf

# 获取本机的主机名
localhost=$(hostname -f)

tar -zcPf "${hbase_dir}/${package_name}.tar.gz"  "${hbase_dir}/${package_name}"
# 以","作为分隔符，将在server1节点配好的hbase包传到所有regionserver节点，并建立软链接、添加环境变量
export IFS=","
for ip in ${regionserver_list}
do
    if [ "${localhost}" == "${ip}" ];then
        continue
    fi

    # 将在server1节点配好的hbase包传到当前datanode节点
    send_remote "${hbase_dir}/${package_name}.tar.gz" "${hbase_dir}/${package_name}.tar.gz" "${ip}" "root"

    ssh $ip "tar -zxPf ${hbase_dir}/${package_name}.tar.gz -C ${hbase_dir} || exit 1"
    # 建立软链接
    run_remote "ln -s ${hbase_dir}/${package_name} ${hbase_dir}/hbase" "${ip}" "root"

    # Ìí¼Ó环境变量
    add_env_var "${ip}" "root" "${add_env_var_script}"
done

# 启动hbase集群
bash "${tool_root_dir}/bin/switch/start.sh"
