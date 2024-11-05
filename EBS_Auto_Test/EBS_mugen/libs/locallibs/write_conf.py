# -*- coding: utf-8 -*-
"""
 Copyright (c) [2021] Huawei Technologies Co.,Ltd.ALL rights reserved.
 This program is licensed under Mulan PSL v2.
 You can use it according to the terms and conditions of the Mulan PSL v2.
          http://license.coscl.org.cn/MulanPSL2
 THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
 EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
 MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
 See the Mulan PSL v2 for more details.

 @Author  : lemon-higgins
 @email   : lemon.higgins@aliyun.com
 @Date    : 2021-04-20 15:13:09
 @License : Mulan PSL v2
 @Version : 1.0
 @Desc    : 生成测试环境配置
"""

import sys
import os
import json
import socket
import subprocess
import argparse
import paramiko

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_PATH)
import mugen_log

NODE_DATA = {"ID": 1}


def write_conf(ip, password, port=22, user="root", run_remote=False, copy_all=True):
    """写入测试环境的配置

    Args:
        ip ([str]): 测试环境地址
        password ([str]): 测试环境的用户密码
        port (int, optional): 测试环境ssh端口号. Defaults to 22.
        user (str, optional): 测试环境用户名. Defaults to "root".
    """
    if None in (ip, password):
        mugen_log.logging("error", "必要参数ip or password存在缺失.")
        sys.exit(1)

    if not os.path.exists("/etc/mugen"):
        OET_PATH = os.environ.get("OET_PATH")
        if OET_PATH is None:
            mugen_log.logging("error", "环境变量：OET_PATH不存在，请检查mugen框架.")
            sys.exit(1)

        conf_path = OET_PATH.rstrip("/") + "/" + "conf/env.json"
        os.makedirs(OET_PATH.rstrip("/") + "/" + "conf", exist_ok=True)
    else:
        conf_path = "/etc/mugen/env.json"

    if os.path.exists(conf_path):
        exitcode = subprocess.getstatusoutput("grep " + ip + " " + conf_path)[0]
        if exitcode == 0:
            mugen_log.logging("warn", "当前机器:" + ip + "的相关信息已经录入到配置文件中.")
            sys.exit(0)

        try:
            f = open(conf_path, "r")
            ENV_DATA = json.loads(f.read())
            f.close()

            node_id_list = list()
            for node in ENV_DATA["NODE"]:
                node_id_list.append(node["ID"])
            node_id_list.sort()
            NODE_DATA.update({"ID": node_id_list[-1] + 1})
        except json.decoder.JSONDecodeError as e:
            mugen_log.logging("warn", e)
            ENV_DATA = {"NODE": []}
    else:
        ENV_DATA = {"NODE": []}

    if subprocess.getstatusoutput("ip a | grep " + ip)[0] == 0:
        NODE_DATA["LOCALTION"] = "local"
    elif run_remote:
        NODE_DATA["LOCALTION"] = "local"
    else:
        NODE_DATA["LOCALTION"] = "remote"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    try:
        ssh.connect(ip, port, user, password)
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        mugen_log.logging("error", e)
        sys.exit(1)

    if os.path.exists(conf_path):
        stdin, stdout, stderr = ssh.exec_command(
            "ip a | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | awk -F '/' '{print $1}'"
        )
        for remote_ip in stdout.read().decode("utf-8").strip("\n").split("\n"):
            exitcode, output = subprocess.getstatusoutput(
                "grep " + remote_ip + " " + conf_path
            )
            if exitcode == 0:
                mugen_log.logging("warn", ip + "和已录入到配置文件中的" + remote_ip + "是同一台机器.")
                sys.exit(0)

    stdin, stdout, stderr = ssh.exec_command("hostnamectl | grep 'Virtualization: kvm'")
    if stdout.read().decode("utf-8").strip("\n") == "":
        NODE_DATA.update({"MACHINE": "physical"})
    elif run_remote:
        NODE_DATA.update({"MACHINE": "physical"})
    else:
        NODE_DATA["MACHINE"] = "kvm"

    stdin, stdout, stderr = ssh.exec_command(
        "ip a | grep 'inet6' | grep -v 'scope host' | awk '{print $2}' | awk -F '/' '{print $1}' | head -n 1"
    )
    NODE_DATA["IPV6"] = stdout.read().decode("utf-8").strip("\n")

    stdin, stdout, stderr = ssh.exec_command("uname -m")
    NODE_DATA["FRAME"] = stdout.read().decode("utf-8").strip("\n")

    stdin, stdout, stderr = ssh.exec_command(
        " ip route | grep " + ip + " | awk '{print $3}' | sort -u"
    )
    NODE_DATA["NIC"] = stdout.read().decode("utf-8").strip("\n")

    stdin, stdout, stderr = ssh.exec_command(
        "cat /sys/class/net/" + NODE_DATA["NIC"] + "/address"
    )
    NODE_DATA["MAC"] = stdout.read().decode("utf-8").strip("\n")

    NODE_DATA["IPV4"] = ip
    NODE_DATA["USER"] = user
    NODE_DATA["PASSWORD"] = password
    NODE_DATA["SSH_PORT"] = port

    ssh.close()

    if NODE_DATA["MACHINE"] == "kvm":
        NODE_DATA["HOST_IP"] = ""
        NODE_DATA["HOST_USER"] = ""
        NODE_DATA["HOST_PASSWORD"] = ""
        NODE_DATA["HOST_SSH_PORT"] = ""

    if NODE_DATA["MACHINE"] == "physical":
        NODE_DATA["BMC_IP"] = ""
        NODE_DATA["BMC_USER"] = ""
        NODE_DATA["BMC_PASSWORD"] = ""

    if run_remote :
        NODE_DATA.update({"ID": 1})
        if copy_all:
            NODE_DATA["COPY_ALL"]="true"
        for change_node in ENV_DATA["NODE"]:
            change_node.update({"ID": change_node["ID"] + 1})
        ENV_DATA["NODE"].insert(0, NODE_DATA)
    else:
        ENV_DATA["NODE"].append(NODE_DATA)

    with open(conf_path, "w") as f:
        f.write(json.dumps(ENV_DATA, indent=4))
        mugen_log.logging("info", "配置文件加载完成...")

    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="manual to this script")
    parser.add_argument("--ip", type=str, default=None)
    parser.add_argument("--password", type=str, default=None)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--user", type=str, default="root")
    parser.add_argument("--run_remote", action='store_true')
    parser.add_argument("--put_all", action='store_true')

    args = parser.parse_args()

    if not args.run_remote:
        args.put_all = False

    write_conf(args.ip, args.password, args.port, args.user, args.run_remote, args.put_all)
