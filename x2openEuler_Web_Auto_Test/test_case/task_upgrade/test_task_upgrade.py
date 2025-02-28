"""
@Time : 2025/1/7 9:10
@Auth : ysc
@File : test_task_upgrade.py
@IDE  : PyCharm
"""
import os
import pytest
from x2openEuler_Web_Auto_Test.config.config import get_test_config, get_config, data_path
from x2openEuler_Web_Auto_Test.common.ssh_cmd import SSHClient
from x2openEuler_Web_Auto_Test.common.util import get_kvm_ip
import x2openEuler_Web_Auto_Test.common.util as util
from x2openEuler_Web_Auto_Test.page_object.task_upgrade import TaskUpgrade
from x2openEuler_Web_Auto_Test.common.log import log

test_data_path = os.path.join(data_path, 'task_upgrade', "test_files/task_upgrade.yaml")


def retry_operation(node, res_index, expect_res, count):
    """
    重试机制
    :param count: 重试次数
    :param node: 节点信息
    :param res_index: 实际值索引
    :param expect_res: 预期值
    :return:
    """
    for attempt in range(1, count + 1):
        result = node.check_res(res_index)
        if result not in expect_res:
            return result
        log.info(f"retry task_node {attempt} times but failed")
        if expect_res == "升级失败":
            node.upgrade_retry_node()
        else:
            node.reboot_retry_node()
            if node.check_res(res_index) == "重启失败":
                expect_res = "重启失败"
    return node.check_res(res_index)


class TestTaskUpgrade:
    @pytest.fixture(params=get_test_config(test_data_path),
                    ids=["{}".format(case["case_name"]) for case in get_test_config(test_data_path)])
    def test_data(self, request):
        return request.param

    @pytest.fixture(autouse=True)
    def kvm_create_and_delete(self, request, test_data, drivers):
        """
        虚拟机创建与删除、环境准备与清理
        :return:
        """
        self.host = get_config().get('host')
        ssh = SSHClient(hostname=self.host.get('host_name'), port=self.host.get('port'),
                        username=self.host.get('user_name'), password=self.host.get('password'))
        log.info(f'case_name: {test_data["case_name"]}')

        # 获取节点信息模板
        self.node = get_config().get('node_to_migrate')
        self.node.update({
            'nick_name': test_data["node_name"],
            'source_sys_version': test_data['source_sys_version'],
            'target_sys_version': test_data['target_sys_version'],
            'repo_name': test_data['repo_name'],
        })
        self.target_os_version = test_data['target_os_version']

        # 创建虚拟机
        _code, address_res = ssh.execute_command(f"ccentos.sh {test_data['os_type_num']} {self.node['nick_name']}")
        self.node['ip'] = get_kvm_ip(address_res)
        log.info(f"kvm init success, name is {self.node['nick_name']}, ip is {self.node['ip']} ...")
        ssh.close()
        self.x2upgrade = TaskUpgrade(drivers)
        yield
        ssh.connect()
        # 删除 known_hosts
        del_known_host_cmd = "rm -rf /home/x2openEuler/.ssh/known_hosts"
        web_host = get_config().get('web_real_host')
        del_cmd = (f"/usr/local/Python-3.8.12/bin/python3 /home/autotest_py/cmd_support.py '{web_host['host_name']}' "
                   f"'{web_host['user_name']}' '{web_host['password']}' '{web_host['port']}' '{del_known_host_cmd}'")
        util.exec_cmd(self.host, self.host['host_name'], f"{del_cmd}")
        # 删除虚拟机
        ssh.execute_command(f"virsh destroy {self.node['nick_name']}")
        log.info(f"Domain {self.node['nick_name']} destroyed")
        ssh.execute_command(f"virsh undefine --nvram {self.node['nick_name']}")
        log.info(f"Domain {self.node['nick_name']} has been undefined")
        ssh.execute_command(f"rm -rf {self.host.get('qcow2')}/{self.node['nick_name']}.qcow2")
        ssh.close()

        # 用例失败时，删除node节点 避免ip重复占用
        test_result = getattr(request.node, 'test_result', None)
        if test_result and test_result.failed:
            log.info(f"测试 {test_data['case_name']} 失败， 删除node节点")
            self.x2upgrade.refresh()
            self.x2upgrade.del_node()
        # sleep 1 min
        self.x2upgrade.sleep(60)

    def test_task_upgrade(self):
        """
        os 系统升级
        :return:
        """
        self.x2upgrade.refresh()
        self.x2upgrade.create_task_upgrade()
        self.x2upgrade.add_single_node_upgrade(self.node)

        # 环境检查
        self.x2upgrade.env_check()
        env_ret = self.x2upgrade.check_res("env")
        assert env_ret == "检查通过"
        log.info("环境检查通过")

        # 升级前检查
        self.x2upgrade.upgrade_check()
        pre_env_ret = self.x2upgrade.check_res("pre_upgrade")
        assert pre_env_ret == "检查通过"
        log.info("升级前检查通过")

        # 升级
        self.x2upgrade.upgrade_node()
        upgrade_ret = self.x2upgrade.check_res("upgrade")
        if upgrade_ret == "升级失败":
            upgrade_ret = retry_operation(self.x2upgrade, "upgrade", "升级失败", 3)
        assert upgrade_ret in "升级完成（待重启生效）"
        log.info("升级完成（待重启生效）")

        # 重启节点
        self.x2upgrade.reboot_node()
        upgrade_after_reboot_ret = self.x2upgrade.check_res("upgrade_after_reboot")
        if upgrade_after_reboot_ret == "重启超时":
            upgrade_after_reboot_ret = retry_operation(self.x2upgrade, "upgrade_after_reboot", "重启超时", 6)
        assert upgrade_after_reboot_ret in "升级成功"

        # 升级后环境检查
        self.x2upgrade.post_upgrade_check()
        post_upgrade_ret = self.x2upgrade.check_res("post_upgrade")
        assert post_upgrade_ret in "检查通过"

        # 升级检查
        check_cmd = "cat /etc/os-release | grep 'VERSION'"
        send_cmd = (f"/usr/local/Python-3.8.12/bin/python3 /home/autotest_py/cmd_support.py '{self.node['ip']}' "
                    f"'{self.node['user_name']}' '{self.node['password']}' '{self.node['port']}' '{check_cmd}'")
        check_start_type = util.exec_cmd(self.host, self.host['host_name'], f"{send_cmd}")
        assert f"{self.target_os_version[0]} ({self.target_os_version[1]})" in check_start_type[1]
        log.info(f"已升级至OE{self.target_os_version[0]}-{self.target_os_version[1]}系统")

        # 回退节点
        self.x2upgrade.rollback_node()
        roll_back_ret = self.x2upgrade.check_res("roll_back")
        assert "回退完成（待重启生效）" in roll_back_ret
        log.info("回退完成（待重启生效）")

        # 重启节点
        self.x2upgrade.rollback_reboot_node()
        roll_back_after_reboot_ret = self.x2upgrade.check_res("roll_back_after_reboot")
        if roll_back_after_reboot_ret == "重启超时":
            roll_back_after_reboot_ret = retry_operation(self.x2upgrade, "roll_back_after_reboot", "重启超时", 6)
        assert "待升级" in roll_back_after_reboot_ret
        log.info("回退成功")

        # 删除节点
        self.x2upgrade.del_node()

