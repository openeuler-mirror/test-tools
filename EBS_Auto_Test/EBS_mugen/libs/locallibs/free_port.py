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
 @Date    : 2021-04-22 17:03:00
 @License : Mulan PSL v2
 @Version : 1.0
 @Desc    : 查找空闲端口或检查端口是否空闲
"""


import os
import sys
import subprocess
import socket
import random
import telnetlib
import argparse

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_PATH)
import mugen_log


def find_free_port(ip="", start=1000, stop=10000):
    """查找未使用的端口号

    Args:
        ip (str, optional): 指定查找的ip地址，默认未本地. Defaults to "".
        start (int, optional): 空闲端口查找范围的起始端口号. Defaults to 1000.
        stop (int, optional): 空闲端口查找范围的结束端口号. Defaults to 10000.

    Returns:
        [int]: 空闲端口号
    """
    if start > stop:
        mugen_log.logging(
            "error",
            "The initial value of the port range must be less than or equal to the end value.",
        )
        sys.exit(2)

    if ip == "":
        conn = socket.socket()
    else:
        exitcode = subprocess.getstatusoutput("ping " + ip + " -c 1")[0]
        if exitcode != 0:
            mugen_log.logging("error", "Unable to establish connection with IP:" + ip)
            sys.exit(519)

    count = 0
    while count < 100:
        count += 1
        port = random.randint(start, stop)
        if ip == "":
            try:
                conn.bind(("", port))
                conn.close()
                return port
            except Exception:
                continue

        else:
            try:
                telnetlib.Telnet(ip, port)
                continue
            except Exception:
                return port


def is_free_port(port, ip=""):
    """检测端口号是否被使用

    Args:
        port ([int]): 需要被检查的端口号
        ip (str, optional): 需要检查端口号的机器ip地址. Defaults to "".

    Returns:
        [int]: 被使用-1，未被使用-0
    """
    if ip == "":
        conn = socket.socket()
    else:
        exitcode = subprocess.getstatusoutput("ping " + ip + " -c 1")[0]
        if exitcode != 0:
            mugen_log.logging("error", "Unable to establish connection with IP:" + ip)
            sys.exit(519)

    if ip == "":
        try:
            conn.bind(("", port))
            return 0
        except Exception:
            return 1
    else:
        try:
            telnetlib.Telnet(ip, port)
            return 1
        except Exception:
            return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="manual to this script")
    parser.add_argument("operation", type=str, choices=["get", "check"], default=None)
    parser.add_argument("--ip", type=str, default="")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--start", type=int, default=1000)
    parser.add_argument("--end", type=int, default=100000)

    args = parser.parse_args()

    if sys.argv[1] == "get":
        print(find_free_port(args.ip, args.start, args.end))
    elif sys.argv[1] == "check":
        sys.exit(is_free_port(args.port, args.ip))
    else:
        mugen_log.logging(
            "error",
            "usage: free_port.py get|install [-h] [--ip IP] [--port PORT] [--start START PORT] [--end END PORT]",
        )
        sys.exit(1)
