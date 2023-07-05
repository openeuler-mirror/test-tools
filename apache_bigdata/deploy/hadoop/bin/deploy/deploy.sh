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
tool_root_dir=$(cd "$(dirname "$0")"/../..||exit 1;pwd)
source "${tool_root_dir}"/conf/config
source "${tool_root_dir}"/bin/common/remote.sh

add_env_var_script=${tool_root_dir}/bin/deploy/check_add_env_var.sh
disk_part_script=${tool_root_dir}/bin/deploy/disk_part.sh
read -r -a dn_arr <<< "${datanode//,/ }"

add_env_var() {
    ip=$1
    user=$2
    add_env_var_script=$3

    echo -e "\033[42;30m ====================Check & add environment variables to /etc/profile [${ip}]==================== \033[0m"

    send_remote "${add_env_var_script}" /tmp/"${add_env_var_script##*/}" "${ip}" "${user}"

    run_remote "bash /tmp/${add_env_var_script##*/}" "${ip}" "${user}"

    delete_remote /tmp/"${add_env_var_script##*/}" "${ip}" "${user}"
}

modify_conf() {
    conf_dir=${hadoop_dir}/hadoop/etc/hadoop
    \cp "${tool_root_dir}"/conf/hadoop-conf/"${platform}"/"${hadoop_version}"/* "${conf_dir}"
    
    # Ìæ»»ÅäÖÃÎÄ¼þÖÐµÄ²ÎÊý
    sed -i "s/{namenode}/${namenode}/g" "${conf_dir}"/core-site.xml
    sed -i "s!{hadoop_tmp_dir}!${hadoop_tmp_dir}!g" "${conf_dir}"/core-site.xml

    sed -i "s/{namenode}/${namenode}/g" "${conf_dir}"/hdfs-site.xml
    sed -i "s!{namenode_dir}!${namenode_dir}!g" "${conf_dir}"/hdfs-site.xml
    sed -i "s!{datanode_dir}!${datanode_dir}!g" "${conf_dir}"/hdfs-site.xml

    sed -i "s/{namenode}/${namenode}/g" "${conf_dir}"/yarn-site.xml
    sed -i "s/{yarn_memory}/${yarn_memory}/g" "${conf_dir}"/yarn-site.xml
    sed -i "s/{yarn_vcores}/${yarn_vcores}/g" "${conf_dir}"/yarn-site.xml
    sed -i "s!{hadoop_dir}!${hadoop_dir}!g" "${conf_dir}"/yarn-site.xml

    sed -i "s!{hadoop_dir}!${hadoop_dir}!g" "${conf_dir}"/mapred-site.xml
    
    echo "export HDFS_NAMENODE_USER=root" >> "${conf_dir}"/hadoop-env.sh
    echo "export HDFS_SECONDARYNAMENODE_USER=root" >> "${conf_dir}"/hadoop-env.sh
    echo "export HDFS_DATANODE_USER=root" >> "${conf_dir}"/hadoop-env.sh

   # { echo "export HDFS_NAMENODE_USER=root"; echo "export HDFS_NAMENODE_USER=root"; } >> "${conf_dir}"/hadoop-env.sh

    echo "export YARN_REGISTRYDNS_SECURE_USER=root" >> "${conf_dir}"/yarn-env.sh
    echo "export YARN_RESOURCEMANAGER_USER=root" >> "${conf_dir}"/yarn-env.sh
    echo "export YARN_NODEMANAGER_USER=root" >> "${conf_dir}"/yarn-env.sh

    jdk_env_var=`cat /etc/profile | grep "^export JAVA_HOME="`
    echo "${jdk_env_var}" >> "${conf_dir}"/hadoop-env.sh

    # 根据datanode变量配置slaves或者workers文件
    if [ -f "${conf_dir}"/workers ]; then
        dn_file=${conf_dir}/workers
    else
        dn_file=${conf_dir}/slaves
    fi
    rm -rf "${dn_file}"

    for ip in "${dn_arr[@]}"
    do
        echo "${ip}" >> "${dn_file}"
    done
}

# 下载安装包
if [ "${is_online}" == "true" ]; then    
    if ! bash "${tool_root_dir}"/bin/download/download.sh; then
        echo "Download deps fail!"
        exit 1
    fi
fi

# 解压压缩包
tar -zxf "${tool_root_dir}"/deps/"${platform}"/"${hadoop_version}"/"${package}" -C "${hadoop_dir}"

if [ "${platform}" == "HDP" ]; then
    package_name=${package%.tar*}
elif [ "${platform}" == "CDH" ]; then
    package_name=${package%-bin*}
elif [ ${platform} == "APACHE" ]; then
    package_name=${package%.tar*}
else
    echo "Unsupported platform!"
    exit 1;
fi

# 建立软链接
ln -s "${hadoop_dir}"/"${package_name}" "${hadoop_dir}"/hadoop

# 添加环境变量
bash "${add_env_var_script}"

# 替换hadoop配置文件
modify_conf

# 获取本机的主机名
localhost=$(hostname -f)
yum install numactl -y

# 压缩包作为send传 速率更快
tar -zcPf "${hadoop_dir}"/"${package_name}.tar.gz"   "${hadoop_dir}"/"${package_name}"
# 以","作为分隔符，将在server1节点配好的hadoop包传到所有datanode节点，并建立软链接、添加环境变量
for ip in "${dn_arr[@]}"
do
    if [ "${localhost}" == "${ip}" ];then
        continue
    fi
    run_remote "yum install numactl -y"  "${ip}" "${user}"
    # part disk
    send_remote "${disk_part_script}" /tmp/"${disk_part_script##*/}" "${ip}" "${user}"

    run_remote "bash /tmp/${disk_part_script##*/} ${disk_num} ${dir_name} ${disk_format_type}" "${ip}" "${user}"

    delete_remote /tmp/"${disk_part_script##*/}" "${ip}" "${user}"
 
   
    # 将在server1节点配好的hadoop包传到当前datanode节点
    send_remote "${hadoop_dir}"/"${package_name}.tar.gz" "${hadoop_dir}"/"${package_name}.tar.gz" "${ip}" "root"

    ssh $ip "tar -zxPf ${hadoop_dir}/${package_name}.tar.gz -C ${hadoop_dir} || exit 1"
    # 建立软链接
    run_remote "ln -s ${hadoop_dir}/${package_name} ${hadoop_dir}/hadoop" "${ip}" "root"

    # Ìí¼Ó环境变量
    add_env_var "${ip}" "root" "${add_env_var_script}"
done

# 格式化数据目录
bash "${tool_root_dir}"/bin/deploy/format.sh

# 启动hadoop集群
bash "${tool_root_dir}"/bin/switch/start.sh
