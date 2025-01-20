# -*-coding:utf-8-*-
import pytest
from selenium.common import TimeoutException
from Aops_Web_Auto_Test.common.createtestdata import create_new_name, generate_random_number, generate_content
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.command_magt import CommandManagementPage

command_elem = Element('command_magt')


@pytest.fixture(scope='class')
def command(drivers):
    return CommandManagementPage(drivers)


class TestEditAndDeleteCommand:
    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, drivers, command):
        command.enter_command_magt_page()
        self.command_name = create_new_name("command")
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(999)
        command.add_command(self.command_name, timeout, command_content)
        command.refresh()
        yield
        try:
            if self.command_name:
                command.delete_command(self.command_name)
        except (NameError, TimeoutException):
            pass

    def test_edit_command_001(self, drivers, command):
        """编辑未在使用中的命令"""
        command_name2 = create_new_name("command2")
        timeout2 = generate_random_number(1, 86400)
        command_content2 = generate_content(999)
        command.edit_command(self.command_name, command_name2, timeout2, command_content2)
        self.command_name = command_name2
        assert "编辑成功" in command.get_notice_text()

    def test_delete_command_001(self, drivers, command):
        """删除不在执行中的命令"""
        command.delete_command(self.command_name)
        self.command_name = None
        assert "删除成功" in command.get_notice_text()


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/command_magt/test_edit_and_delete_command.py', '-s'])

