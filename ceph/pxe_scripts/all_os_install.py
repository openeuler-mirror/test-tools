#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import yaml
from pathlib import Path

current_path = Path(__file__).cwd()
server_info_yaml = current_path.joinpath("server_info.yaml")
conf_path = current_path.joinpath("conf")


with open(server_info_yaml, "r") as f:
    server_info = yaml.safe_load(f)

for bmc_ip, info in server_info.items():
    print(bmc_ip)
    for key, value in info.items():
        print(f"sed -i 's#{key}=.*#{key}={value}' {conf_path}")
        os.system(f"sed -i 's#{key}=.*#{key}={value}#' {conf_path}")
    os.system(f"cd {current_path};sh pxe_install.sh")

for bmc_ip, info in server_info.items():
    os_ip = info["manage_ip"]
    print(f"cd {current_path};python3 check_wait_os_ok.py {os_ip} 22 root huawei@2022")
    os.system(f"cd {current_path};python3 check_wait_os_ok.py {os_ip} 22 root huawei@2022")
