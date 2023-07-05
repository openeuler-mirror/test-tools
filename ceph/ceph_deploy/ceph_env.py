#!/usr/bin/env python3
# -*- * coding: utf-8 -*-
import math
import os.path
import re
import time
from pathlib import Path
from threading import Thread

from multiprocessing import Process

import yaml
import paramiko


current_path = Path(__file__).cwd()


class BasePrepare(object):
    def __init__(self, cluster_conf, node_info, config_info):
        self.cluster_conf = cluster_conf
        self.ceph_common = cluster_conf["ceph_common"]
        self.node_info = node_info
        self.config_info = config_info
        self.username = node_info.get("username") or self.ceph_common.get("username", "root")
        self.password = node_info.get("password") or self.ceph_common["password"]
        self.port = node_info.get("port") or self.ceph_common.get("port", 22)

        self.ssh = self.open_ssh(node_info["manager_ip"],
                                 self.username, self.password, self.port)

        log_dir = current_path.joinpath("logs")
        log_dir.mkdir(exist_ok=True)
        self.log_file = log_dir.joinpath(
            "{}.log".format(node_info["hostname"]))
        self.f_log = open(self.log_file, "w")
        self.step = 0
        self.hosts_info_list = []
        self.manager_ip_list = []
        self.data_disk_list = []
        self.nvme_disk_list = []
        self.finished = False
        self.prox_cmd = ""
        self.python = ""
        self.pip = ""
        self.install_info = {
            "mon_list": [],
            "mgr_list": [],
            "osd_list": [],
            "rgw_list": [],
            "mds_list": [],
        }
        self.nodes_password = {}
        self.init_need_parameter()

        # get system info
        self.system_name = self.ssh_cmd_get_first_line("cat /etc/system-release|awk '{print $1}'").lower()
        self.arch = self.ssh_cmd_get_first_line("arch").lower()
        if self.system_name == "centos":
            self.os_version = self.ssh_cmd_get_first_line("cat /etc/system-release|awk '{print $4}'")
        elif self.system_name == "openeuler":
            self.os_version = self.ssh_cmd_get_first_line("cat /etc/system-release|awk '{print $3}'")
            os_lts = self.ssh_cmd_get_first_line("cat /etc/system-release|awk '{print $4}'")
            if '(' in os_lts:
                self.os_lts = os_lts.split("(")[1].split(")")[0]
            else:
                if os_lts:
                    self.os_lts = os_lts
        elif self.system_name == "anolis":
            self.os_version = self.ssh_cmd_get_first_line("cat /etc/system-release|awk '{print $4}'")
        else:
            self.os_version = ""

        self.remote_adapter_dir = "/home/ceph/adapter/"
        self.bcache_size = None

    def  init_need_parameter(self):
        servers = self.cluster_conf.get("servers", {})
        clients = self.cluster_conf.get("clients", {})

        for server_name, server_info in servers.items():
            self.hosts_info_list.append((server_name, server_info["public_ip"]))
            self.manager_ip_list.append(server_info["manager_ip"])
            self.nodes_password[server_info["manager_ip"]] = {
                "username": server_info.get("username") or self.ceph_common.get("username", "root"),
                "password": server_info.get("password") or self.ceph_common["password"],
                 "port": server_info.get("port") or self.ceph_common.get("port", 22)
            }
            if server_info["mon"].upper() in ["Y", "YES"]:
                self.install_info["mon_list"].append(server_name)
            if server_info["mgr"].upper() in ["Y", "YES"]:
                self.install_info["mgr_list"].append(server_name)
            if server_info["osd"].upper() in ["Y", "YES"]:
                self.install_info["osd_list"].append(server_name)
            if server_info["mds"].upper() in ["Y", "YES"]:
                self.install_info["mds_list"].append(server_name)
            if server_info["rgw"].upper() in ["Y", "YES"]:
                self.install_info["rgw_list"].append(server_name)
        for client_name, client_info in clients.items():
            self.hosts_info_list.append((client_name, client_info["public_ip"]))
            self.manager_ip_list.append(client_info["manager_ip"])
            self.nodes_password[client_info["manager_ip"]] = {
                "username": client_info.get("username") or self.ceph_common.get("username", "root"),
                "password": client_info.get("password") or self.ceph_common["password"],
                 "port": client_info.get("port") or self.ceph_common.get("port", 22)
            }
        # get disk info
        data_disk = self.node_info.get("data_disk") or self.ceph_common.get("data_disk")

        if not data_disk:
            data_disk = self.ssh_exec_cmd("lsblk|grep disk |grep -v nvme"
                                        "|grep -v $(lsblk|grep /boot/efi|awk '{print $1}'"
                                        "|grep -Eo '[a-zA-Z]+')|grep sd|awk '{print $1}'").strip().split("\n")
        system_disk = self.ssh_cmd_get_first_line(
            "lsblk|grep /boot/efi|awk '{print $1}'|grep -Eo '[a-zA-Z]+'")

        data_disk_list = self.data_to_list(data_disk)
        if system_disk in data_disk_list:
            self.error(f"system disk {system_disk} in data_disk")
            raise Exception(f"system disk {system_disk} in data_disk")
        osd_num = self.node_info.get("osd_num") or self.ceph_common.get("osd_per_node_num")

        if osd_num:
            data_disk_list = data_disk_list[:int(osd_num)]
        self.data_disk_list = data_disk_list
        self.info(self.data_disk_list)
        # nvme disk
        nvme_disk = self.node_info.get("nvme_disk") or self.ceph_common.get("nvme_disk") or []
        self.nvme_disk_list = self.data_to_list(nvme_disk)

        config_proxy = self.config_info.get("proxy")
        if config_proxy:
            self.prox_cmd = 'export http_proxy="{}";export https_proxy="{}"'.format(
                config_proxy["http_proxy"], config_proxy["https_proxy"])

    @staticmethod
    def data_to_list(data):
        data_list = []
        if isinstance(data, list):
            data_list = data
        elif isinstance(data, str):
            if "," in data:
                deal_list = data.split(",")
            elif " " in data:
                deal_list = data.split(" ")
            else:
                deal_list = [data]
            for disk in deal_list:
                data_list.append(disk.strip())
        return data_list

    def close(self):
        self.ssh.close()
        self.f_log.close()

    def is_success(self):
        return self.finished

    @staticmethod
    def open_ssh(node_ip, username, password, port=22):
        ssh = paramiko.SSHClient()
        know_host = paramiko.AutoAddPolicy()
        ssh.set_missing_host_key_policy(know_host)
        ssh.connect(node_ip, port, username, password,
                    allow_agent=False)
        return ssh

    def ssh_exec_cmd(self, cmd, ssh=None):
        if ssh is None:
            ssh = self.ssh
        shell = self.ssh.invoke_shell()
        shell.settimeout(1)
        self.info("exec cmd: {}".format(cmd))
        stdin, stdout, stderr = ssh.exec_command(cmd)
        res, err = stdout.read(), stderr.read()
        result = (res + err).decode("utf-8", "ignore")
        self.info("result:{}".format(result))
        return result

    def ssh_cmd_get_first_line(self, cmd, ssh=None):
        return self.ssh_exec_cmd(cmd, ssh).split("\n")[0]

    def info(self, message):
        data = "%s %s" % (
            time.strftime("[INFO] [%Y-%m-%d %H:%M:%S]"),
            message)
        print("\033[1;32;40m%s\033[0m" % ("[{}]".format(self.node_info["hostname"]) + data))
        self.f_log.write(data + "\n")

    def error(self, message):
        data = "%s %s" % (
            time.strftime("[ERROR] [%Y-%m-%d %H:%M:%S]"),
            message)
        print("\033[1;31;40m%s\033[0m" % ("[{}]".format(self.node_info["hostname"]) + data))
        self.f_log.write(data + "\n")

    def step_increase(self):
        self.step += 1
        self.info("current step {}".format(self.step))

    def exec_func_increase_step(self, func):
        self.info("exec {} function".format(func.__name__))
        for _ in range(3):
            flag = func()
            if flag is True:
                self.step_increase()
                break
            time.sleep(10)

    def check_command_is_existed(self, command):
        flag = self.ssh_cmd_get_first_line(
            "command -v {} &> /dev/null;echo $?".format(command))
        if flag == "0":
            return True
        else:
            return False

    def yum_install_package(self, package_name):
        install_cmd = """
{}
yum install -y {} &> /dev/null;echo $?
""".format(self.prox_cmd, package_name)
        flag = self.ssh_cmd_get_first_line(install_cmd)
        if flag == "0":
            self.info("yum install {} success".format(package_name))
            return True
        else:
            self.error("yum install {} failed".format(package_name))
            return True

    def pip_install_package(self, package_name):
        remote_mirror = self.config_info["pip"]["remote_mirror"]
        trusted_host = self.config_info["pip"]["trusted_host"]
        install_cmd = r"""
{}
{} install --trusted-host {} -i {} {} &> /dev/null;echo $?""".format(
            self.prox_cmd,  self.pip, trusted_host, remote_mirror, package_name)
        flag = self.ssh_cmd_get_first_line(install_cmd)
        if flag == "0":
            self.info("{} install {} success".format(self.pip, package_name))
            return True
        else:
            self.error("{} install {} failed".format(self.pip, package_name))
            return True 

    def check_install_python(self):
        python = "python2"
        pip = "pip2"

        if self.check_command_is_existed(python) is True:
            self.python = python
        else:
            # install python
            if self.yum_install_package(python) is False:
                return False
            self.python = python

        if self.check_command_is_existed(pip) is True:
            self.pip = pip
        else:
            # install pip
            if self.yum_install_package(f"{python}-pip") is False:
                return False
            self.pip = pip
        # upgrade pip
        self.pip_install_package("--upgrade pip")
        return True

    def check_netcard_is_up(self, netcard):
        is_up = self.ssh_cmd_get_first_line(
            "ip a|grep {}|grep 'state UP' &> /dev/null ;echo $?".format(netcard))

        if is_up == "0":
            self.info("{} is up: {}".format(netcard, is_up))
            return True
        else:
            self.error("{} is down".format(netcard))
            return False

    def mac_to_netcard(self, mac_info):
        netcard_list = []
        mac_list = self.data_to_list(mac_info)
        for mac in mac_list:
            netcard = self.ssh_cmd_get_first_line(
                "ip a|grep -B 1 %s|head -n 1|awk -F ': ' '{print $2}'" % mac)
            if not netcard:
                raise Exception(f"{mac} mac not existed")
            netcard_list.append(netcard)
        return netcard_list

    def set_network(self):
        bond_index = 0
        if self.node_info.get("public_mac"):
            public_netcard = self.mac_to_netcard(self.node_info.get("public_mac"))
        else:
            public_netcard = self.data_to_list(self.node_info.get("public_netcard"))
        public_ip = self.node_info["public_ip"]
        public_gateway = self.ceph_common["public_gateway"]
        public_mask = self.ceph_common["public_mask"]

        if self.node_info.get("cluster_mac"):
            cluster_netcard = self.mac_to_netcard(self.node_info.get("cluster_mac"))
        else:
            cluster_netcard = self.data_to_list(self.node_info.get("cluster_netcard"))
        cluster_ip = self.node_info.get("cluster_ip")
        cluster_gateway = self.ceph_common["cluster_gateway"]
        cluster_mask = self.ceph_common["cluster_mask"]

        if len(public_netcard) < 1:
            self.error("public_netcard less than 1")
            return False
        # check netcard
        for card in public_netcard:
            if self.check_netcard_is_up(card) is False:
                self.error("public netcard {} is not up")
                return False
        for card in cluster_netcard:
            if self.check_netcard_is_up(card) is False:
                self.error("cluster netcard {} is not up")
                return False

        if cluster_ip and cluster_netcard:
            if self.set_cluster_public_ip(
                    public_netcard, cluster_netcard, public_ip, cluster_ip,
                    bond_index, public_mask, public_gateway,
                    cluster_mask, cluster_gateway) is False:
                return False
        else:
            if self.set_public_ip(public_netcard, public_ip, public_mask,
                                  public_gateway, bond_index) is False:
                return False
        return True

    def set_cluster_public_ip(self, public_netcard, cluster_netcard,
                              public_ip, cluster_ip, bond_index, public_mask,
                              public_gateway, cluster_mask, cluster_gateway):
        if len(public_netcard) >1 and len(cluster_netcard) > 1:
            # config bond
            if set(public_netcard) == set(cluster_netcard):
                # config one bond
                if public_ip == cluster_ip:
                    ip_list = [public_ip]
                else:
                    ip_list = [public_ip, cluster_ip]
                if self.set_bond(bond_index, public_netcard, ip_list) is False:
                    return False
                bond_index += 1
            else:
                # config public bond
                if self.set_bond(bond_index, public_netcard, [public_ip]) is False:
                    self.error("{} set public bond failed".format(public_netcard))
                    return False
                bond_index += 1
                # config cluster bond
                if self.set_bond(bond_index, cluster_netcard, [cluster_ip]) is False:
                    self.error("{} set cluster bond failed".format(cluster_netcard))
                    return False
                bond_index += 1
        else:
            if len(public_netcard) > 1:
                # config public bond
                if self.set_bond(bond_index, public_netcard, [public_ip]) is False:
                    self.error("{} set public bond failed".format(public_netcard))
                    return False
                bond_index += 1
            else:
                if self.set_ip(public_netcard[0], public_ip, public_mask, public_gateway) is False:
                    self.error("{} set public ip failed".format(public_netcard[0]))
                    return False

            if len(cluster_netcard) > 1:
                # config cluster bond
                if self.set_bond(bond_index, cluster_netcard, [cluster_ip]) is False:
                    self.error("{} set cluster bond failed".format(cluster_netcard))
                    return False
                bond_index += 1
            else:
                if self.set_ip(cluster_netcard[0], public_ip, cluster_mask, cluster_gateway) is False:
                    self.error("{} set cluster ip failed".format(cluster_netcard[0]))
                    return False
        return True

    def set_public_ip(self, public_netcard, public_ip, public_mask,
                      public_gateway, bond_index):
        if len(public_netcard) > 1:
            # config public bond
            if self.set_bond(bond_index, public_netcard, [public_ip]) is False:
                self.error("{} set public bond failed".format(public_netcard))
                return False
            bond_index += 1
        else:
            if self.set_ip(public_netcard[0], public_ip, public_mask, public_gateway) is False:
                self.error("{} set public ip failed".format(public_netcard[0]))
                return False

    def set_ip(self, net_card, ip_addr, net_mask, gateway):
        set_ip_cmd = r"""
net_card=%s
ip_addr=%s
net_mask=%s
gateway=%s
filename=/etc/sysconfig/network-scripts/ifcfg-${net_card}
bak_file=/etc/sysconfig/network-scripts/bak-${net_card}
if [[ -f ${filename} ]];then
cp ${filename} ${bak_file}
cat ${filename}|grep IPADDR &>/dev/null
if [[ $? -ne 1 ]];then
    sed -i "s/IPADDR.*/IPADDR=${ip_addr}/g" ${filename}
else
    echo "IPADDR=${ip_addr}" >> ${filename}
fi
cat ${filename}|grep NETMASK &>/dev/null
if [[ $? -ne 1 ]];then
    sed -i "s/NETMASK.*/NETMASK=${net_mask}/g" ${filename}
else
    echo "NETMASK=${net_mask}" >> ${filename}
fi

cat ${filename}|grep GATEWAY &>/dev/null
if [[ $? -ne 1 ]];then
    sed -i "s/GATEWAY.*/GATEWAY=${gateway}/g" ${filename}
else
    echo "GATEWAY=${gateway}" >> ${filename}
fi

cat ${filename}|grep BOOTPROTO &>/dev/null
if [[ $? -ne 1 ]];then
    sed -i "s/BOOTPROTO.*/BOOTPROTO=static/g" ${filename}
else
    echo "BOOTPROTO=static" >> ${filename}
fi

cat ${filename}|grep ONBOOT &>/dev/null
if [[ $? -ne 1 ]];then
    sed -i "s/ONBOOT.*/ONBOOT=yes/g" ${filename}
else
    echo "ONBOOT=yes" >> ${filename}
fi

cat ${filename}|grep MTU &>/dev/null
if [[ $? -ne 1 ]];then
    sed -i "s/MTU.*/MTU=9000/g" ${filename}
else
    echo "MTU=9000" >> ${filename}
fi
else
ifconfig ${net_card} ${ip_addr}/24
cat >${filename} <<EOF
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
DEVICE=${net_card}
ONBOOT=yes
NAME=${net_card}
IPADDR=${ip_addr}
NETMASK=${net_mask}
GATEWAY=${gateway}
IPV6_PRIVACY=no
MTU=9000
EOF
fi
""" % (net_card, ip_addr, net_mask, gateway)
        # down netcard
        self.ssh_exec_cmd("nmcli con down {}".format(net_card))
        self.ssh_exec_cmd(set_ip_cmd)
        self.ssh_exec_cmd("nmcli con reload {}".format(net_card))

        self.ssh_exec_cmd("nmcli con up {} &>/dev/null;echo $?".format(net_card))
        time.sleep(3)
        if self.ssh_cmd_get_first_line(
                "ip a|grep {} &>/dev/null;echo $?".format(ip_addr)) == "0":
            self.info("set {} {} success".format(net_card, ip_addr))
            return True
        else:
            self.info("set {} {} failed".format(net_card, ip_addr))
            return False

    def set_bond(self, bond_index, net_card_list, ip_addr_list):
        bond_name = "auto_bond{}".format(bond_index)
        set_bond_cmd = r"""
bond_name=%s
net_card_list=(%s)
ip_addr_list=(%s)
bond_file=/etc/sysconfig/network-scripts/ifcfg-${bond_name}
cat >${bond_file} <<EOF
DEVICE=${bond_name}
Type=Bond
BONDING_MASTER=yes
BOOTPROTO=static
ONBOOT=yes
BONDING_OPTS="mode=6 miimon=100 xmit_hash_polic=layer3+4"
MTU=9000
EOF

for ((i=0;i<${#ip_addr_list[*]};i++));do
    echo "IPADDR${i}=${ip_addr_list[i]}" >> ${bond_file}
done

for ((i=0;i<${#net_card_list[*]};i++));do
nmcli con down ${net_card_list[i]}
nic_file=/etc/sysconfig/network-scripts/ifcfg-${net_card_list[i]}
bak_file=/etc/sysconfig/network-scripts/bak-ifcfg-${net_card_list[i]}
cp ${nic_file} ${bak_file}
cat > ${nic_file} <<EOF
TYPE=Ethernet
BOOTPROTO=none
IPV6INIT=no
DEVICE=${net_card_list[i]}
ONBOOT=yes
MASTER=${bond_name}
SLAVE=yes
EOF
nmcli con up ${net_card_list[i]}
done
""" % (bond_name, " ".join(net_card_list), " ".join(ip_addr_list))
        self.ssh_exec_cmd(set_bond_cmd)
        self.ssh_exec_cmd("nmcli con reload")
        time.sleep(3)
        for ip_addr in ip_addr_list:
            for _ in range(3):
                if self.ssh_cmd_get_first_line(
                        "ip a|grep {} &>/dev/null;echo $?".format(ip_addr)) == "0":
                    break
                time.sleep(3)
            else:
                self.error("set {} {} failed".format(bond_name, ip_addr))
                return False
        else:
            self.info("set {} {} {} success".format(bond_name, net_card_list, ip_addr_list))
            return True

    def close_firewall(self):
        firewall_open = self.ceph_common["firewall_open"].upper()
        if firewall_open not in ["Y", "YES"]:
            # close firewall
            self.ssh_exec_cmd("systemctl stop firewalld && systemctl disable firewalld")
            if self.ssh_cmd_get_first_line("systemctl status firewalld|grep Active|awk '{print $2}'") == "inactive":
                self.info("close firewall success")
                return True
            else:
                self.error("close firewall failed")
                return False

    def close_selinux(self):
        self.ssh_exec_cmd("setenforce 0")
        self.ssh_exec_cmd(" sed -i 's/SELINUX=.*/SELINUX=disabled/g' /etc/selinux/config")
        selinux_value = self.ssh_cmd_get_first_line("getenforce")
        if selinux_value in ["Disabled"]:
            self.info("close selinux success")
            return True
        else:
            self.info("close selinux failed")
            return True

    def change_umask(self):
        change_cmd = """
if [[ "$(umask)" != "0022" ]];then
echo "umask 0022" >> /etc/bashrc
source /etc/bashrc
fi
"""
        self.ssh_exec_cmd(change_cmd)
        if self.ssh_cmd_get_first_line("umask") == "0022":
            self.info("change umask success")
            return True
        else:
            self.error("change umask failed")
            return False

    def set_hostname(self):
        hostname = self.node_info["hostname"]
        self.ssh_exec_cmd(
            "hostnamectl --static set-hostname {}".format(hostname))
        if self.ssh_cmd_get_first_line("hostname") == hostname:
            self.info("set hostname success")
            return True
        else:
            self.error("set hostname failed")
            return False

    def add_host_file(self):
        # backup /etc/hosts
        self.ssh_exec_cmd("mv /etc/hosts  /etc/hosts-bak")
        add_hosts_cmd = """
cat > /etc/hosts <<EOF
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
"""
        for info in self.hosts_info_list:
            add_hosts_cmd += """\n{} {}""".format(info[1], info[0])
        else:
            add_hosts_cmd += "\nEOF"
        self.ssh_exec_cmd(add_hosts_cmd)
        return True

    def replace_os_repo_file(self):
        # modify yum.conf
        modify_yum_conf = """
        sed -i "s/gpgcheck=1/gpgcheck=0/g" /etc/yum.conf
        cat /etc/yum.conf|grep sslverify
        if [ $? -ne 0 ];then
            echo "sslverify=false" >> /etc/yum.conf
        else
            sed -i "s/sslverify.*/sslverify=false/g" /etc/yum.conf
        fi
        cat /etc/yum.conf|grep deltarpm
        if [ $? -ne 0 ];then
            echo "deltarpm=0" >> /etc/yum.conf
        else
            sed -i "s/deltarpm.*/deltarpm=0/g" /etc/yum.conf
        fi
        """
        self.ssh_exec_cmd(modify_yum_conf)
        # repo add priority
        self.ssh_exec_cmd("sed -i '/gpgcheck=.*/a priority=1' /etc/yum.repos.d/*.repo")

        if self.ceph_common.get("replace_system_repo").upper() not in ["Y", "YES"]:
            return True

        if self.system_name == "openeuler":
            if hasattr(self, "os_lts"):
                local_system_repo = current_path.joinpath(
                    "conf", "repo_file", "{}_{}_{}_{}.repo".format(
                        self.system_name, self.os_version, self.os_lts, self.arch))
            else:
                local_system_repo = current_path.joinpath(
                    "conf", "repo_file", "{}_{}_{}.repo".format(
                        self.system_name, self.os_version, self.arch))
        elif self.system_name == "centos":
            big_version = self.os_version.split(".")[0]
            local_system_repo = current_path.joinpath(
                "conf", "repo_file", "{}{}_{}.repo".format(
                    self.system_name, big_version, self.arch))
        else:
            local_system_repo = current_path.joinpath(
                "conf", "repo_file", "{}_{}_{}.repo".format(
                    self.system_name, self.os_version, self.arch))

        if not local_system_repo.exists():
            self.error(f"{local_system_repo} not existed")
            local_system_repo = str(local_system_repo).replace(f"_{self.arch}", "")
            if not os.path.exists(local_system_repo):
                self.error(f"{local_system_repo} not existed")
                return True
            else:
                self.info(f"using {local_system_repo}")
        # bcakup repo and upload repo
        self.ssh_exec_cmd("mkdir -p /etc/yum.repos.d/auto_backup/")
        self.ssh_exec_cmd("mv  /etc/yum.repos.d/*.repo /etc/yum.repos.d/auto_backup/")
        sftp = self.ssh.open_sftp()
        sftp.put(local_system_repo, f"/etc/yum.repos.d/{self.system_name}.repo")
        sftp.close()

        return True

    def config_no_password(self):
        if self.check_command_is_existed("expect") is False:
            if self.yum_install_package("expect") is False:
                return False

        # generate id_rsa
        self.ssh_exec_cmd("ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ''")
        # client ssh-copy-id
        for manager_ip in self.manager_ip_list:
            node_password = self.nodes_password[manager_ip]
            copy_id_cmd = r"""
/usr/bin/expect <<EOF
            set timeout 120
            spawn ssh-copy-id -p %s %s@%s
            expect {
                    "*yes/no" { send "yes\r";exp_continue }
                    "*password:" { send "%s\r" }
            }
            expect eof
EOF
""" % (node_password["port"], node_password["username"],
                manager_ip, node_password["password"])
            self.ssh_exec_cmd(copy_id_cmd)

        # ssh input yes
        for host_info in self.hosts_info_list:
            input_yes_cmd = r"""
/usr/bin/expect <<EOF
            set timeout 120
            spawn ssh %s "exit"
            expect {
                          "*yes/no" { send "yes\r";exp_continue }
            }
            expect eof
EOF
""" % (host_info[0])
            self.ssh_exec_cmd(input_yes_cmd)

        # check no password
        for manager_ip in self.manager_ip_list:
            node_password = self.nodes_password[manager_ip]
            check_cmd = "ssh {}@{} -p {} -o PreferredAuthentications" \
                        "=publickey -o StrictHostKeyChecking=no pwd " \
                        "&>/dev/null;echo $?".format(node_password["username"],
                                                     manager_ip, node_password["port"])
            if self.ssh_cmd_get_first_line(check_cmd) != "0":
                self.error("set no password in {} failed".format(manager_ip))
                return False
        return True

    def config_chrony(self):
        # set date
        self.ssh_exec_cmd("date -s '{}'".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        ntp_public_net = '.'.join(self.ceph_common["ntp_server"].split(".")[:2]) + ".0.0/16"
        config_cmd = """
%s
ntp_server=%s
public_net=%s
yum -y install chrony
[[ $? -ne 0 ]] && echo "install chrony failed" && exit 1
if [[ -f /etc/chrony.conf ]];then
mv /etc/chrony.conf /etc/chrony.conf-bak
ip a show |grep ${ntp_server}
if [ $? -eq 0 ];then
cat > /etc/chrony.conf <<EOF
allow ${public_net}
local stratum 5
server ${ntp_server} iburst
makestep 1.0 3
EOF
else
cat > /etc/chrony.conf <<EOF
server ${ntp_server} iburst
makestep 1.0 3
EOF
fi
systemctl start chronyd.service
systemctl enable chronyd.service
timedatectl set-timezone Asia/Shanghai
chronyc -a makestep
timedatectl set-ntp true
systemctl restart chronyd.service
hwclock -w
fi
""" % (self.prox_cmd, self.ceph_common["ntp_server"], ntp_public_net)
        self.ssh_exec_cmd(config_cmd)
        if self.ssh_cmd_get_first_line("systemctl status chronyd|"
                                       "grep Active|awk '{print $2}'") == "active":
            self.info("config chrony success")
            return True
        else:
            self.error("config chrony failed")
            return False

    def local_ceph_rpm_repo(self):
        # check command createrepo, tar, expect
        for command in ["createrepo", "tar", "expect"]:
            if self.check_command_is_existed(command) is False:
                if self.yum_install_package(command) is False:
                    return False

        # upload local rpm
        upload_path = "/home/local_ceph_rpm/"
        self.ssh_exec_cmd("mkdir -p {}".format(upload_path))
        local_rpm_path = self.ceph_common["local_rpm_path"]
        rpm_package_name = Path(local_rpm_path).name
        sftp = self.ssh.open_sftp()
        sftp.put(local_rpm_path, upload_path + rpm_package_name)
        sftp.close()

        parameter = """
upload_path=%s
local_rpm_path=%s
""" % (upload_path, local_rpm_path)

        config_local_repo_cmd = parameter + """
cd ${upload_path}
package_name=$(basename "${local_rpm_path}")
tar -xzvf "${package_name}"
if [ $? != 0 ];then
    echo "[ERROR] tar -xzvf ${package_name} failed"
    exit
fi
cd ${package_name%.tar.gz}
createrepo .
cat > /etc/yum.repos.d/local_ceph.repo <<EOF
[local_ceph]
name=local_ceph
baseurl=file://${upload_path}/${package_name%.tar.gz}
gpgcheck=0
enabled=1
priority=1
EOF
"""
        self.ssh_exec_cmd(config_local_repo_cmd)
        # check local_ceph.repo is existed
        if self.ssh_cmd_get_first_line("ls  /etc/yum.repos.d/"
                                       "local_ceph.repo &>/dev/null;echo $?") != "0":
            self.error("local_ceph.repo not existed")
            return False
        if self.ssh_cmd_get_first_line("{};yum makecache &>/dev/null;"
                                       "echo $?".format(self.prox_cmd)) == "0":
            self.info("local ceph rpm config success")
            return True
        else:
            self.error("local ceph rpm config failed")
            return False

    def config_ceph_repo(self):
        sftp = self.ssh.open_sftp()
        if self.system_name == "openeuler":
            arch_fedora = current_path.joinpath("conf", "repo_file", "arch_fedora.repo")
            sftp.put(arch_fedora, "/etc/yum.repos.d/arch_fedora.repo")
        if self.system_name == "centos":
            if self.ssh_cmd_get_first_line(
                    "rpm -qa|grep epel &>/dev/null;echo $?") != "0":
                if self.yum_install_package("epel-release") is False:
                    return False
            else:
                self.ssh_exec_cmd("yum remove -y epel-release")
                if self.yum_install_package("epel-release") is False:
                    return False

        if self.ceph_common.get("local_rpm").upper() in ["Y", "YES"]:
            if self.local_ceph_rpm_repo() is False:
                return False
        else:
            ceph_repo = current_path.joinpath("conf", "repo_file", "ceph.repo")
            sftp.put(ceph_repo, "/etc/yum.repos.d/ceph.repo")
        sftp.close()

        self.ssh_exec_cmd(
            "sed -i 's/gpgcheck=1/gpgcheck=0/g' /etc/yum.repos.d/*.repo")
        return True

    def ceph_dependent(self):
        # install librados2
        ceph_version = self.ceph_common["ceph_version"]
        if self.yum_install_package("librados2-{}".format(
                ceph_version)) is False:
            return True
        # install ceph
        yum_args = ""
        if self.system_name == "openeuler":
            if self.os_version == "22.03" and self.os_lts == "LTS":
                yum_args = "--allowerasing"

        if self.ssh_cmd_get_first_line(
                "yum install -y ceph-{} {} &>/dev/null;echo $?".format(
                    ceph_version, yum_args)) != "0":
            self.error("ceph install failed")
            return True

        self.yum_install_package("openssl-devel")

        self.pip_install_package("werkzeug")
        self.pip_install_package("six")
        self.pip_install_package("requests")
        self.pip_install_package("cherrypy")
        self.pip_install_package("pecan")
        self.pip_install_package("pyOpenSSL")

        if self.pip_install_package("prettytable") is False:
            return False

        if len(self.install_info["rgw_list"]) > 0:
            # install rgw
            if self.yum_install_package("ceph-radosgw-{}".format(
                    ceph_version)) is False:
                return False
        if self.ssh_cmd_get_first_line(
                "ls /etc/ceph &>/dev/null;echo $?") != "0":
            self.ssh_exec_cmd("mkdir -p /etc/ceph")
            self.ssh_exec_cmd("chown ceph:ceph /etc/ceph")

        check_version = self.ssh_cmd_get_first_line("ceph -v|awk '{print $3}'")
        if check_version == ceph_version:
            return True
        else:
            self.error("ceph version {}".format(check_version))
            return False

    def add_ceph_user(self):
        add_cmd = """
cat /etc/group|grep ceph
if [ $? -ne 0 ];then
    echo "ceph:x:167:" >> /etc/group
else
    sed -i "s/^ceph.*/ceph:x:176:/g" /etc/group
fi
cat /etc/passwd|grep ceph
if [ $? -ne 0 ];then
    echo "ceph:x:167:167:Ceph daemons:/var/lib/ceph:/sbin/nologin" >> /etc/passwd
else
    sed -i "s#^ceph.*#ceph:x:167:167:Ceph daemons:/var/lib/ceph:/sbin/nologin#g" /etc/passwd
fi
"""
        self.info("add ceph user")
        self.ssh_exec_cmd(add_cmd)
        return True

    def clean_env(self):
        # kill ceph
        self.ssh_exec_cmd("ps -ef|grep -v grep|grep ceph|grep -v deploy|awk '{print $2}'|xargs -i kill -9 {}")
        # umount ceph osd
        self.ssh_exec_cmd("df -h|grep '/var/lib/ceph/osd'|awk '{print $NF}'|xargs -i umount {}")
        # del ssh path
        self.ssh_exec_cmd("rm -rf ~/.ssh")

    def compatible_adapter(self):
        if self.system_name == "openeuler":
            if hasattr(self, "os_lts"):
                local_adapter_dir = current_path.joinpath(
                    "system_compatible", f"{self.system_name}_{self.os_version}_{self.os_lts}")
            else:
                local_adapter_dir = current_path.joinpath(
                    "system_compatible", f"{self.system_name}_{self.os_version}")

        else:
            local_adapter_dir = current_path.joinpath(
                "system_compatible", f"{self.system_name}_{self.os_version}")
        # local_adapter_dir existed exec adapter script
        if local_adapter_dir.exists():

            self.sftp_upload_dir(local_adapter_dir, self.remote_adapter_dir)
            self.ssh_exec_cmd("cd {};sh adapter.sh run".format(self.remote_adapter_dir))
            if "adapter success" in self.ssh_exec_cmd(
                    "cd {};sh adapter.sh check".format(self.remote_adapter_dir)):
                self.info("compatible adapter success")
            else:
                self.error("compatible adapter failed")
                return False
        return True

    def sftp_upload_dir(self, local_dir, remote_dir):
        sftp = self.ssh.open_sftp()
        all_files = self.get_path_all_file(local_dir)
        for file in all_files:
            relative_path = file.as_posix().split(local_dir.as_posix())[1]

            remote_path = Path(remote_dir + relative_path)
            self.ssh_exec_cmd("mkdir -p {}".format(remote_path.parent.as_posix()))
            sftp.put(file.absolute(), remote_path.as_posix())

    def get_path_all_file(self, local_dir):
        all_files = []
        for path in Path(local_dir).iterdir():
            if path.is_dir():
                all_files.extend(self.get_path_all_file(path))
            else:
                all_files.append(path)
        return all_files


class ServerPrepare(BasePrepare):
    def mkpart_data_disk(self, data_disk_list, osd_per_dev):
        for disk in data_disk_list:
            parameter_cmd = """
disk=%s
osd_per_dev=%s
step_ratio=%s
""" % (disk, osd_per_dev, 100//osd_per_dev)
            mkpart_cmd = parameter_cmd + r"""
dd if=/dev/zero of=/dev/${disk} bs=1K count=3000
parted /dev/${disk} mklabel gpt
for j in $(seq 1 ${osd_per_dev})
do
start_ratio=$(echo ${step_ratio} ${j}|awk '{print $1*($2-1)}')
end_ratio=$(echo ${step_ratio} ${j}|awk '{print $1*$2}')
/usr/bin/expect <<EOF
    set timeout 30
    spawn parted /dev/${disk} mkpart primary ${start_ratio}% ${end_ratio}%
    expect {
            "Yes" { send "yes\r";exp_continue" }
    }
EOF
done
"""
            self.ssh_exec_cmd(mkpart_cmd)
            time.sleep(6)
            check_parted_num = self.ssh_cmd_get_first_line(
                r"lsblk|grep %s|grep part|awk '{print $1}'|grep '%s[0-9]\+'|wc -l" % (disk, disk))
            if check_parted_num != str(osd_per_dev):
                self.error("{} parted error, check_parted_num:{}, need parted nm:{}".format(
                    disk, check_parted_num, osd_per_dev))
                return False
            else:
                self.info("{} parted success".format(disk))
        return True

    def mkpart_db_wal_disk(self, db_wal_disk, parted_num, bcache_size):
        db_size = self.ceph_common.get("db_size", 30)
        wal_size = self.ceph_common.get("wal_size", 50)
        mkpart_unit = self.ceph_common.get("mkpart_unit", "G")
        self.ssh_exec_cmd(f"dd if=/dev/zero of=/dev/{db_wal_disk} bs=1K count=3000")
        parameter_cmd = """
db_wal_disk=%s
parted_num=%s
db_size=%s
wal_size=%s
unit=%s
bcache_size=%s
""" % (db_wal_disk, parted_num, db_size, wal_size, mkpart_unit, bcache_size or 0)
        parted_cmd = parameter_cmd + """
parted /dev/${db_wal_disk} mklabel gpt
index=1
for j in $(seq 1 ${parted_num})
do
start_index=$(echo ${index} ${db_size}|awk '{print $1 + $2}')
end_index=$(echo ${start_index} ${wal_size}|awk '{print $1 + $2}')
parted /dev/${db_wal_disk} mkpart primary ${index}${unit} ${start_index}${unit}
parted /dev/${db_wal_disk} mkpart primary ${start_index}${unit} ${end_index}${unit}
index=${end_index}
done
if [[ "${bcache_size}" != "0" ]];then
for j in $(seq 1 ${parted_num})
do
end_index=$(echo ${index} ${bcache_size}|awk '{print $1 + $2}')
parted /dev/${db_wal_disk} mkpart primary ${index}${unit} ${end_index}${unit}
index=${end_index}
done
fi
"""
        self.ssh_exec_cmd(parted_cmd)
        time.sleep(3)
        check_parted_num = self.ssh_cmd_get_first_line(
            r"lsblk|grep %s|grep part|wc -l" % (db_wal_disk))
        if bcache_size:
            disk_part_num = str(parted_num * 3)
        else:
            disk_part_num = str(parted_num * 2)
        if check_parted_num != disk_part_num:
            self.error("{} parted error, check_parted_num:{}, need parted num:{}".format(
                db_wal_disk, check_parted_num, disk_part_num))
            return False
        else:
            self.info("{} parted success".format(db_wal_disk))
        return True

    def check_disk_is_existed(self, disk):
        if self.ssh_cmd_get_first_line(
                "lsblk|grep {} &>/dev/null;echo $?".format(disk)) != "0":
            self.error("{} disk not existed".format(disk))
            return False
        else:
            return True

    def init_disk(self):
        # vgremove ceph
        self.ssh_exec_cmd("vgs|grep ceph|awk '{print $1}'|xargs -i vgremove -y {}")
        self.ssh_exec_cmd("dmsetup ls|grep ceph|awk '{print $1}'|xargs -i dmsetup remove {}")
        # clean bcache
        self.clean_bcache()

        osd_per_dev = int(self.ceph_common["osd_per_dev"])
        # check disk conf
        if len(self.data_disk_list) < 1:
            self.error("data_disk number must >= 1")
            return False
        if osd_per_dev < 1:
            self.error("osd_per_dev must >=1")
            return False
        for disk in self.data_disk_list:
            if self.check_disk_is_existed(disk) is False:
                self.error("{} is not existed".format(disk))
                return False
            self.ssh_exec_cmd(f"mkfs.ext4 -F /dev/{disk}")

        for disk in self.nvme_disk_list:
            if self.check_disk_is_existed(disk) is False:
                self.error("{} is not existed".format(disk))
                return False
            self.ssh_exec_cmd(f"mkfs.ext4 -F /dev/{disk}")
        if osd_per_dev > 1:
            # mkpart data disk
            if self.mkpart_data_disk(self.data_disk_list, osd_per_dev) is False:
                self.error("mkpart data disk error")
                return False
        # bcache size
        if self.ceph_common.get("is_bacache", "N").upper() in ["YES", "Y"]:
            bcache_size = self.ceph_common.get("bcache_size", 200)
            # check bcache env modinfo bcache getconf PAGESIZE 4096
            if self.ssh_cmd_get_first_line("modinfo bcache &>/dev/null;echo $?") != "0":
                self.error("modinfo bcache failed")
                return False
            if self.ssh_cmd_get_first_line("getconf PAGESIZE") != "4096":
                self.error("getconf PAGESIZE != 4096")
                return False
            # install bcache-tools
            if "install bcache-tools success" in self.ssh_exec_cmd(
                    "cd {};sh adapter.sh bcache".format(self.remote_adapter_dir)):
                self.info("install bcache-tools success")
            else:
                self.error("install bcache-tools failed")
                return False
        else:
            bcache_size = None
        self.bcache_size = bcache_size
        # mkpart db_wal disk
        nvme_num = len(self.nvme_disk_list)
        if nvme_num > 0:
            per_wal_disk_osd_num = math.ceil(len(self.data_disk_list) / nvme_num) * osd_per_dev
            index = 0
            bcache_num = 0
            for nvme_disk in self.nvme_disk_list:
                if self.mkpart_db_wal_disk(nvme_disk, per_wal_disk_osd_num, bcache_size) is False:
                    self.error("mkpart db wal disk error {}".format(nvme_disk))
                    return False
                # make bcache disk
                if bcache_size:
                    step = math.ceil(len(self.data_disk_list) / nvme_num)

                    disk_range = self.data_disk_list[index: index + step]
                    index += step
                    self.make_bcache_disk(nvme_disk, disk_range, per_wal_disk_osd_num)
                    bcache_num += len(disk_range)
                    # check bcache
                    for _ in range(3):
                        time.sleep(30)
                        if self.ssh_cmd_get_first_line("cat /sys/block/bcache*/bcache/cache/cache_available_percent|wc -l"
                                                       ) == str(bcache_num):
                            self.info("make bcache success")
                            break
                        self.make_bcache_disk(nvme_disk, disk_range, per_wal_disk_osd_num)
                    else:
                        self.error("make bcache failed")
                        return False
            if bcache_size:
                # check bcache
                for _ in range(3):
                    if self.ssh_cmd_get_first_line("cat /sys/block/bcache*/bcache/cache/cache_available_percent|wc -l"
                                                   ) == str(len(self.data_disk_list)):
                        self.info("make bcache success")
                        return True
                    time.sleep(6)
                else:
                    self.error("make bcache failed")
                    return False

        return True

    def clean_bcache(self, ssh=None):
        clean_bcache_cmd = """
lsblk|grep bcache &>/dev/null
if [ $? -eq 0 ];then
for i in $(ls /sys/block/|grep bcache)
do
 echo 1 > /sys/block/${i}/bcache/stop
done
for i in $(ls -l /sys/fs/bcache |grep drwx|awk '{print $NF}')
do
 echo "echo 1 > /sys/fs/bcache/${i}/stop"
 echo 1 > /sys/fs/bcache/${i}/stop
done
sleep 1
fi
"""
        self.ssh_exec_cmd(clean_bcache_cmd, ssh=ssh)

    def make_bcache_disk(self, nvme_disk, disk_range, avg_nvme_osd_num):

        make_bcache_cmd = """
nvme_disk=%s
disk_list=(%s)
index=%s
for disk in ${disk_list[*]}
do
wipefs -a /dev/${disk}
sleep 2s
make-bcache -B /dev/${disk} -C /dev/${nvme_disk}p${index}
((index=${index}-1))
done
""" % (nvme_disk, " ".join(disk_range), avg_nvme_osd_num * 3)
        self.ssh_exec_cmd(make_bcache_cmd)

    def install_mon(self):
        append_conf_info = """

public_network = %s/24
cluster_network = %s/24

""" % (self.ceph_common["public_net"], self.ceph_common["cluster_net"])
        # check is single
        if len(self.install_info["mon_list"]) == 1:
            append_conf_info += """
osd pool default size = 1
osd pool default min size = 1

"""
        append_conf_info += """
[mon]
mon_allow_pool_delete = true

"""
        rgw_node_num = len(self.install_info["rgw_list"])
        if rgw_node_num:
            bucket_num = 1
            for i in range(1, rgw_node_num + 1, 1):
                for port_num in range(1, self.ceph_common["rgw_per_node"] + 1, 1):
                    port = "1" + "{:0>4d}".format(port_num)
                    append_conf_info += """
[client.rgw.bucket{}]
rgw_frontends = civetweb port={}
log file = /var/log/ceph/client.rgw.bucket{}.log
""".format(bucket_num, port, bucket_num)
                    bucket_num += 1
        # install mon
        self.ssh_exec_cmd("cd /etc/ceph;ceph-deploy new {}".format(
            " ".join(self.install_info["mon_list"])))
        self.ssh_exec_cmd("echo '{}' >> /etc/ceph/ceph.conf".format(append_conf_info))

        self.ssh_exec_cmd("cd /etc/ceph;ceph-deploy mon create-initial")
        time.sleep(3)

        for _ in range(3):
            mon_num = self.ssh_cmd_get_first_line("ceph -s|grep mon:|awk '{print $2}'")
            if mon_num == str(len(self.install_info["mon_list"])):
                self.info("install mon success")
                break
            time.sleep(3)
        else:
            self.error("install mon failed")
            return False
        self.ssh_exec_cmd("cd /etc/ceph;ceph-deploy --overwrite-conf admin {}".format(
            " ".join([host_info[0] for host_info in self.hosts_info_list])))
        self.ssh_exec_cmd("ceph -s")
        self.info("install mon success")
        return True

    def install_mgr(self):
        self.ssh_exec_cmd("cd /etc/ceph;ceph-deploy mgr create {}".format(
            " ".join(self.install_info["mgr_list"])))
        time.sleep(3)
        for _ in range(3):
            get_installed_mgr = self.ssh_cmd_get_first_line("ceph -s|grep mgr:")
            installed_list = []
            for mgr_hostname in self.install_info["mgr_list"]:
                ret_list = re.findall(mgr_hostname, get_installed_mgr)
                installed_list.extend(ret_list)
            if set(installed_list) == set(self.install_info["mgr_list"]):
                self.info("install mgr success")
                return True
            time.sleep(6)
        else:
            self.error("install mgr failed")
            return False

    def install_osd(self):
        osd_per_dev = int(self.ceph_common["osd_per_dev"])
        servers = self.cluster_conf["servers"]
        total_osd_num = 0
        for hostname in self.install_info["osd_list"]:
            node_info = servers[hostname]
            # get disk info
            data_disk = node_info.get("data_disk") or self.ceph_common.get("data_disk")

            if self.bcache_size or not data_disk:
                username = node_info.get("username") or self.ceph_common.get("username", "root")
                password = node_info.get("password") or self.ceph_common["password"]
                port = node_info.get("port") or self.ceph_common.get("port", 22)

                node_ssh = self.open_ssh(node_info["manager_ip"],
                                         username, password, port)
                if not self.bcache_size:
                    data_disk = self.ssh_exec_cmd(
                        "lsblk|grep disk |grep -v nvme|grep -v $(lsblk|grep "
                        "/boot/efi|awk '{print $1}'|grep -Eo '[a-zA-Z]+')|"
                        "awk '{print $1}'", ssh=node_ssh).strip().split("\n")
                else:
                    data_disk = self.ssh_exec_cmd(
                        "lsblk|grep -C 1 sd|grep -Eo bcache[0-9]+|sort -u", ssh=node_ssh).strip().split("\n")
                node_ssh.close()

            data_disk_list = self.data_to_list(data_disk)
            osd_num = node_info.get("osd_num") or self.ceph_common.get("osd_per_node_num")

            if osd_num:
                data_disk_list = data_disk_list[:int(osd_num)]
            data_disk_list = data_disk_list
            # nvme disk
            nvme_disk = node_info.get("nvme_disk") or self.ceph_common.get("nvme_disk") or []
            nvme_disk_list = self.data_to_list(nvme_disk)
            nvme_num = len(nvme_disk_list)
            if nvme_num > 0:
                step = math.ceil(len(data_disk_list) / nvme_num)
                index = 0
                for nvme in nvme_disk_list:
                    disk_range = data_disk_list[index: index + step]
                    index += step
                    self.create_osd(hostname, nvme, osd_per_dev, disk_range)
            else:
                self.create_osd(hostname, "none", osd_per_dev, data_disk_list)
            total_osd_num += int(len(data_disk_list) * osd_per_dev)

        time.sleep(3)
        for _ in range(3):

            check_osd_num = self.ssh_cmd_get_first_line(
                "ceph -s|grep osd:|awk '{print $4}'")
            if str(total_osd_num) == check_osd_num:
                self.info("install osd success")
                break
            time.sleep(6)
        else:
            self.info("install osd failed")
            return False
        return True

    def create_osd(self, hostname, nvme, osd_per_dev, disk_list):
        db_wal_prefix = "{}p".format(nvme) if "nvme" in nvme else nvme
        create_osd_cmd = r"""
node=%s
nvme_disk=%s
osd_per_dev=%s
data_disk_list=(%s)
j=1
k=2
cd /etc/ceph
for disk in ${data_disk_list[@]}
do
for disk_index in $(seq 1 ${osd_per_dev})
do
if [ ${osd_per_dev} -eq 1 ];then
    target_disk=${disk}
else
    target_disk=${disk}${disk_index}
fi
if [[ "${nvme_disk}" == "none" ]];then
    ceph-deploy osd create ${node} --data /dev/${target_disk}
else
    ceph-deploy osd create ${node} --data /dev/${target_disk} \
--block-wal /dev/${nvme_disk}${k} --block-db /dev/${nvme_disk}${j} 
fi
((j=${j}+2))
((k=${k}+2))
done
done
cd -
""" % (hostname, db_wal_prefix, osd_per_dev, " ".join(disk_list))
        self.ssh_exec_cmd(create_osd_cmd)

    def install_rgw(self):
        rgw_per_node = int(self.ceph_common["rgw_per_node"])
        count = 0
        for hostname in self.install_info["rgw_list"]:
            rgw_range = "{%s..%s}" % (
                (count * rgw_per_node) + 1, (count + 1) * rgw_per_node)
            self.ssh_exec_cmd("""
cd /etc/ceph
ceph-deploy gatherkeys %s
for i in %s
do
ceph-deploy rgw create %s:bucket${i}
done
""" % (hostname, rgw_range, hostname))
            count += 1
        time.sleep(3)
        for _ in range(3):
            check_rgw_num = self.ssh_cmd_get_first_line(
                "ceph -s|grep rgw:|awk '{print $2}'")
            if check_rgw_num == str(count * rgw_per_node):
                self.info("rgw_install success")
                return True
            time.sleep(3)
        else:
            self.error("rgw install failed")
            return False

    def install_mds(self):
        mds_list = self.install_info["mds_list"]
        for hostname in mds_list:
            self.ssh_exec_cmd("cd /etc/ceph;ceph-deploy mds create {}".format(hostname))
            time.sleep(3)
        for _ in range(3):
            check_mds_num = self.ssh_cmd_get_first_line("ceph -s|grep mds:|awk '{print $2}'")
            if check_mds_num == str(len(mds_list)):
                self.info("install mds success")
                return True
            time.sleep(3)
        else:
            self.error("install mds failed")
            return False

    def deploy_main(self):
        # install ceph-deploy
        if self.pip_install_package("ceph-deploy") is False:
            return False
        if self.system_name in ["openeuler", "anolis"]:
            # modfy  __init__.py
            sed_cmd = """
ceph_deploy_dir=$(dirname $(%s -c "import ceph_deploy;print(ceph_deploy.__file__)"))
sed -i "s#linux_distribution()#('fedora', '1.0', 'test')#g" "${ceph_deploy_dir}/hosts/remotes.py"
cat ${ceph_deploy_dir}/hosts/remotes.py|grep "('fedora', '1.0', 'test')" &>/dev/null
echo $?
""" % self.python
            if self.ssh_cmd_get_first_line(sed_cmd) != "0":
                self.error("host/remotes.py sed failed")
                return False
        if len(self.install_info["mon_list"]) > 0:
            if self.install_mon() is False:
                return False
        if len(self.install_info["mgr_list"]) > 0:
            if self.install_mgr() is False:
                return False
        if len(self.install_info["osd_list"]) > 0:
            if self.install_osd() is False:
                return False
        if len(self.install_info["rgw_list"]) > 0:
            if self.install_rgw() is False:
                return False
        if len(self.install_info["mds_list"]) > 0:
            if self.install_mds() is False:
                return False
        return True

    def uninstall_main(self):
        ceph_host_list = list(self.cluster_conf["servers"].keys())
        # ceph-deploy  purge
        self.ssh_exec_cmd("cd /etc/ceph;ceph-deploy purge {}".format(" ".join(ceph_host_list)))
        # ceph-deploy purge data
        self.ssh_exec_cmd("ceph-deploy purge {}".format(" ".join(ceph_host_list)))
        self.ssh_exec_cmd("ceph-deploy forgetkeys")

        for node_name, node_info in self.cluster_conf["servers"].items():
            username = node_info.get("username") or self.ceph_common.get("username", "root")
            password = node_info.get("password") or self.ceph_common["password"]
            port = node_info.get("port") or self.ceph_common.get("port", 22)

            node_ssh = self.open_ssh(node_info["manager_ip"],
                                     username, password, port)
            # kill ceph
            self.ssh_exec_cmd("ps -ef|grep -v grep|grep ceph|grep -v deploy|"
                              "awk '{print $2}'|xargs -i kill -9 {}", node_ssh)
            # umount ceph osd
            self.ssh_exec_cmd("df -h|grep '/var/lib/ceph/osd'|"
                              "awk '{print $NF}'|xargs -i umount '{}'", node_ssh)

            # uninstall ceph
            self.ssh_exec_cmd("yum remove -y ceph", node_ssh)
            # clean ceph data
            self.ssh_exec_cmd("rm -rf /etc/ceph", node_ssh)
            self.ssh_exec_cmd("rm -rf /var/lib/ceph", node_ssh)
            self.ssh_exec_cmd("rm -rf /var/run/ceph", node_ssh)
            self.ssh_exec_cmd("rm -rf /var/log/ceph", node_ssh)
            self.ssh_exec_cmd("vgs|grep ceph|awk '{print $1}'|xargs -i vgremove -y '{}'", node_ssh)
            self.ssh_exec_cmd("dmsetup ls|grep ceph|awk '{print $1}'|xargs -i dmsetup remove '{}'", node_ssh)
            if self.ssh_cmd_get_first_line("ceph -v &>/dev/null;echo $?", node_ssh) != "127":
                node_ssh.close()
                self.error(f"{node_name} ceph uninstall failed")
                return False
            # clean bcache
            self.clean_bcache(ssh=node_ssh)
            node_ssh.close()
        self.info("ceph uninstall finished")
        return True

    def run(self):
        # self.check_install_python()
        # # self.compatible_adapter()
        # self.init_disk()
        # return
        # self.finished = True
        # return True
        # clean env
        self.clean_env()
        if self.step == 0:
            # set netword
            self.exec_func_increase_step(self.set_network)
        if self.step == 1:
            # close_firewall
            self.exec_func_increase_step(self.close_firewall)
        if self.step == 2:
            # close selinux
            self.exec_func_increase_step(self.close_selinux)
        if self.step == 3:
            # change umask
            self.exec_func_increase_step(self.change_umask)
        if self.step == 4:
            # set hostname
            self.exec_func_increase_step(self.set_hostname)
        if self.step == 5:
            # add /etc/hosts
            self.exec_func_increase_step(self.add_host_file)
        if self.step == 6:
            # replace os repo
            self.exec_func_increase_step(self.replace_os_repo_file)
        if self.step == 7:
            # config ceph.repo
            self.exec_func_increase_step(self.config_ceph_repo)
        if self.step == 8:
            # compatible adapter
            self.exec_func_increase_step(self.compatible_adapter)
        if self.step == 9:
            # config chrony
            self.exec_func_increase_step(self.config_chrony)
        if self.step == 10:
            # config no password
            self.exec_func_increase_step(self.config_no_password)
        if self.step == 11:
            # check install python
            self.exec_func_increase_step(self.check_install_python)
        if self.step == 12:
            # check add  ceph user
            self.exec_func_increase_step(self.add_ceph_user)
        if self.step == 13:
            # install dependent
            self.exec_func_increase_step(self.ceph_dependent)
        if self.step == 14:
            # check clean disk
            self.exec_func_increase_step(self.init_disk)
        if self.step == 15:
            self.finished = True


class ClientPrepare(BasePrepare):
    def run(self):
        # clean env
        self.clean_env()
        if self.step == 0:
            # set netword
            self.exec_func_increase_step(self.set_network)
        if self.step == 1:
            # close_firewall
            self.exec_func_increase_step(self.close_firewall)
        if self.step == 2:
            # close selinux
            self.exec_func_increase_step(self.close_selinux)
        if self.step == 3:
            # change umask
            self.exec_func_increase_step(self.change_umask)
        if self.step == 4:
            # set hostname
            self.exec_func_increase_step(self.set_hostname)
        if self.step == 5:
            # add /etc/hosts
            self.exec_func_increase_step(self.add_host_file)
        if self.step == 6:
            # replace os repo
            self.exec_func_increase_step(self.replace_os_repo_file)
        if self.step == 7:
            # config ceph.repo
            self.exec_func_increase_step(self.config_ceph_repo)
        if self.step == 8:
            # compatible adapter
            self.exec_func_increase_step(self.compatible_adapter)
        if self.step == 9:
            # config chrony
            self.exec_func_increase_step(self.config_chrony)
        if self.step == 10:
            # config no password
            self.exec_func_increase_step(self.config_no_password)
        if self.step == 11:
            # check install python
            self.exec_func_increase_step(self.check_install_python)
        if self.step == 12:
            # check add  ceph user
            self.exec_func_increase_step(self.add_ceph_user)
        if self.step == 13:
            # install dependent
            self.exec_func_increase_step(self.ceph_dependent)
        if self.step == 14:
            self.finished = True


def deploy_main(cluster_conf=None):
    with open(current_path.joinpath("conf", "conf.yaml")) as f:
        conf_info = yaml.safe_load(f)
    if not cluster_conf:
        with open(current_path.joinpath("conf", "cluster_conf.yaml")) as f:
            cluster_conf = yaml.safe_load(f)
    servers_info = cluster_conf.get("servers", {})
    clients_info = cluster_conf.get("clients", {})
    prepare_obj_list = []
    thread_list = []
    for server_name, server_info in servers_info.items():
        server_info["hostname"] = server_name
        server_prepare = ServerPrepare(
            cluster_conf=cluster_conf, node_info=server_info, config_info=conf_info)

        prepare_obj_list.append(server_prepare)
        server_thread = Thread(target=server_prepare.run)
        thread_list.append(server_thread)
        server_thread.start()

    for client_name, client_info in clients_info.items():
        client_info["hostname"] = client_name
        client_prepare = ClientPrepare(
            cluster_conf=cluster_conf, node_info=client_info, config_info=conf_info)

        prepare_obj_list.append(client_prepare)
        client_thread = Thread(target=client_prepare.run)
        thread_list.append(client_thread)
        client_thread.start()
    # wait thread finished
    for t in thread_list:
        t.join()

    success_flag = True
    for prepare_obj in prepare_obj_list:
        if prepare_obj.is_success() is False:
            print(prepare_obj.node_info["hostname"], prepare_obj.is_success())
            success_flag = False
    if success_flag is True:
        if prepare_obj_list[0].deploy_main() is False:
            success_flag = False
        else:
            prepare_obj_list[0].info("ceph deploy success")

    for prepare_obj in prepare_obj_list:
        prepare_obj.close()

    if success_flag is False:
        raise Exception("ceph deploy failed")


def uninstall_main(cluster_conf=None):
    with open(current_path.joinpath("conf", "conf.yaml")) as f:
        conf_info = yaml.safe_load(f)
    if not cluster_conf:
        with open(current_path.joinpath("conf", "cluster_conf.yaml")) as f:
            cluster_conf = yaml.safe_load(f)
    first_ceph = list(cluster_conf["servers"].keys())[0]
    first_ceph_info = cluster_conf["servers"][first_ceph]
    first_ceph_info["hostname"] = first_ceph
    first_ceph_prepare = ServerPrepare(
        cluster_conf=cluster_conf, node_info=first_ceph_info, config_info=conf_info)
    if first_ceph_prepare.uninstall_main() is False:
        raise Exception("cepj uninstall failed")


if __name__ == '__main__':
    deploy_main()
    # uninstall_main()

