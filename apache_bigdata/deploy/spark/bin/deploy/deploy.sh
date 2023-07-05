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

tool_root_dir=$(cd "$(dirname "$0")/../../"||exit 1;pwd)
source "${tool_root_dir}/bin/common/remote.sh"
source "${tool_root_dir}/conf/config"

read -r -a node_arr <<< "${spark_client//,/ }"

add_env_var_script=${tool_root_dir}/bin/deploy/check_add_env_var.sh

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
    # Init conf
    spark_conf_dir=${spark_dir}/${package%.tar.gz*}/conf
    \cp "${tool_root_dir}/conf/spark-conf/${platform}/${spark_version}"/* "${spark_conf_dir}"
    
    java_home=$(grep "^export JAVA_HOME" /etc/profile)
    echo "${java_home}" >> "${spark_conf_dir}/spark-env.sh"
    echo "export SCALA_HOME=${scala_dir}/scala" >> "${spark_conf_dir}/spark-env.sh"
    echo "export HADOOP_HOME=${hadoop_home}" >> "${spark_conf_dir}/spark-env.sh"
    echo "export HADOOP_CONF_DIR=${hadoop_home}/etc/hadoop" >> "${spark_conf_dir}/spark-env.sh"
    
    echo "spark.master                     yarn" >> "${spark_conf_dir}/spark-defaults.conf"
    echo "spark.eventLog.enabled           true" >> "${spark_conf_dir}/spark-defaults.conf"
    echo "spark.eventLog.dir               ${spark_log_dir}" >> "${spark_conf_dir}/spark-defaults.conf"
    echo "spark.eventLog.compress          true" >> "${spark_conf_dir}/spark-defaults.conf"
    echo "spark.history.fs.logDirectory          ${spark_log_dir}" >> "${spark_conf_dir}/spark-defaults.conf"
    
    if [ ! -f "${hadoop_home}/etc/hadoop/core-site.xml" ] && [ ! -f "${hadoop_home}/etc/hadoop/hdfs-site.xml" ]; then
        echo "${hadoop_home}/etc/hadoop/core-site.xml or ${hadoop_home}/etc/hadoop/hdfs-site.xml does not exit, please check environment"
        exit 1;
    fi
    #if [ ! -f ${hive_home}/conf/hive-site.xml ] && [ ! -f ${hive_home}/lib/${jdbc_driver} ]; then
    #    echo "${hive_home}/conf/hive-site.xml or ${hive_home}/lib/${jdbc_driver} does not exit, please check environment"
    #    exit 1;
    #fi
    \cp "${hadoop_home}/etc/hadoop/core-site.xml" "${spark_dir}/spark/conf"
    \cp "${hadoop_home}/etc/hadoop/hdfs-site.xml" "${spark_dir}/spark/conf"
    #\cp ${hive_home}/conf/hive-site.xml ${spark_dir}/spark/conf
    
    sed -i "s/{hive_node}/${hive_node}/g" "${spark_conf_dir}/hive-site.xml"
    sed -i "s/{thrift_server_port}/${thrift_server_port}/g" "${spark_conf_dir}/hive-site.xml"

    # CDH默认不支持Thrift Server，需要另外步骤
    if [ "X${platform}" == "XCDH" ]; then
        sed -i "s!{spark_yarn_jar}!${spark_yarn_jar}!g" "${spark_conf_dir}/spark-defaults.conf"

        # 上传spark-assembly jar包至HDFS的{spark_yarn_jar}位置
        existed_flag=$(hadoop fs -ls "${spark_yarn_jar}" > /dev/null 2>&1; echo $?)
        #let existed_flag=${existed_flag}
        if [ "${existed_flag}" -ne 0 ]; then
            hadoop fs -mkdir -p "${spark_yarn_jar%/*}" 
            hadoop fs -put "${spark_dir}/spark/lib/${spark_yarn_jar##*/}" "${spark_yarn_jar}"
            hadoop fs -chmod 755 "${spark_yarn_jar}"
        fi
    fi
    
    if [ ! -f "${hive_home}/lib/${jdbc_driver}" ]; then
        echo "${hive_home}/lib/${jdbc_driver} does not exit, please check environment"
        exit 1;
    fi
    \cp "${hive_home}/lib/${jdbc_driver}" "${spark_dir}/spark/jars"
    
    for node in ${node_arr[*]}
    do
        echo "Send spark & scala dir to node [${node}]"
        send_remote "${spark_dir}/${package%.tar.gz*}" "${spark_dir}/${package%.tar.gz*}" "${node}" "root"
        send_remote "${scala_dir}/${scala_package%.tar*}" "${scala_dir}/${scala_package%.tar*}" "${node}" "root"
    
        echo "Create soft link [${node}]"
        run_remote "ln -s ${scala_dir}/${scala_package%.tar*} ${scala_dir}/scala" "${node}" "root"
        run_remote "ln -s ${spark_dir}/${package%.tar.gz*} ${spark_dir}/spark" "${node}" "root"
    
        echo "Configure /etc/profile [${node}]"
        add_env_var "${node}" "root" "${add_env_var_script}"
    done
}

#download packages
if [ "$is_online" == "true" ]
then
    echo "statr download packages!"
    if ! sh "${tool_root_dir}/bin/download/download.sh"; then
        echo "download deps fail!"
        exit 1
    fi
fi

echo "Unpack scala package to ${scala_dir}"
tar -zxf "${tool_root_dir}/deps/${platform}/${spark_version}/${scala_package}" -C "${scala_dir}"

echo "Unpack spark package to ${spark_dir}"
tar -zxf "${tool_root_dir}/deps/${platform}/${spark_version}/${package}" -C "${spark_dir}"

echo "Create soft link"
ln -s "${scala_dir}/${scala_package%.tar*}" "${scala_dir}/scala"
ln -s "${spark_dir}/${package%.tar.gz*}" "${spark_dir}/spark"

echo "Configure /etc/profile"
bash "${add_env_var_script}"

# modify spark configuration file
modify_conf

# start spark history server
source /etc/profile
hdfs dfs -mkdir -p "${spark_log_dir}"
#run_remote "source /etc/profile; ${spark_dir}/spark/sbin/start-history-server.sh" ${history_node}


for node in ${node_arr[*]}
    do
        send_remote "/usr/local/hadoop/share/hadoop/hdfs/lib/jersey-core-1.19.jar" "/usr/local/spark/jars/jersey-core-1.19.jar" "${node}" "root"
        send_remote "/usr/local/hadoop/share/hadoop/yarn/lib/jersey-client-1.19.jar" "/usr/local/spark/jars/jersey-client-1.19.jar" "${node}" "root"
    done
cp /usr/local/hadoop/share/hadoop/yarn/lib/jersey-client-1.19.jar  /usr/local/spark/jars/
cp /usr/local/hadoop/share/hadoop/hdfs/lib/jersey-core-1.19.jar /usr/local/spark/jars/
bash "${tool_root_dir}/bin/switch/start.sh"
