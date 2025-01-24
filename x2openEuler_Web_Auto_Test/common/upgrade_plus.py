"""
@Time : 2024/12/10 19:52
@Auth : ysc
@File : upgrade_plus.py
@IDE  : PyCharm
"""
import os
import subprocess
import util
from log import log


class Upgrade(object):
    def __init__(self, node, host_ip, src_os_name, node_arch):
        """
        加载节点信息
        :param node: 节点
        :param host_ip: 节点ip
        :param src_os_name: 源操作系统名称
        :param node_arch: 节点架构
        """
        self.check_result = None
        self.upgrade_check_output = None
        (self.node_name, self.node_info), = node.items()
        self.ip_upgrade = host_ip
        self.node_arch = node_arch
        self.src_os_name = src_os_name
        self.back_path = self.node_info["back_path"]
        self.parm_repo = self.node_info["target_os_repos"]
        self.target_os_name = self.node_info["target_os_name"]
        self.back_save_path = self.node_info["back_save_path"]
        self.back_ignore_path = self.node_info["back_ignore_path"]
        self.current_directory = subprocess.run(f"find {os.getcwd()} -type d -name 'x2openEuler'", shell=True,
                                                capture_output=True).stdout.decode("utf-8").strip("\n").split("\n")[0]
        self.repo_filename = f"migrate-{self.target_os_name}.repo"

    def install_rpm(self):
        """
        安装x2openEuler软件包
        :return:
        """
        install_rpm_flag = 0
        log.info(f"[+---] {self.ip_upgrade} : {self.src_os_name} -> {self.target_os_name} start to install rpm ....")
        if self.parm_repo.find(self.node_arch) < 0:
            log.error("yaml's repos is error, please check!")
            install_rpm_flag += 1

        repo_template = f"{self.current_directory}/test_file/repo/migrate-template.repo"
        with open(repo_template, "r") as file_repo:
            content = file_repo.read()
            lines = content.split("\n")
        node_repo = self.parm_repo.split(",")
        for i in range(len(node_repo)):
            if node_repo[i].find("everything") > 0:
                lines[2] = f"baseurl={node_repo[i]}"
            elif node_repo[i].find("EPOL") > 0:
                lines[8] = f"baseurl={node_repo[i]}"
            elif node_repo[i].find("update") > 0:
                lines[14] = f"baseurl={node_repo[i]}"
                install_rpm_flag += 2
            else:
                log.error(f"{node_repo[i]} can not find real repo!")
                install_rpm_flag += 2
        with open(f"{self.current_directory}/test_file/repo/{self.repo_filename}", "w") as file_repo:
            file_repo.write("\n".join(lines))

        rpm = subprocess.getoutput(f"find /etc/x2openEuler/rpms -name 'x2openEuler*upgrade*rpm' -type f "
                                   f"| grep E '{self.node_arch}'").split("\n")[0].split("/")[-1]
        if rpm:
            util.upload_file(self.node_info, self.ip_upgrade, local_dir="etc/x2openEuler/rpms", local_file=rpm,
                             remote_dir="/root/")
        else:
            log.error("rpm load failed !")
            install_rpm_flag += 4
        if "SUSE" in self.src_os_name:
            cmd_rpm_install = f"rpm -qa | grep x2openEuler | xargs rpm -e --nodeps &> /dev/null; " \
                              f"rpm -ivh /root/{rpm} --nodes"
        else:
            cmd_rpm_install = f"rpm -qa | grep x2openEuler | xargs rpm -e &> /dev/null; yum install {rpm} -y"
        rpm_install = util.exec_cmd(self.node_info, self.ip_upgrade, cmd_rpm_install)
        if rpm_install[0] != 0:
            log.error("rpm install is failed !")
            install_rpm_flag += 8
        util.exec_cmd(self.node_info, self.ip_upgrade, "source ~/.bashrc; mkdir /.osbak;")
        return install_rpm_flag

    def environment_check(self):
        """
        环境检查
        :return:
        """
        environment_check_flag = 0
        log.info(f"[+---] {self.ip_upgrade} : {self.src_os_name} -> {self.target_os_name} "
                 f"start to environment check ......")
        env_check = "echo $PATH > /opt/smt/root_path_result "
        pre_check = util.exec_cmd(self.node_info, self.ip_upgrade, env_check)
        if pre_check[0] != 0:
            log.error("environment_check is failed !")
            environment_check_flag = 1
        return environment_check_flag

    def upgrade_info_collect(self):
        """
        升级信息收集
        :return:
        """
        upgrade_info_collect_flag = 0
        log.info(f"[+---] {self.ip_upgrade} : {self.src_os_name} -> {self.target_os_name} "
                 f"start to upgrade_info_collect ......")
        cmd_upgrade_pre_check = "x2openEuler-client upgrade-check-collect 2>&1 | grep -Eo " \
                                "'/opt/x2openEuler-client/output/collect/.*?.tar.gz'"
        log.info(cmd_upgrade_pre_check)
        collect_check = util.exec_cmd(self.node_info, self.ip_upgrade, cmd_upgrade_pre_check)
        if collect_check[0] != 0:
            log.error("upgrade info collect is failed !")
            upgrade_info_collect_flag = 1
        return upgrade_info_collect_flag

    def upgrade_pre_check(self):
        """
        升级前环境检查
        :return:
        """
        upgrade_pre_check_flag = 0
        log.info(f"[+---] {self.ip_upgrade} : {self.src_os_name} -> {self.target_os_name} "
                 f"start to upgrade_pre_check ......")
        cmd_upgrade_pre_check = "x2openEuler-pre-check upgrade-check"
        log.info(cmd_upgrade_pre_check)
        upgrade_check = util.exec_cmd(self.node_info, self.ip_upgrade, cmd_upgrade_pre_check)
        if upgrade_check[0] != 0:
            log.error("upgrade_pre_check is failed !")
            upgrade_pre_check_flag += 1
        self.upgrade_check_output = upgrade_check[1]
        self.check_result = util.exec_cmd(self.node_info, self.ip_upgrade,
                                          f"find $(dirname {self.upgrade_check_output}) -type f | grep txt$")[1]
        return upgrade_pre_check_flag

    def upgrade(self):
        """
        OS升级
        :return:
        """
        upgrade_flag = 0
        log.info(f"[+---] {self.ip_upgrade} : {self.src_os_name} -> {self.target_os_name} "
                 f"start to upgrade ......")
        util.upload_file(self.node_info, self.ip_upgrade, local_dir=f"{self.current_directory}/test_file/repo",
                         local_file=self.repo_filename, remote_dir="/root/")
        subprocess.run(f"rm -rf {self.current_directory}/test_file/repo/{self.repo_filename}", shell=True,
                       capture_output=True)
        repo = f"/root/{self.repo_filename}"
        cmd_upgrade = f"/usr/bin/sh /opt/x2openEuler-upgrade/upgrade_entrance.sh upgrade {self.back_path} " \
                      f"{self.back_ignore_path} {self.back_save_path} empty_value {self.upgrade_check_output} " \
                      f"{self.check_result} OTHERS /root {repo} > ~/up.log 2>&1"
        log.info(f"{cmd_upgrade}")
        util.exec_cmd(self.node_info, self.ip_upgrade, cmd_upgrade)
        # 检查是否升级成功
        is_upgrade_success = util.exec_cmd(self.node_info, self.ip_upgrade,
                                           "grep 'please reboot as soon as possible' ~/up.log")
        if is_upgrade_success[0] != 0:
            log.info(f"[+++++] {self.ip_upgrade} : {self.src_os_name} -> {self.target_os_name} "
                     f"upgrade success! now is rebooting .......")
            util.exec_cmd(self.node_info, self.ip_upgrade, "reboot")
        else:
            log.error("upgrade is failed!")
            upgrade_flag += 1
        return upgrade_flag

    def rollback(self):
        rollback_flag = 0
        log.info(f"[+---] {self.ip_upgrade} : {self.src_os_name} -> {self.target_os_name} "
                 f"start to rollback ......")
        util.exec_cmd(self.node_info, self.ip_upgrade, "sh /opt/x2openEuler-upgrade/upgrade_entrance.sh "
                                                       "rollback OTHERS > ~/rb.log 2>&1")
        is_rollback_success = util.exec_cmd(self.node_info, self.ip_upgrade,
                                            "grep 'please reboot as soon as possible' ~/up.log")
        if is_rollback_success[0] != 0:
            log.info(f"[+---] {self.ip_upgrade} : {self.src_os_name} -> {self.target_os_name} rollback success! "
                     f"now is rebooting ......")
            util.exec_cmd(self.node_info, self.ip_upgrade, "reboot")
        else:
            log.info("rollback is failed!")
            rollback_flag += 1
        return rollback_flag
