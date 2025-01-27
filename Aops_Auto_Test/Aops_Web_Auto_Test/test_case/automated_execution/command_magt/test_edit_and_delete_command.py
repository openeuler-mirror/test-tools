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
    def prepare_and_clean_data(self, command):
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

    def test_edit_unused_command_001_cancel(self, command):
        """
        编辑命令 - 取消编辑未在使用中的命令
        """
        command_name_new = self.command_name + '_new'
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(999)
        command.edit_command(self.command_name, command_name_new, timeout, command_content, action='cancel')
        new_loc = command.replace_locator_text(command_elem['command_list'], command_name_new)
        assert not command.find_element(new_loc)

    def test_edit_unused_command_002(self, command):
        """
        编辑命令 - 编辑未在使用中的命令
        """
        command_name_new = self.command_name + '_new'
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(999)
        command.edit_command(self.command_name, command_name_new, timeout, command_content)
        self.command_name = command_name_new
        assert command.get_notice_text() in ("编辑成功", "Update Succeed")

    def test_delete_unused_command_001_cancel(self, command):
        """
        删除命令 - 取消删除不在执行中的命令
        """
        command.delete_command(self.command_name, action='cancel')
        new_loc = command.replace_locator_text(command_elem['command_list'], self.command_name)
        assert command.find_element(new_loc)

    def test_delete_unused_command_002(self, command):
        """
        删除命令 - 删除不在执行中的命令
        """
        command.delete_command(self.command_name)
        self.command_name = None
        assert command.get_notice_text() in ("删除成功", "Delete Succeed")


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/command_magt/test_edit_and_delete_command.py', '-s'])

