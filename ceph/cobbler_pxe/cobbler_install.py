#!/usr/bin/python3
import os
import subprocess
import time
import xmlrpc.client

import paramiko
import yaml


class CobblerCommand(object):
    def __init__(self, server_url, user, passwd):
        try:
            self.remote_server = xmlrpc.client.Server(server_url)
            self.token = self.remote_server.login(user, passwd)
        except Exception as e:
            exit('URL:%s no access' % server_url)

    def new_system(self, system_conf):
        system_id = self.remote_server.new_system(self.token)
        # check must parameter
        for key in ["name", "hostname", "profile", "power_address",
                    "power_user", "power_pass", "power_type", "modify_interface", "gateway"]:
            if key not in system_conf:
                raise Exception(f"{key} is must ")
        # del old system
        self.remote_server.remove_system(system_conf["name"], self.token)
        # add system info
        for key, value in system_conf.items():
            print(system_id, key, value, self.token)             
            self.remote_server.modify_system(system_id, key, value, self.token)
        self.remote_server.save_system(system_id, self.token)
        return system_id

    @staticmethod
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
        else:
            raise Exception("check os timeout")

    def generate_auto_ks(self, auto_adapter, profile, power_address, ks_templete=None):
        # copy templete
        if ks_templete:
            templete_ks = f"/var/lib/cobbler/templates/ks/{ks_templete}"
        else:
            templete_ks = f"/var/lib/cobbler/templates/ks/{profile}-ks.templete"
        # check templete
        if not os.path.exists(templete_ks):
            print(f"[Warning] {templete_ks} not exist, using commom-ks.templete")
            templete_ks = "/var/lib/cobbler/templates/ks/common-ks.templete"
        with open(templete_ks, "r", encoding="utf-8") as templete_f:
            target_ks_str = templete_f.read()
        target_ks_str = target_ks_str.replace("manage_ip", auto_adapter["manage_ip"])
        target_ks_str = target_ks_str.replace("manage_prefix", str(auto_adapter["manage_prefix"]))
        target_ks_str = target_ks_str.replace("manage_gateway", auto_adapter["manage_gateway"])
        target_ks_str = target_ks_str.replace("scsi-disk_uuid", auto_adapter["disk_uuid"])
        target_ks = f"/var/lib/cobbler/templates/ks/auto_ks/{power_address}-ks.cfg"
        os.makedirs(os.path.dirname(target_ks), exist_ok=True)
        with open(target_ks, "w", encoding="utf-8") as target_f:
            target_f.write(target_ks_str)

    def pxe_install(self, system_conf_list):

        system_ids = []
        manage_ips = []
        # add system
        for system_conf in system_conf_list:
            auto_adapter = system_conf.pop("auto_adapter")
            manage_ips.append(auto_adapter["manage_ip"])
            power_address = system_conf['power_address']
            self.generate_auto_ks(auto_adapter, system_conf["profile"], power_address, system_conf.get("ks_templete"))
            system_conf["autoinstall"] = f"ks/auto_ks/{power_address}-ks.cfg"
            system_conf.pop("ks_templete")
            system_id = self.new_system(system_conf)
            # set pxe boot
            set_boot_cmds = ["/usr/bin/ipmitool", "-I", "lanplus", "-H", system_conf["power_address"],
                             "-U", system_conf["power_user"], "-P", system_conf["power_pass"], "chassis", "bootdev"]
            print(subprocess.check_call(set_boot_cmds + ["disk", "options=persistent"], shell=False))
            # print(subprocess.check_call(set_boot_cmds + ["pxe"], shell=False))
            print(subprocess.check_call(set_boot_cmds + ["pxe", "options=efiboot"], shell=False))
            system_ids.append(system_id)
        # sync
        # self.remote_server.sync_dhcp(self.token)
        print(self.remote_server.sync(self.token))

        # reboot pxe install
        for system_conf in system_conf_list:

            # set pxe boot
            set_boot_cmds = ["/usr/bin/ipmitool", "-I", "lanplus", "-H", system_conf["power_address"],
                             "-U", system_conf["power_user"], "-P", system_conf["power_pass"], "chassis"]

            print(subprocess.check_call(set_boot_cmds + ["power", "reset"], shell=False))

        # check wait install
        for manage_ip in manage_ips:
            self.check_wait_os_ok(node_ip=manage_ip, password="huawei@2022")


if __name__ == '__main__':

    system_conf_list = []
    with open("cobbler_info.yaml") as f:
        config = yaml.safe_load(f)

        server_url = config["service"]["server_url"]
        user = config["service"]["user"]
        passwd = config["service"]["passwd"]
        command = CobblerCommand(server_url, user, passwd)
        for key, conf_info in config["system_info"].items():
            conf_info.update(
                {
                    "name": key,
                    "hostname": key,
                }
            )
            system_conf_list.append(conf_info)

    print(command.pxe_install(system_conf_list))

