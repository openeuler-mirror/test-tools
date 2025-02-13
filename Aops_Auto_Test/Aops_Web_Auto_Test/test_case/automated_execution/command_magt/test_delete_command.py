# -*-coding:utf-8-*-
import time
import pytest
from selenium.common import TimeoutException
from Aops_Web_Auto_Test.common.createtestdata import create_new_name, generate_random_number, generate_content
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.command_magt import CommandManagementPage

command_elem = Element('command_magt')


@pytest.fixture(scope='class')
def command(drivers):
    return CommandManagementPage(drivers)


class TestDeleteCommand:
    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, command):
        command.enter_command_magt_page()
        self.command_name = create_new_name("command")
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(99)
        command.add_command(self.command_name, timeout, command_content)
        command.refresh()
        self.task_name = None
        self.host_group1 = ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP1")
        self.host1 = ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTNAME1")
        yield
        try:
            if self.task_name:
                command.delete_task(self.task_name)
            if self.command_name:
                command.delete_command(self.command_name)
        except (NameError, TimeoutException):
            pass

    def test_delete_unused_command_001_cancel(self, command):
        """
        删除命令 - 取消删除不在执行中的命令
        """
        command.delete_command(self.command_name, action='cancel')
        new_loc = command.replace_locator_text(command_elem['item_list'], self.command_name)
        assert command.find_element(new_loc)

    def test_delete_unused_command_002(self, command):
        """
        删除命令 - 删除不在执行中的命令
        """
        command.delete_command(self.command_name)
        assert command.get_notice_text() in ("删除成功", "Delete Succeed")
        command.click_refresh_button()
        new_loc = command.replace_locator_text(command_elem['item_list'], self.command_name)
        self.command_name = None
        assert not command.find_element(new_loc)

    def test_delete_completed_execution_command_003(self, command):
        """
        删除命令 - 删除已执行完成的命令
        """
        self.task_name = create_new_name("task")
        command.enter_add_task_page()
        command.input_task_name(self.task_name)
        command.select_host_group(self.host_group1)
        command.select_host(self.host1)
        command.select_command(self.command_name)
        command.click_element(command_elem['task_name_label'])
        command.add_task()
        assert command.get_notice_text() in ("创建成功", "Create Successfully")
        time.sleep(2)
        command.click_refresh_button()

        command.execute_task(self.task_name)
        time.sleep(2)
        command.click_refresh_button()

        new_loc = command.replace_locator_text(command_elem['re_execute_task'], self.task_name)
        while not command.find_element(new_loc):
            time.sleep(3)
            command.click_refresh_button()

        command.delete_command(self.command_name)
        assert command.get_notice_text() in ("删除成功", "Delete Succeed")
        command.click_refresh_button()
        new_loc = command.replace_locator_text(command_elem['item_list'], self.command_name)
        self.command_name = None
        assert not command.find_element(new_loc)


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/command_magt/test_delete_command.py', '-s'])

