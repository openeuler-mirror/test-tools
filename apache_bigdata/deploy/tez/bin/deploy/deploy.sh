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
tool_root_dir=$(cd "$(dirname "$0")"/../.. || exit 1;pwd)
source "${tool_root_dir}"/conf/config
source "${tool_root_dir}"/bin/common/remote.sh
script_path=`cd $(dirname "$0");pwd`

tmp_dir=/tmp

modify_conf() {
    hadoop_home=$1

    # 拷贝tez-site.xml到hadoop配置目录
    \cp "${tool_root_dir}"/conf/tez-conf/"${platform}"/"${tez_version}"/tez-site.xml "${hadoop_home}"/etc/hadoop/
    
    # 修改tez-site.xml配置
    sed -i "s/{master}/${master}/g" "${hadoop_home}"/etc/hadoop/tez-site.xml
    sed -i "s/{package}/${package}/g" "${hadoop_home}"/etc/hadoop/tez-site.xml

    # 添加Tez相关环境变量至hadoop-env.sh
    cat  ${hadoop_home}/etc/hadoop/hadoop-env.sh |grep "^export TEZ_CONF_DIR=${hadoop_home}/etc/hadoop/tez-site.xml"
    if [ $? != 0 ];then
        echo "export TEZ_CONF_DIR=/usr/local/tez/conf/tez-site.xml" >> "${hadoop_home}"/etc/hadoop/hadoop-env.sh
    fi
    cat ${hadoop_home}/etc/hadoop/hadoop-env.sh |grep "^export TEZ_JARS=/usr/local/tez"
    if [ $? != 0 ];then
        echo "export TEZ_JARS=/usr/local/tez" >> "${hadoop_home}"/etc/hadoop/hadoop-env.sh
    fi
    cat ${hadoop_home}/etc/hadoop/hadoop-env.sh |grep "^export HADOOP_CLASSPATH=\${HADOOP_CLASSPATH}:\${TEZ_CONF_DIR}:\${TEZ_JARS}/*:\${TEZ_JARS}/lib/*"
    if [ $? != 0 ];then
        echo "export HADOOP_CLASSPATH=\${HADOOP_CLASSPATH}:\${TEZ_CONF_DIR}:\${TEZ_JARS}/*:\${TEZ_JARS}/lib/*" >> "${hadoop_home}"/etc/hadoop/hadoop-env.sh
    fi
    source /etc/profile
    hadoop dfsadmin -safemode leave

}

install_tez_ui() {
    # 解压tomcat至指定安装目录，并建立软链接
    tar -zxf "${tool_root_dir}"/deps/"${platform}"/"${tez_version}"/"${tomcat_package}" -C "${tomcat_dir}"
    ln -s "${tomcat_dir}"/"${tomcat_package%.tar*}" "${tomcat_dir}"/tomcat

    # 解压tez-ui war包至${tomcat_dir}/tomcat/webapps/tez-ui
    mkdir -p "${tomcat_dir}"/tomcat/webapps/tez-ui
    unzip -o -d "${tomcat_dir}"/tomcat/webapps/tez-ui/ "${tool_root_dir}"/deps/"${platform}"/"${tez_version}"/"${tez_ui_war}" > /dev/null 2>&1

    # 替换configs.env中，timeline和rm中的IP地址
    sed -i "s%timeline:\ \"http://localhost:8188\"%timeline:\ \"http://${master}:8188\"%g" "${tomcat_dir}"/tomcat/webapps/tez-ui/config/configs.env
    sed -i "s%rm:\ \"http://localhost:8088\"%rm:\ \"http://${master}:8088\"%g" "${tomcat_dir}"/tomcat/webapps/tez-ui/config/configs.env

    # 添加timeline server的参数至hadoop yarn-site.xml
    if [ ! -f "${hadoop_home}"/etc/hadoop/yarn-site.xml-ori-backup ]; then
        cp "${hadoop_home}"/etc/hadoop/yarn-site.xml "${hadoop_home}"/etc/hadoop/yarn-site.xml-ori-backup
    fi
    sed -i '1,$s%</configuration>%%g' "${hadoop_home}"/etc/hadoop/yarn-site.xml
    cat "${tool_root_dir}"/conf/tez-conf/"${platform}"/"${tez_version}"/tez-ui-yarn-site.xml | while read -r line
    do
        para=$(echo "${line}" | awk -F '=' '{print $1}')
        value=$(echo "${line}" | awk -F '=' '{print $2}')

        is_existed=$(grep -n "${para}" "${hadoop_home}"/etc/hadoop/yarn-site.xml)
        if [ "X${is_existed}" == "X" ]; then
            echo -e "    <property>\n        <name>${para}</name>\n        <value>${value}</value>\n    </property>\n" >> ${hadoop_home}/etc/hadoop/yarn-site.xml
        fi
    done
    #cat ${tool_root_dir}/conf/tez-conf/${platform}/${tez_version}/tez-ui-yarn-site.xml >> ${hadoop_home}/etc/hadoop/yarn-site.xml
    echo '</configuration>' >> "${hadoop_home}"/etc/hadoop/yarn-site.xml
    sed -i "s/{master}/${master}/g" "${hadoop_home}"/etc/hadoop/yarn-site.xml

    # 修改${tomcat_dir}/tomcat/webapps/tez-ui/assets/tez-ui.js文件，将localhost修改为tez-ui计划部署的节点ip（原因：修改配置文件未生效，最终没有修改tez-ui.js文件）
    sed -i "s/localhost/${master}/g" "${tomcat_dir}"/tomcat/webapps/tez-ui/assets/tez-ui.js
}

# 默认脚本在server1节点执行，当不使用ssh远程调用命令，即默认在server1执行该命令

# 下载安装包
if [ "${is_online}" == "true" ]; then                
    if ! bash "${tool_root_dir}"/bin/download/download.sh ; then                        
        echo "Download deps fail!"                   
        exit 1                                       
    fi                                               
fi

# 解压压缩包
mkdir -p "${tez_dir}"/"${package%.tar*}"
tar -zxf "${tool_root_dir}"/deps/"${platform}"/"${tez_version}"/"${package}" -C "${tez_dir}"/"${package%.tar*}"

# 建立软链接
ln -s "${tez_dir}"/"${package%.tar*}" "${tez_dir}"/tez

# 上传tez tar包至HDFS
source /etc/profile
hadoop fs -mkdir -p /user/tez
hadoop fs -put "${tool_root_dir}"/deps/"${platform}"/"${tez_version}"/"${package}" /user/tez
hadoop fs -mkdir -p /apps/tez
hadoop fs -put "${tool_root_dir}"/deps/"${platform}"/"${tez_version}"/"${tez_package}" /apps/tez

# 替换tez配置文件
modify_conf "${hadoop_home}"

# 如果需要配置tez-ui，则安装tomcat，配置timelineserver和tez-ui参数
if [ "${is_tezui_installed}" == "true" ]; then
    install_tez_ui
fi

# 以","作为分隔符，将在server1节点配好的tez-site.xml等配置文件传到所有slave节点，并建立软链接、添加环境变量
read -r -a ip_arr <<< "${slaves//,/ }"
for ip in "${ip_arr[@]}"
do
    send_remote "${hadoop_home}/etc/hadoop/tez-site.xml" "${hadoop_home}"/etc/hadoop/tez-site.xml "${ip}" "root"
    send_remote "${hadoop_home}/etc/hadoop//hadoop-env.sh" "${hadoop_home}"/etc/hadoop/hadoop-env.sh "${ip}" "root"

    if [ "${is_tezui_installed}" == "true" ]; then
        send_remote "${hadoop_home}/etc/hadoop/yarn-site.xml" "${hadoop_home}"/etc/hadoop/yarn-site.xml "${ip}" "root"
    fi
done

# 重启hadoop集群使得配置生效
bash "${tool_root_dir}"/bin/common/restart_hadoop.sh

# 启动tez集群
bash "${tool_root_dir}"/bin/switch/start.sh
