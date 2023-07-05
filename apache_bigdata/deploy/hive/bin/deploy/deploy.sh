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
yum remove  selinux-policy-targeted   -y
tool_root_dir=$(cd "$(dirname "$0")"/../..||exit 1;pwd)
source "${tool_root_dir}"/conf/config
source "${tool_root_dir}"/bin/common/remote.sh

add_env_var_script=${tool_root_dir}/bin/deploy/check_add_env_var.sh

modify_conf() {
    hadoop_home=$1

    # 配置环境变量
    bash "${add_env_var_script}"

    # 拷贝hive-site.xml到hive配置目录
    conf_dir=${hive_dir}/${package%.tar*}/conf/
    \cp "${tool_root_dir}"/conf/hive-conf/"${platform}"/"${hive_version}"/hive-site.xml "${conf_dir}"
    
    # 修改hive-site.xml配置
    sed -i "s/{master}/${master}/g" "${conf_dir}"/hive-site.xml
    sed -i "s/{db_user}/${db_user}/g" "${conf_dir}"/hive-site.xml
    sed -i "s/{db_pswd}/${db_pswd}/g" "${conf_dir}"/hive-site.xml

    # 修改hive-env.sh，添加环境变量
    \cp "${conf_dir}"/hive-env.sh.template "${conf_dir}"/hive-env.sh
    java_install_home=$(grep "^export JAVA_HOME" /etc/profile)
    echo "${java_install_home}" >> "${conf_dir}"/hive-env.sh
    hadoop_install_home=$(grep "^export HADOOP_HOME" /etc/profile)
    echo "${hadoop_install_home}" >> "${conf_dir}"/hive-env.sh
    echo "export HIVE_CONF_DIR=${hive_dir}/hive/conf" >> "${conf_dir}"/hive-env.sh

    # 修改hadoop的core-site.xml文件，添加hadoop.proxyuser.root.hosts和hadoop.proxyuser.root.groups参数
    modify_flag=false
    hadoop_core_xml=${hadoop_home}/etc/hadoop/core-site.xml
    for para in $(cat "${tool_root_dir}"/conf/hive-conf/"${platform}"/"${hive_version}"/hive-core-site.xml)
    do
        para_name=${para%=*}
        para_value=${para#*=}
        query_result=$(grep "${para_name}" "${hadoop_core_xml}")
        if [ "X${query_result}" == "X" ]; then
            sed -i "s%</configuration>%    <property>\n        <name>${para_name}</name>\n        <value>${para_value}</value>\n    </property>\n</configuration>%g" ${hadoop_core_xml}
	    modify_flag=true
	fi
    done

    node_arr=(${slaves//,/ });
    for ip in ${node_arr[*]}
    do
        send_remote "${hadoop_core_xml}" "${hadoop_core_xml}" "${ip}" "root"
    done

    if [ ${modify_flag} == true ]; then
        # 重启hadoop集群
	bash "${tool_root_dir}"/bin/common/restart_hadoop.sh
    fi
}

add_para() {
    para=$1
    value=$2
    file=$3
    label=$4

    is_existed=$(grep -n "${para}" "${file}")
    if [ "X${value}" == "X" ]; then
        if [ "X${is_existed}" == "X" ]; then
            sed -i "s/\[${label}\]/\[${label}\]\n${para}/g" "${file}"
        fi
    else
        if [ "X${is_existed}" == "X" ]; then
            sed -i "s/\[${label}\]/\[${label}\]\n${para}=${value}/g" "${file}"
        else
            is_init_connect_existed=$(grep -n "${para}=${value}" "${file}")
            if [ "${para}" == "init_connect" ]; then
                if [ "X${is_init_connect_existed}" == "X" ]; then
                    sed -i "s/\[${label}\]/\[${label}\]\n${para}=${value}/g" "${file}"
                fi
            else
                sed -i "s/${para}.*/${para}=${value}/g" "${file}"
            fi
        fi
    fi
}

install_mariadb() {
    # 安装mariadb，默认已配置yum源
    yum -y install mariadb  mariadb-server
    systemctl start mariadb.service
    systemctl enable mariadb.service
    
    # 考虑mariadb刚安装默认不带密码和已经设密码两种情况
    ret=$(mysqladmin -uroot -p"${db_pswd}" ping 2>/dev/null)
    if [ "${ret}" == "mysqld is alive" ];then
        echo "Mariadb has been installed before."
        cur_pswd=${db_pswd}
    else
        ret2=$(mysqladmin -uroot ping 2>/dev/null)
        if [ "${ret2}" == "mysqld is alive" ];then
            echo "Mariadb has just been installed."
            cur_pswd=""
        else
            echo "Mariadb login error."
            exit 1
        fi
    fi

    # 配置权限和密码
expect <<EOF
      set timeout 100
      spawn mysql -uroot -p
      expect "Enter password:" { send "${cur_pswd}\r" }
      expect "Ma" { send "set password for ${db_user}@localhost=password('${db_pswd}');\r" }
      expect "Ma" { send "grant all on *.* to ${db_user}@'${master}' identified by '${db_pswd}';\r" }
      expect "Ma" { send "flush privileges;\r" }
      expect "Ma" { send "exit;\r" }
      expect eof
EOF
    
    # 设置utf-8字符编码，并重启mariadb
    \cp /etc/my.cnf /etc/my.cnf_origin_backup
    \cp /etc/my.cnf.d/mysql-clients.cnf /etc/my.cnf.d/mysql-clients.cnf_origin_backup
    if [[ "${os}" != openEuler* ]]; then
        \cp /etc/my.cnf.d/client.cnf /etc/my.cnf.d/client.cnf_origin_backup
    fi

    add_para "skip-character-set-client-handshake" "" /etc/my.cnf "mysqld"
    add_para "collation-server" "utf8_unicode_ci" /etc/my.cnf "mysqld"
    add_para "character-set-server" "utf8" /etc/my.cnf "mysqld"
    add_para "init_connect" "'SET NAMES utf8'" /etc/my.cnf "mysqld"
    add_para "init_connect" "'SET collation_connection = utf8_unicode_ci'" /etc/my.cnf "mysqld"

    if [[ "${os}" != openEuler* ]]; then
        add_para "default-character-set" "utf8" /etc/my.cnf.d/client.cnf "client"
    fi

    add_para "default-character-set" "utf8" /etc/my.cnf.d/mysql-clients.cnf "mysql"

    # 重启mariadb
    systemctl restart mariadb
}

# 默认脚本在server1节点执行，当不使用ssh远程调用命令，即默认在server1执行该命令

# 下载安装包
if [ "${is_online}" == "true" ]; then                
    if ! bash "${tool_root_dir}"/bin/download/download.sh; then                        
        echo "Download deps fail!"                   
        exit 1                                       
    fi                                               
fi

# 解压压缩包
tar -zxf "${tool_root_dir}"/deps/"${platform}"/"${hive_version}"/"${package}" -C "${hive_dir}"

# 建立软链接
ln -s "${hive_dir}"/"${package%.tar*}" "${hive_dir}"/hive

# 安装mariadb
install_mariadb

# 替换hive配置文件
modify_conf "${hadoop_home}"

# 移动jdbc driver包到hive lib目录
\cp "${tool_root_dir}"/deps/"${platform}"/"${hive_version}"/"${jdbc_driver}" "${hive_dir}"/"${package%.tar*}"/lib

# 创建Hive数据存放目录
"${hadoop_home}"/bin/hadoop fs -mkdir /tmp
"${hadoop_home}"/bin/hadoop fs -mkdir -p /user/hive/warehouse
"${hadoop_home}"/bin/hadoop fs -chmod +w /tmp
"${hadoop_home}"/bin/hadoop fs -chmod +w /user/hive/warehouse

# 初始化schema
"${hive_dir}"/"${package%.tar*}"/bin/schematool -initSchema -dbType mysql

# 启动hive集群
bash "${tool_root_dir}"/bin/switch/start.sh



#相关配置目录
mkdir -p /usr/local/hive/log/
touch /usr/local/hive/log/hiveserver.log
touch /usr/local/hive/log/hiveserver.err
nohup hiveserver2 1>/usr/local/hive/log/hiveserver.log 2>/usr/local/hive/log/hiveserver.err &
