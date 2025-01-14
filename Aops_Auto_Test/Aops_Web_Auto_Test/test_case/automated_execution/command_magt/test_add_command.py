# -*-coding:utf-8-*-
import pytest
from selenium.common import TimeoutException
from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.command_magt import CommandManagementPage
import random
import string

command_elem = Element('command_magt')


@pytest.fixture(scope='class')
def command(drivers):
    return CommandManagementPage(drivers)


class TestAddCommand:
    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, drivers, command):
        command.enter_command_magt_page()
        self.is_cancel = None
        self.command_name = None
        yield
        try:
            if self.is_cancel:
                command.click_cancel_button()
            if self.command_name:
                command.delete_command(self.command_name)
        except (NameError, TimeoutException):
            pass

    def test_add_command_001_invalid_data(self, drivers, command):
        self.is_cancel = True
        characters = string.ascii_letters + string.digits + ''.join(set(string.punctuation) - set("><"))
        # 命令名称长度超过128个字符
        length = random.randint(129, 999)
        command_name = ''.join(random.choices(characters, k=length))
        command_timeout = createtestdata.command_timeout()
        command_content = createtestdata.command_content()
        command.add_command(command_name, command_timeout, command_content)
        assert "命令名称长度不超过128个字符" in command.item_explain_error_info("命令名称")
        command.click_cancel_button()

        # 超时时间大于86400
        command_name = createtestdata.command_name()
        command_timeout = random.randint(86401, 99999)
        command.add_command(command_name, command_timeout, command_content)
        assert "超时时间需在1-86400之间" in command.item_explain_error_info("超时时间")

        # # 命令内容长度超过65535个字符
        # command_timeout = createtestdata.command_timeout()
        # length = random.randint(65536, 99999)
        # command_content = ''.join(random.choices(characters, k=length))
        # command.add_command(command_name, command_timeout, command_content)
        # assert "命令内容长度不超过65535个字符" in command.item_explain_error_info("命令内容")
        # command.click_cancel_button()

    def test_add_command_004_invalid_data(self, drivers, command):
        self.is_cancel = True
        """无效边界值校验"""
        command_name = ''
        command_content = ''
        command_timeout = ''
        command.add_command(command_name, command_timeout, command_content)
        assert "请输入命令名称" in command.item_explain_error_info("命令名称")
        assert "请输入超时时间" in command.item_explain_error_info("超时时间")
        assert "请输入命令内容" in command.item_explain_error_info("命令内容")
        command.click_cancel_button()
        command_timeout = 0
        command.add_command(command_name, command_timeout, command_content)
        assert "超时时间需在1-86400之间" in command.item_explain_error_info("超时时间")

    def test_add_command_004_01_valid_data(self, drivers, command):
        """有效边界值校验，输入最短有效内容"""
        characters = string.ascii_letters + string.digits
        # 命令名称长度等于1个字符
        command_name = ''.join(random.choices(characters, k=1))
        # 超时时间为1
        command_timeout = 1
        # 命令内容长度等于1个字符
        command_content = ''.join(random.choices(characters, k=1))
        command.add_command(command_name, command_timeout, command_content)
        self.command_name = command_name
        new_command_name = command.replace_locator_text(command_elem['command_list'], command_name)
        command.refresh()
        assert command.find_element(new_command_name)

    def test_add_command_004_02_valid_data(self, drivers, command):
        """有效边界值校验，输入最长有效内容"""
        characters = string.ascii_letters + string.digits
        # 命令名称长度等于128个字符
        command_name = ''.join(random.choices(characters, k=128))
        # 超时时间为86400
        command_timeout = 86400
        # 命令内容长度等于65535个字符
        command_content = ''.join(random.choices(characters, k=9999))
        command.add_command(command_name, command_timeout, command_content)
        self.command_name = command_name
        new_command_name = command.replace_locator_text(command_elem['command_list'], command_name)
        command.refresh()
        assert command.find_element(new_command_name)

    def test_add_command_006_exist_data(self, drivers, command):
        """添加已经存在的命令"""
        self.is_cancel = True
        command_name = createtestdata.command_name()
        command_timeout = createtestdata.command_timeout()
        command_content = createtestdata.command_content()
        command.add_command(command_name, command_timeout, command_content)
        self.command_name = command_name
        new_command_name = command.replace_locator_text(command_elem['command_list'], command_name)
        command.refresh()
        assert command.find_element(new_command_name)
        command.add_command(command_name, command_timeout, command_content)
        assert command.get_top_right_notice_text() == "data has existed"

    def test_add_command_008_cancel_add_command(self, drivers, command):
        """取消添加命令"""
        command_name = createtestdata.command_name()
        command_timeout = createtestdata.command_timeout()
        command_content = createtestdata.command_content()
        command.add_command(command_name, command_timeout, command_content, action='cancel')
        new_command_name = command.replace_locator_text(command_elem['command_list'], command_name)
        command.refresh()
        assert not command.find_element(new_command_name)


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/command_magt/test_add_command.py', '-s'])

