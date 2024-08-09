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
 @Date    : 2021-04-22 17:20:06
 @License : Mulan PSL v2
 @Version : 1.0
 @Desc    : 远端重启
"""


import os
import sys
import subprocess
import time
import argparse

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_PATH)
import mugen_log
import ssh_cmd


def reboot_wait(node=2, wait_time=None):
    """等待重启成功

    Args:
        node (int, optional): 节点号. Defaults to 2.
        wait_time ([int], optional): 等待重启的时长，默认虚拟机:300s，物理机:600s. Defaults to None.

    Returns:
        [int]: 成功-0，失败-非0
    """
    count = 0

    if node == 1:
        mugen_log.logging(
            "error", "The local machine is unavailable for reboot operation"
        )
        sys.exit(1)

    machine_type = os.environ.get("NODE" + str(node) + "_MACHINE")

    if wait_time is not None:
        time_sleep = wait_time
    elif machine_type.lower() == "kvm":
        time_sleep = 300
    else:
        time_sleep = 600

    while [count < time_sleep]:
        exitcode = subprocess.getstatusoutput(
            "ping -c 3 -w 3 " + os.environ.get("NODE" + str(node) + "_IPV4")
        )[0]
        if exitcode == 0:
            conn = ssh_cmd.pssh_conn(
                os.environ.get("NODE" + str(node) + "_IPV4"),
                os.environ.get("NODE" + str(node) + "_PASSWORD"),
                os.environ.get("NODE" + str(node) + "_SSH_PORT"),
                os.environ.get("NODE" + str(node) + "_USER"),
                log_level="warn",
            )
            if conn:
                if ssh_cmd.pssh_cmd(conn, "ls")[1]:
                    ssh_cmd.pssh_close(conn)
                    return 0
        time.sleep(1)
        count += 1

    mugen_log.logging(
        "error",
        "The remote machine:%s failed to restart."
        % os.environ.get("NODE" + str(node) + "_IPV4"),
    )
    return 519


def remote_reboot(node=2, wait_time=None):
    """重启

    Args:
        node (int, optional): 节点号. Defaults to 2.
        wait_time ([int], optional): 等待重启的时长，默认虚拟机:300s，物理机:600s. Defaults to None.
    """
    if node == 1:
        mugen_log.logging(
            "error", "The local machine is unavailable for reboot operation"
        )
        sys.exit(1)

    conn = ssh_cmd.pssh_conn(
        os.environ.get("NODE" + str(node) + "_IPV4"),
        os.environ.get("NODE" + str(node) + "_PASSWORD"),
        os.environ.get("NODE" + str(node) + "_SSH_PORT"),
        os.environ.get("NODE" + str(node) + "_USER"),
    )
    exitcode, error_output = ssh_cmd.pssh_cmd(conn, "reboot")
    ssh_cmd.pssh_close(conn)
    if exitcode != -1 and exitcode != 0:
        mugen_log.logging("error", error_output)
        sys.exit(exitcode)

    sys.exit(reboot_wait(node, wait_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="remote_reboot.py reboot|wait [-h] [--node NODE]",
        description="manual to this script",
    )
    parser.add_argument("operation", type=str, choices=["reboot", "wait"], default=None)
    parser.add_argument("--node", type=int, default=2)
    parser.add_argument("--waittime", type=int, default=None)
    args = parser.parse_args()

    if args.operation == "wait":
        sys.exit(reboot_wait(args.node, args.waittime))
    elif args.operation == "reboot":
        remote_reboot(args.node, args.waittime)
    else:
        mugen_log.logging(
            "error", "usage: remote_reboot.py reboot|wait [-h] [--node NODE]"
        )
        sys.exit(1)
