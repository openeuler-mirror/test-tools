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

if [ X"${1}" == "X" ]; then
    tool_root_dir=$(cd "$(dirname "$0")"/.. || exit 1;pwd)
else
    tool_root_dir=$1
fi

remote_script_dir=${tool_root_dir}/remote
deps_dir=${tool_root_dir}/deps
source "${tool_root_dir}"/bin/remote.sh
source "${tool_root_dir}"/conf/config

check_add_umask_script=${remote_script_dir}/check_add_umask.sh
firewalld_close_script=${remote_script_dir}/firewalld_close.sh
hostname_deploy_script=${remote_script_dir}/hostnamectl_deploy.sh
yum_deploy_script=${remote_script_dir}/yum_local_source_deploy.sh
jdk_install_script=${remote_script_dir}/openjdk_install.sh
chrony_synchronnize_script=${remote_script_dir}/config_chrony.sh


rpm_file_dir=${deps_dir}/RPMS
os_iso=${deps_dir}/${os_iso}
jdk_package=${deps_dir}/${jdk_package}

basic_environment_deploy() {
    if [[ ${arch} != "aarch64" ]] && [[ ${arch} != "x86_64" ]]; then
        echo -e "\033[42;30m ====================Unsupported arch: ${arch}==================== \033[0m"
    fi

    # 安装 wget
    yum install expect bc tar wget -y
    # 下载合适的os镜像、jdk、rpm文件
    if [ "${is_online}" == "true" ]; then
        if ! bash "${tool_root_dir}"/bin/download.sh; then
            echo "Download deps fail!"
            exit 1
        fi
    fi


    # server节点创建ssh私钥
    ssh_create_key

    # 遍历ip_list文件，建立server节点到所有集群节点的免密登陆设置
    if [ "${ip_list:0:1}" != '/' ]; then
        ip_list=${tool_root_dir}/${ip_list}
    fi
    cat "${ip_list}" | while read -r line
    do
        ip=$(echo "${line}" | cut -d" " -f1)
        
        # copy ssh_id
        ssh_id_copy "${ip}" "${user}" "${passwd}"
    done

    server_ip=''
    # 遍历ip_list文件，关闭所有集群节点的防火墙 & 修改主机名 & 设置yum本地源 & 安装jdk & 配置ntp
    # 注意：exec 3<filename 是为了解决filename数字提前被ssh命令读走，导致无法正确循环的问题
    exec 3<"${ip_list}"
    while read -r line <&3
    do
        ip=$(echo "${line}" | cut -d" " -f1)
        hostname=$(echo "${line}" | cut -d" " -f2)
        
       # install deps
       run_remote  "yum install expect bc tar -y" "${ip}" "${passwd}" "${user}"

       # 增加umask 0022命令至/etc/profile，使得后续创建目录都是755权限
       check_add_umask "${ip}" "${user}" "${passwd}" "${check_add_umask_script}"

       # 关闭${ip}节点的防火墙
       firewalld_close "${ip}" "${user}" "${passwd}" "${firewalld_close_script}"

       # 修改${ip}节点的主机名为${hostname}
       hostname_deploy "${hostname}" "${ip}" "${user}" "${passwd}" "${hostname_deploy_script}" "${ip_list}"
   
       # 设置yum本地源
       yum_local_source_deploy "${ip}" "${user}" "${passwd}" "${yum_deploy_script}" "${os_iso}" "${yum_mount_path}" "${local_iso_flag}"

       # 安装jdk
 #      jdk_install "${ip}" "${user}" "${passwd}" "${jdk_install_script}" "${jdk_package}" "${jdk_name}" "${target_path}"
       if [ "${jdk_install_mode}" = "tar_pack" ];then
          jdk_install "${ip}" "${user}" "${passwd}" "${jdk_install_script}" "${jdk_package}" "${jdk_name}" "${target_path}"
        else
           run_remote "yum  install java-1.8.0* -y" "${ip}" "${passwd}" "${user}"
        fi
        # 配置chrony, 第一个读取的ip默认作为server_ip，即ntp server节点
        if [ X"${server_ip}" == "X" ]; then
            server_ip=${ip}
        fi
        chrony_install_configure "${ip}" "${user}" "${passwd}" "${server_ip}" "${chrony_synchronnize_script}"

    done

    # 建立server到所有集群节点hostname的免密登陆
    hostname_ssh
}

hostname_ssh() {
    if [ "${ip_list:0:1}" != '/' ]; then
            ip_list=${tool_root_dir}/${ip_list}
    fi
    cat ${ip_list} | while read -r line
    do
        hostname=($(echo ${line} | cut -d" " -f2))
        expect <<EOF
            spawn ssh ${hostname} "exit"
            expect {
                "yes/no" { send "yes\r";exp_continue }
            }
EOF
    done

    hostname=0.0.0.0
    expect <<EOF
         spawn ssh ${hostname} "exit"
         expect {
             "yes/no" { send "yes\r";exp_continue }
         }
EOF

}

install_by_rpm() {
    rpm_file_dir=$1

    echo -e "\033[42;30m ====================Install dependency library by rpm==================== \033[0m"
    cd "${rpm_file_dir}"
    filenames=$(ls *.rpm)
    for file in ${filenames}; do
        rpm -ivh "${file}"
    done
}

ssh_create_key() {
    echo -e "\033[42;30m ====================Create ssh id_rsa by command ssh-keygen==================== \033[0m"
     if [ ! -f ~/.ssh/id_rsa ];then
        if ! ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa; then
            echo "Create ssh id_rsa success"
            exit 1
        fi
    else
        echo "The id_rsa has created"
    fi
}

ssh_id_copy() {
    ip=$1
    user=$2
    passwd=$3

    echo -e "\033[42;30m ====================Create password-free login by copying id_rsa to ================== \033[0m"

expect <<EOF
      set timeout 100
      spawn ssh-copy-id ${user}@${ip}
      expect {
        "yes/no" { send "yes\r";exp_continue }
        "password" { send "${passwd}\r";exp_continue }
      }
EOF
}

check_add_umask() {
    ip=$1
    user=$2
    passwd=$3
    check_add_umask_script=$4

    echo -e "\033[42;30m ====================Chech & add umask to /etc/profile [${ip}]==================== \033[0m"

    send_remote "${check_add_umask_script}" /tmp/"${check_add_umask_script##*/}" "${ip}" "${passwd}" "${user}"

    run_remote "bash /tmp/${check_add_umask_script##*/}" "${ip}" "${passwd}" "${user}"

    delete_remote /tmp/"${check_add_umask_script##*/}" "${ip}" "${passwd}" "${user}"
}

firewalld_close() {
    ip=$1
    user=$2
    passwd=$3
    firewalld_close_script=$4

    echo -e "\033[42;30m ====================Firewall close [${ip}]==================== \033[0m"

    send_remote "${firewalld_close_script}" /tmp/"${firewalld_close_script##*/}" "${ip}" "${passwd}" "${user}"

    run_remote "bash /tmp/${firewalld_close_script##*/}" "${ip}" "${passwd}" "${user}"

    delete_remote /tmp/"${firewalld_close_script##*/}" "${ip}" "${passwd}" "${user}"
}

hostname_deploy() {
    hostname=$1
    ip=$2
    user=$3
    passwd=$4
    hostname_deploy_script=$5
    ip_hostname_file=$6
    
    echo -e "\033[42;30m ====================Hostname deploy & add host to /etc/hosts [${ip}-${hostname}]==================== \033[0m"
    send_remote "${hostname_deploy_script}" /tmp/"${hostname_deploy_script##*/}" "${ip}" "${passwd}" "${user}"
    send_remote "${ip_hostname_file}" /tmp/"${ip_hostname_file##*/}" "${ip}" "${passwd}" "${user}"

    run_remote "bash /tmp/${hostname_deploy_script##*/} ${hostname} /tmp/${ip_hostname_file##*/}" "${ip}" "${passwd}" "${user}"

    delete_remote /tmp/"${firewalld_close_script##*/}" "${ip}" "${passwd}" "${user}"
    delete_remote /tmp/"${ip_hostname_file##*/}" "${ip}" "${passwd}" "${user}"
}

yum_local_source_deploy() {
    ip=$1
    user=$2
    passwd=$3
    yum_deploy_script=$4
    os_iso=$5
    yum_mount_path=$6
    local_iso_flag=$7

    echo -e "\033[42;30m ====================Yum local source deploy [${ip}]==================== \033[0m"

    if [ "${local_iso_flag}" == "true" ]; then
        send_remote "${os_iso}" /root/"${os_iso##*/}" "${ip}" "${passwd}" "${user}"

        send_remote "${yum_deploy_script}" /tmp/"${yum_deploy_script##*/}" "${ip}" "${passwd}" "${user}"

        run_remote "bash /tmp/${yum_deploy_script##*/} /root/${os_iso##*/} ${yum_mount_path}" "${ip}" "${passwd}" "${user}"

        delete_remote /tmp/"${yum_deploy_script##*/}" "${ip}" "${passwd}" "${user}"
    fi
}

jdk_install() {
    ip=$1
    user=$2
    passwd=$3
    jdk_install_script=$4
    jdk_package=$5
    jdk_name=$6
    target_path=$7

    echo -e "\033[42;30m ====================Openjdk install [${ip}]==================== \033[0m"

    send_remote "${jdk_install_script}" /tmp/"${jdk_install_script##*/}" "${ip}" "${passwd}" "${user}"
    send_remote "${jdk_package}" /tmp/"${jdk_package##*/}" "${ip}" "${passwd}" "${user}"

    run_remote "bash /tmp/${jdk_install_script##*/} /tmp/${jdk_package##*/} ${jdk_name} ${target_path}" "${ip}" "${passwd}" "${user}"

    delete_remote /tmp/"${jdk_install_script##*/}" "${ip}" "${passwd}" "${user}"
}

chrony_install_configure() {
    ip=$1
    user=$2
    passwd=$3
    server_ip=$4
    chrony_synchronnize_script=$5

    
    echo -e "\033[42;30m ==================== chrony config [${ip}]==================== \033[0m"
    send_remote "${chrony_synchronnize_script}" /tmp/"${chrony_synchronnize_script##*/}" "${ip}" "${passwd}" "${user}"
    run_remote "bash /tmp/${chrony_synchronnize_script##*/} ${server_ip}" "${ip}" "${passwd}" "${user}"
    delete_remote /tmp/"${chrony_synchronnize_script##*/}" "${ip}" "${passwd}" "${user}"
}


