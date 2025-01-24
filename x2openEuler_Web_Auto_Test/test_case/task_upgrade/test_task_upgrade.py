"""
@Time : 2025/1/7 9:10
@Auth : ysc
@File : test_task_upgrade.py
@IDE  : PyCharm
"""
import os
import pytest
from config.config import get_test_config, get_config, data_path
from common.ssh_cmd import SSHClient
from common.util import get_kvm_ip
import common.util as util
from page_object.task_upgrade import TaskUpgrade
from common.log import log

node_name = None
node_ip = None
target_os_version = None
node_src_os = None
node_target_os = None
repo_name = None
host = None
host_ip = None

test_data_path = os.path.join(data_path, 'task_upgrade', "test_files/task_upgrade.yaml")


class TestTaskUpgrade:

    @pytest.fixture(params=get_test_config(test_data_path))
    def test_data(self, request):
        return request.param

    @pytest.fixture(autouse=True)
    def kvm_create_and_delete(self, test_data):
        """
        虚拟机创建与删除、环境准备与清理
        :return:
        """
        global host, host_ip
        host = get_config().get('host')
        host_ip = host.get('host_name')
        ssh = SSHClient(hostname=host.get('host_name'), port=host.get('port'), username=host.get('user_name'),
                        password=host.get('password'))
        log.info(f'case_name: {test_data["case_name"]}')
        # 创建虚拟机
        global node_name
        node_name = test_data["node_name"]
        _code, address_res = ssh.execute_command(f"ccentos.sh {test_data['os_type_num']} {node_name}")

        global target_os_version
        target_os_version = test_data['target_os_version']

        global node_src_os
        node_src_os = test_data['source_sys_version']

        global node_target_os
        node_target_os = test_data['target_sys_version']

        global repo_name
        repo_name = test_data['repo_name']

        global node_ip
        node_ip = get_kvm_ip(address_res)
        log.info(f"kvm init success, name is {node_name}, ip is {node_ip} ...")
        ssh.close()
        yield
        ssh.connect()
        # 删除 known_hosts
        del_known_host_cmd = "rm -rf /home/x2openEuler/.ssh/known_hosts"
        web_host = get_config().get('web_real_host')
        del_cmd = (f"/usr/local/Python-3.8.12/bin/python3 /home/autotest_py/cmd_support.py '{web_host['host_name']}' "
                   f"'{web_host['user_name']}' '{web_host['password']}' '{web_host['port']}' '{del_known_host_cmd}'")
        util.exec_cmd(host, host_ip, f"{del_cmd}")
        # 删除虚拟机
        ssh.execute_command(f"virsh destroy {node_name}")
        log.info(f"Domain {node_name} destroyed")
        ssh.execute_command(f"virsh undefine --nvram {node_name}")
        log.info(f"Domain {node_name} has been undefined")
        ssh.execute_command(f"rm -rf {host.get('qcow2')}/{node_name}.qcow2")
        ssh.close()

    def test_task_upgrade(self, drivers):
        """
        os 系统升级
        :return:
        """
        env_info = get_config()

        x2upgrade = TaskUpgrade(drivers)
        x2upgrade.create_task_upgrade()
        # 获取节点信息模板
        node = env_info.get('node_to_migrate')
        node['ip'] = node_ip
        node['nick_name'] = node_name
        node['source_sys_version'] = node_src_os
        node['target_sys_version'] = node_target_os
        node['repo_name'] = repo_name
        x2upgrade.add_single_node_upgrade(node)

        # 环境检查
        x2upgrade.env_check()
        env_ret = x2upgrade.check_res("env")
        assert env_ret in "检查通过"
        log.info("环境检查通过")

        # 升级前检查
        x2upgrade.upgrade_check()
        pre_env_ret = x2upgrade.check_res("pre_upgrade")
        assert pre_env_ret in "检查通过"
        log.info("升级前检查通过")

        # 升级
        x2upgrade.upgrade_node()
        upgrade_ret = x2upgrade.check_res("upgrade")
        count = 0
        # 重试机制
        while upgrade_ret in "升级失败" and count < 3:
            count += 1
            x2upgrade.retry_node()
            upgrade_ret = x2upgrade.check_res("upgrade")
            log.info(f"retry task_node {count} times but failed !")
        assert upgrade_ret in "升级完成（待重启生效）"
        log.info("升级完成（待重启生效）")

        # 重启节点
        x2upgrade.reboot_node()
        upgrade_after_reboot_ret = x2upgrade.check_res("upgrade_after_reboot")
        assert upgrade_after_reboot_ret in "升级成功"

        # 升级后环境检查
        x2upgrade.post_upgrade_check()
        post_upgrade_ret = x2upgrade.check_res("post_upgrade")
        assert post_upgrade_ret in "检查通过"

        # 升级检查
        check_cmd = "cat /etc/os-release | grep 'VERSION'"
        send_cmd = (f"/usr/local/Python-3.8.12/bin/python3 /home/autotest_py/cmd_support.py '{node_ip}' "
                    f"'{node['user_name']}' '{node['password']}' '{node['port']}' '{check_cmd}'")
        check_start_type = util.exec_cmd(host, host_ip, f"{send_cmd}")
        assert f"{target_os_version}" in check_start_type[1]
        log.info(f"已升级至OE{target_os_version}系统")

        # 回退节点
        x2upgrade.rollback_node()
        roll_back_ret = x2upgrade.check_res("roll_back")
        assert "回退完成（待重启生效）" in roll_back_ret
        log.info("回退完成（待重启生效）")

        # 重启节点
        x2upgrade.rollback_reboot_node()
        roll_back_after_reboot_ret = x2upgrade.check_res("roll_back_after_reboot")
        assert "待升级" in roll_back_after_reboot_ret
        log.info("回退成功")

        # 删除节点
        x2upgrade.del_node()
