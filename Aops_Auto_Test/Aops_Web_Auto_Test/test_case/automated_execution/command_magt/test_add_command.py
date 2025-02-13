# -*-coding:utf-8-*-
import pytest
from selenium.common import TimeoutException
from Aops_Web_Auto_Test.common.createtestdata import create_new_name, generate_random_number, generate_content
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
    def prepare_and_clean_data(self, command):
        command.enter_command_magt_page()
        self.need_cancel = 0
        self.command_name = None
        yield
        try:
            if self.need_cancel:
                command.click_cancel_button()
            if self.command_name:
                command.delete_command(self.command_name)
        except (NameError, TimeoutException):
            pass

    def test_add_command_001_invalid_command_name(self, command):
        """
        新建命令 - 校验命令名称
        """
        self.need_cancel = 1
        characters = string.ascii_letters + string.digits + ''.join(set(string.punctuation) - set("><"))
        # 命令名称为空
        command_name = ''
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(999)
        command.add_command(command_name, timeout, command_content)
        assert command.get_item_explain_error("form_item_command_name") in ("请输入命令名称", "Please enter the command name")
        command.click_cancel_button()

        # 命令名称长度超过128个字符
        length = generate_random_number(129, 999)
        command_name = ''.join(random.choices(characters, k=length))
        command.add_command(command_name, timeout, command_content)
        assert command.get_item_explain_error("form_item_command_name") in ("命令名称长度不超过128个字符", "The command name cannot exceed 128")

    def test_add_command_002_invalid_command_timeout(self, command):
        """
        新建命令 - 校验超时时间
        """
        self.need_cancel = 1
        # 超时时间为空
        command_name = create_new_name("command")
        timeout = ''
        command_content = generate_content(999)
        command.add_command(command_name, timeout, command_content)
        assert command.get_item_explain_error("form_item_timeout") in ("请输入超时时间", "Please enter the timeout")
        command.click_cancel_button()

        # 超时时间为0
        timeout = 0
        command.add_command(command_name, timeout, command_content)
        assert command.get_item_explain_error("form_item_timeout") in ("超时时间需在1-86400之间", "Timeout must be between 1 and 86400")
        command.click_cancel_button()

        # 超时时间大于86400
        timeout = generate_random_number(86401, 99999)
        command.add_command(command_name, timeout, command_content)
        assert command.get_item_explain_error("form_item_timeout") in ("超时时间需在1-86400之间", "Timeout must be between 1 and 86400")

    def test_add_command_003_invalid_command_content(self, command):
        """
        新建命令 - 校验命令内容
        """
        self.need_cancel = 1
        # characters = string.ascii_letters + string.digits + ''.join(set(string.punctuation) - set("><"))
        # 命令内容为空
        command_name = create_new_name("command")
        timeout = generate_random_number(1, 86400)
        command_content = ''
        command.add_command(command_name, timeout, command_content)
        assert command.get_item_explain_error("form_item_content") in ("请输入命令内容", "Please enter the command content")

        # # 命令内容长度超过65535个字符
        # length = generate_random_number(65536, 99999)
        # command_content = ''.join(random.choices(characters, k=length))
        # command.add_command(command_name, timeout, command_content)
        # assert command.get_item_explain_error("form_item_content") in ("命令内容长度不超过65535个字符")

    def test_add_command_004_minimum_value(self, command):
        """
        新建命令 - 有效边界值校验，输入最短有效内容
        """
        characters = string.ascii_letters + string.digits
        # 命令名称长度等于1个字符
        command_name = ''.join(random.choices(characters, k=1))
        # 超时时间为1
        timeout = 1
        # 命令内容长度等于1个字符
        command_content = ''.join(random.choices(characters, k=1))
        command.add_command(command_name, timeout, command_content)
        command.click_refresh_button()
        self.command_name = command_name
        new_loc = command.replace_locator_text(command_elem['item_list'], command_name)
        assert command.find_element(new_loc)

    def test_add_command_005_maximum_value(self, command):
        """
        新建命令 - 有效边界值校验，输入最长有效内容
        """
        characters = string.ascii_letters + string.digits
        # 命令名称长度等于128个字符
        command_name = ''.join(random.choices(characters, k=128))
        # 超时时间为86400
        timeout = 86400
        # 命令内容长度等于65535个字符
        command_content = ''.join(random.choices(characters, k=9999))
        command.add_command(command_name, timeout, command_content)
        command.click_refresh_button()
        self.command_name = command_name
        new_loc = command.replace_locator_text(command_elem['item_list'], command_name)
        assert command.find_element(new_loc)

    def test_add_command_006_exist_data(self, command):
        """
        新建命令 - 添加已经存在的命令
        """
        self.need_cancel = 1
        command_name = create_new_name("command")
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(999)
        command.add_command(command_name, timeout, command_content)
        command.click_refresh_button()
        self.command_name = command_name
        new_loc = command.replace_locator_text(command_elem['item_list'], command_name)
        assert command.find_element(new_loc)
        command.add_command(command_name, timeout, command_content)
        assert command.get_top_right_notice_text() == "data has existed"

    def test_add_command_007_cancel_add_command(self, command):
        """
        新建命令 - 取消添加命令
        """
        command_name = create_new_name("command")
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(999)
        command.add_command(command_name, timeout, command_content, action='cancel')
        command.click_refresh_button()
        new_loc = command.replace_locator_text(command_elem['item_list'], command_name)
        assert not command.find_element(new_loc)


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/command_magt/test_add_command.py', '-s'])

