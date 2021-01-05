# -*- coding: utf-8 -*-

"""
 Copyright (c) 2020. Huawei Technologies Co.,Ltd.ALL rights reserved.
 This program is licensed under Mulan PSL v2.
 You can use it according to the terms and conditions of the Mulan PSL v2.
          http://license.coscl.org.cn/MulanPSL2
 THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
 EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
 MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
 See the Mulan PSL v2 for more details.
"""
####################################
# @Author    	:   lemon.higgins
# @Contact   	:   lemon.higgins@aliyun.com
# @Date      	:   2020-11-10 02:40:04
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   收集系统的基础信息
#####################################


import subprocess
import os
import logging
from ruamel import yaml
import json


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

ENV_INFO = {}


def basic_info():
    """
    获取linux的基本信息

    Returns:
        [dict]: [获取的环境信息总结]
    """
    ENV_INFO["os"] = subprocess.getoutput(
        "cat /etc/os-release | grep '^PRETTY_NAME' | awk -F '=' '{print $NF}' | tr -d '\"\"'"
    )
    ENV_INFO["hostname"] = subprocess.getoutput("hostname")
    ENV_INFO["platform"] = subprocess.getoutput(
        "hostnamectl  | grep 'Virtualization: kvm' >/dev/nul && echo kvm || echo physical"
    )
    ENV_INFO["frame"] = subprocess.getoutput("uname -m")
    ENV_INFO["kernel version"] = subprocess.getoutput("uname -r")
    ENV_INFO["cmdline"] = subprocess.getoutput("cat /proc/cmdline")

    return ENV_INFO


def mem_info():
    """
    获取环境内存信息

    Returns:
        [dict]: [获取的环境信息总结]
    """
    ENV_INFO["mem info"] = {}
    ENV_INFO["mem info"]["mem"] = {}
    ENV_INFO["mem info"]["swap"] = {}

    ENV_INFO["mem info"]["mem"]["total"] = (
        subprocess.getoutput("cat /proc/meminfo  | grep MemTotal | awk '{print $2}'")
        + "kB"
    )
    ENV_INFO["mem info"]["mem"]["free"] = (
        subprocess.getoutput("cat /proc/meminfo  | grep MemFree | awk '{print $2}'")
        + "kB"
    )
    ENV_INFO["mem info"]["mem"]["available"] = (
        subprocess.getoutput(
            "cat /proc/meminfo  | grep MemAvailable | awk '{print $2}'"
        )
        + "kB"
    )
    ENV_INFO["mem info"]["mem"]["buffers"] = (
        subprocess.getoutput("cat /proc/meminfo  | grep Buffers | awk '{print $2}'")
        + "kB"
    )
    ENV_INFO["mem info"]["mem"]["cache"] = (
        subprocess.getoutput("cat /proc/meminfo  | grep Cached | awk '{print $2}'")
        + "kB"
    )

    ENV_INFO["mem info"]["swap"]["total"] = (
        subprocess.getoutput("cat /proc/meminfo  | grep SwapTotal | awk '{print $2}'")
        + "kB"
    )
    ENV_INFO["mem info"]["swap"]["free"] = (
        subprocess.getoutput("cat /proc/meminfo  | grep SwapFree | awk '{print $2}'")
        + "kB"
    )
    ENV_INFO["mem info"]["swap"]["cache"] = (
        subprocess.getoutput("cat /proc/meminfo  | grep SwapCached | awk '{print $2}'")
        + "kB"
    )

    return ENV_INFO


def cpu_info():
    """
    获取环境的CPU信息

    Returns:
        [dict]: [获取的环境信息总结]
    """
    ENV_INFO["cpu info"] = {}

    ENV_INFO["cpu info"]["processor"] = subprocess.getoutput(
        "cat /proc/cpuinfo  | grep processor | wc -l"
    )
    core_num = 0
    cores = subprocess.getoutput(
        "cat /proc/cpuinfo  | grep 'cpu cores' | awk '{print $NF}'"
    ).split("\n")
    for core in cores:
        core_num += int(core)
    ENV_INFO["cpu info"]["core"] = core_num
    ENV_INFO["cpu info"]["model name"] = subprocess.getoutput(
        "cat /proc/cpuinfo  | grep 'model name' | awk -F ':' '{print $NF}' | sed 's/^ //g' | uniq"
    )

    ENV_INFO["cpu info"]["cpu MHz"] = subprocess.getoutput(
        "cat /proc/cpuinfo | grep 'cpu MHz' | awk '{print $NF}' | uniq"
    )
    ENV_INFO["cpu info"]["cache size"] = subprocess.getoutput(
        "cat /proc/cpuinfo | grep 'cache size' | awk '{print $NF}' | uniq"
    )

    return ENV_INFO


class NetInfo(object):
    """
    获取环境网络基本信息
    """

    def dns():
        """
        获取系统dns信息

        Returns:
            [dict]: [获取的环境信息总结]
        """
        ENV_INFO["net info"] = {}
        resolv = []
        for dns in subprocess.getoutput(
            "cat /etc/resolv.conf  | grep nameserver | awk '{print $NF}'"
        ).split("\n"):
            nameserver = {}
            nameserver["nameserver"] = dns
            resolv.append(nameserver)
        ENV_INFO["net info"]["resolv"] = resolv

        return ENV_INFO

    def eth_info():
        """
        获取网卡信息

        Returns:
            [dict]: [获取的环境信息总结]
        """
        ENV_INFO["net info"] = {}
        ENV_INFO["net info"]["eth info"] = []
        for id in subprocess.getoutput(
            "lspci | grep 'Ethernet' | awk '{print $1}'"
        ).split("\n"):
            if id != "":
                ENV_INFO["net info"]["eth info"].append(
                    subprocess.getoutput(
                        "lspci -s "
                        + id
                        + " -v | grep Subsystem: | awk -F 'Subsystem: ' '{print $NF}'"
                    )
                )

        return ENV_INFO

    def mac(nic):
        """
        获取网卡mac地址

        Args:
            nic ([string]): [网卡名]

        Returns:
            [dict]: [获取的环境信息总结]
        """
        return subprocess.getoutput("cat /sys/class/net/" + nic + "/address")

    def status(nic):
        """获取网卡的status信息

        Args:
            nic ([string]): [网卡名]

        Returns:
            [dict]: [获取的环境信息总结]
        """
        return subprocess.getoutput(
            "ip addr show " + nic + " | grep '<.*>' | awk '{print $3}'| tr -d '<>'"
        )

    def mtu(nic):
        """获取网卡的mtu值

        Args:
            nic ([string]): [网卡名]

        Returns:
            [string]: [mtu值]
        """
        return subprocess.getoutput(
            "ip addr show "
            + nic
            + " | grep 'mtu' | sed -n 's/ /\\n/gp' | sed -n \"$(echo \"$(ip addr show "
            + nic
            + " | grep 'mtu' | sed -n 's/ /\\n/gp' | sed -n '/mtu/=') + 1\" | bc)p\" "
        )

    def driver(nic):
        """获取网卡驱动信息

        Args:
            nic ([string]): [网卡名]

        Returns:
            [string]: [mtu值]
        """
        return subprocess.getoutput(
            "ethtool -i " + nic + " | grep driver | awk '{print $NF}'"
        )

    def brigde(nic):
        """确定当前网卡是否是网桥

        Returns:
            [string]: [YES or NO]
        """
        return subprocess.getoutput(
            "brctl show | grep " + nic + " >/dev/nul && echo 'YES' || echo 'NO'"
        )

    def v4_ip(nic):
        """获取ip,route,genmask信息

        Returns:
            [list]: [ip, route, genmask]
        """
        v4_ip = []

        for ip in subprocess.getoutput(
            "ip addr show " + nic + " | grep 'inet ' | awk '{print $2}' "
        ).split("\n"):
            ipv4 = {}
            ipv4["ipv4"] = ip
            if ip == "":
                ipv4["route"] = ""
                ipv4["genmask"] = ""
                return ENV_INFO["net info"]["nic"]["v4 ip"].append(ipv4)

            ipv4["route"] = subprocess.getoutput(
                'ip route | grep "$(echo '
                + ip
                + " | awk -F '/' '{print $1}')\" | awk '{print $1}'"
            )
            ipv4["genmask"] = subprocess.getoutput(
                "ip addr show " + nic + ' | grep "' + ip + " brd\" | awk '{print $4}'"
            )
            v4_ip.append(ipv4)
        return v4_ip

    def v6_ip(nic):
        """获取ipv6的基础信息

        Returns:
            [list]: [ip, route]
        """
        v6_ip = []
        tmp = []
        v6_routes = subprocess.getoutput(
            "ip -6 route | grep nexthop | grep " + nic + "  | awk '{print $3}'"
        ).split("\n")
        if "fe80::" in subprocess.getoutput(
            "ip -6 route | grep 'fe80::' | grep " + nic
        ):
            v6_routes.append("fe80::")

        for route in v6_routes:
            ipv6 = {}
            v6_route = []
            if route == "" or route in tmp:
                continue

            route_h = route.split("::")[0] + ":"

            for r in v6_routes:
                if route_h in r:
                    v6_route.append(r)
                    tmp.append(r)

            ipv6["ipv6"] = subprocess.getoutput(
                "ip addr show "
                + nic
                + ' | grep "inet6 '
                + route_h
                + "\" | awk '{print $2}'"
            )
            ipv6["route"] = v6_route
            v6_ip.append(ipv6)

        return v6_ip

    def auto_negotiation(nic):
        """查看网卡的自动协商机制

        Returns:
            [string]: [off or on]
        """
        return subprocess.getoutput(
            "ethtool " + nic + " | grep 'Auto-negotiation' | awk '{print $NF}'"
        )

    def link_detected(nic):
        """链路状态

        Returns:
            [string]: [yes or no]
        """
        return subprocess.getoutput(
            "ethtool " + nic + " | grep 'Link detected' | awk '{print $NF}'"
        )

    def nic_info(nic):
        """获取网卡相关所有信息

        Args:
            nic (string): 网卡名称

        Returns:
            [dict]: 网卡信息
        """        
        nic_info = {}
        nic_info["name"] = nic
        nic_info["mac"] = NetInfo.mac(nic)
        nic_info["status"] = NetInfo.status(nic)
        nic_info["mtu"] = NetInfo.mtu(nic)
        nic_info["driver"] = NetInfo.driver(nic)
        nic_info["brigde"] = NetInfo.brigde(nic)
        nic_info["v4 ip"] = NetInfo.v4_ip(nic)
        nic_info["v6 ip"] = NetInfo.v6_ip(nic)
        nic_info["Auto-negotiation"] = NetInfo.auto_negotiation(nic)
        nic_info["Link detected"] = NetInfo.link_detected(nic)

        try:
            ENV_INFO["net info"]
        except:
            ENV_INFO["net info"] = {}
            ENV_INFO["net info"]["nic"] = nic_info
        else:
            ENV_INFO["net info"]["nic"].append(nic_info)

        return ENV_INFO

    def all_nic_info():
        """获取网卡所有的基础信息

        Returns:
            [list]: [所有的网卡信息]
        """
        ENV_INFO["net info"] = {}
        ENV_INFO["net info"]["nic"] = []
        for nic in subprocess.getoutput("ls /sys/class/net/").split("\n"):
            NetInfo.nic_info(nic)

        return ENV_INFO


def disk_info():
    """
    获取磁盘，目录挂载信息
    """
    disk_json = subprocess.getoutput("lsblk -J")
    disk = json.loads(disk_json).get("blockdevices")
    ENV_INFO["disk info"] = disk

    return ENV_INFO


def service_info():
    """
    获取环境中所有服务的状态信息
    """
    ENV_INFO["service info"] = []

    for service in subprocess.getoutput(
        "systemctl --all --no-pager | grep -w 'active\|inactive' | sed 's/● / /g' | awk '{print $1}'"
    ).split("\n"):
        service_info = {}
        service_info["UNIT"] = service
        service = service.replace("\\", "\\\\")

        service_info["LOAD"] = subprocess.getoutput(
            "systemctl --all --no-pager | grep -w '" + service + "' | awk '{print $2}'"
        )
        service_info["ACTIVE"] = subprocess.getoutput(
            "systemctl --all --no-pager | grep -w '" + service + "' | awk '{print $3}'"
        )
        service_info["SUB"] = subprocess.getoutput(
            "systemctl --all --no-pager | grep -w '" + service + "' | awk '{print $4}'"
        )

        ENV_INFO["service info"].append(service_info)

    pass  # TODO


def socket_info():
    """
    获取环境socket信息
    """
    ENV_INFO["socket info"] = {}
    ENV_INFO["socket info"]["used num"] = subprocess.getoutput(
        "cat /proc/net/sockstat | grep sockets | awk '{print $NF}'"
    )

    return ENV_INFO


def process_info():
    """
    获取进程信息
    """
    ENV_INFO["process info"] = []

    for pid in subprocess.getoutput(
        "ps -eo pid,ppid,user,rss,pmem,pcpu,vsize,args | grep -vw 'PID    PPID USER' | awk '{print $1}'"
    ):
        process = {}
        process["pid"] = pid
        process["ppid"] = subprocess.getoutput(
            "ps -eo pid,ppid,user,rss,pmem,pcpu,vsize,args | grep -w "
            + pid
            + "| awk '{print $2}'"
        )
        process["user"] = subprocess.getoutput(
            "ps -eo pid,ppid,user,rss,pmem,pcpu,vsize,args | grep -w "
            + pid
            + "| awk '{print $2}'"
        )
        process["rss"] = subprocess.getoutput(
            "ps -eo pid,ppid,user,rss,pmem,pcpu,vsize,args | grep -w "
            + pid
            + "| awk '{print $2}'"
        )
        process["pmem"] = subprocess.getoutput(
            "ps -eo pid,ppid,user,rss,pmem,pcpu,vsize,args | grep -w "
            + pid
            + "| awk '{print $2}'"
        )
        process["pcpu"] = subprocess.getoutput(
            "ps -eo pid,ppid,user,rss,pmem,pcpu,vsize,args | grep -w "
            + pid
            + "| awk '{print $2}'"
        )
        process["vsize"] = subprocess.getoutput(
            "ps -eo pid,ppid,user,rss,pmem,pcpu,vsize,args | grep -w "
            + pid
            + "| awk '{print $2}'"
        )
        process["args"] = subprocess.getoutput(
            "ps -eo pid,ppid,user,rss,pmem,pcpu,vsize,args | grep -w "
            + pid
            + "| awk '{print $2}'"
        )
        ENV_INFO["process info"].append(process)


def collect_log():
    """收集message日志
    """    
    exitcode, output = subprocess.getstatusoutput(
        "log_dir=$(mktemp -d) && cp /var/log/message* ${log_dir} -fr && dmesg > ${log_dir}/kmesg && tar -zcvf "
        + os.getcwd()
        + "/log.tar.gz ${log_dir} && rm -rf ${log_dir}"
    )
    if exitcode != 0:
        logging.error("failed to collect logs.")
        exit(1)


def write_yaml(info):
    """
    将数据写入导yaml文件中

    Args:
        info ([dict]): [环境信息数据]
    """
    with open(
        os.path.split(os.path.realpath(__file__))[0] + "/envInfo.yaml", "w+"
    ) as f:
        yaml.dump(info, f, Dumper=yaml.RoundTripDumper, allow_unicode=True)


def install_rpm(rpm):
    """安装环境信息收集需要的rpm软件包

    Args:
        rpm (string): 软件包名
    """    
    exitcode, output = subprocess.getstatusoutput(
        "rpm -qa " + rpm + "&& yum -y install " + rpm
    )

    if exitcode != 0:
        logging.error("failed to install rpms:" + rpm)
        exit(1)


if __name__ == "__main__":
    install_rpm("coreutils grep gawk hostname systemd util-linux systemd procps-ng")

    basic_info()
    mem_info()
    cpu_info()
    NetInfo.all_nic_info()
    disk_info()
    service_info()
    process_info()
    collect_log()

    write_yaml(ENV_INFO)