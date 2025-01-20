# -*-coding:utf-8-*-
import pytest
from selenium.common import TimeoutException
from Aops_Web_Auto_Test.common.createtestdata import create_new_name, generate_random_number, generate_content
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.command_magt import CommandManagementPage
import random
import string

command_elem = Element('command_magt')


@pytest.fixture(scope='class')
def command(drivers):
    return CommandManagementPage(drivers)


class TestAddTask:
    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, drivers, command):
        command.enter_command_magt_page()
        self.command_name = create_new_name("command")
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(999)
        command.add_command(self.command_name, timeout, command_content)
        command.refresh()
        command.click_element(command_elem['command_execute'])
        self.is_cancel = None
        self.task_name = None
        yield
        try:
            if self.is_cancel:
                command.click_cancel_button()
            command.delete_command(self.command_name)
            if self.task_name:
                command.delete_task()
        except (NameError, TimeoutException):
            pass

    def test_add_task_001_invalid_task_name(self, drivers, command):
        self.is_cancel = True
        characters = string.ascii_letters + string.digits + ''.join(set(string.punctuation) - set("><"))
        # 任务名称为空
        task_name = ''
        command.add_task(task_name, ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP1"), ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTNAME1"), self.command_name)
        assert "请输入任务名称" in command.item_explain_error_info("任务名称")
        command.click_cancel_button()

        # 任务名称长度超过128个字符
        length = generate_random_number(129, 999)
        task_name = ''.join(random.choices(characters, k=length))
        command.add_task(task_name, ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP1"), ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTNAME1"),  self.command_name)
        assert "任务名称不能超过128字符" in command.item_explain_error_info("任务名称")

    def test_add_task_002_invalid_host_group(self, drivers, command):
        self.is_cancel = True
        # 主机组为空
        task_name = create_new_name("task")
        command.add_task(task_name, '', '', self.command_name)
        assert "请选择主机组" in command.item_explain_error_info("主机选择")
        command.click_cancel_button()

        # 选中的主机组下没有添加主机
        command.add_task(task_name, ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP0"), '', self.command_name)
        # assert "当前选择主机组下没有主机，请选择其他主机组" in command.get_notice_text()
        assert "No data found in database" in command.get_top_right_notice_text()

    def test_add_task_003_invalid_host(self, drivers, command):
        self.is_cancel = True
        # 主机为空
        task_name = create_new_name("task")
        command.add_task(task_name, ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP1"), '', self.command_name)
        assert "请选择主机" in command.item_explain_error_info("主机选择")


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/command_magt/test_add_task.py', '-s'])

