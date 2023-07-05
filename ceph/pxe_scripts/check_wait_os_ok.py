#!/usr/bin/env python3
# -*- * coding: utf-8 -*-
import sys
import time

import paramiko


def check_wait_os_ok(node_ip="", port=22, username="root", password=""):
    for _ in range(60):
        try:
            ssh = paramiko.SSHClient()
            know_host = paramiko.AutoAddPolicy()
            ssh.set_missing_host_key_policy(know_host)
            ssh.connect(node_ip, port, username, password,
                        allow_agent=False)
            ssh.close()
        except Exception as err:
            print(err)
            print("sleep 30")
            time.sleep(30)
            continue
        else:
            print(f"check {node_ip} os is ok")
            break


if __name__ == '__main__':
    if len(sys.argv) != 5:
        raise Exception("param error")
    else:
        check_wait_os_ok(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

