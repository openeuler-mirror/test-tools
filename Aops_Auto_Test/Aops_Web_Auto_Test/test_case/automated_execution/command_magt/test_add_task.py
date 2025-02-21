# -*-coding:utf-8-*-
import time
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
    def prepare_and_clean_data(self, command):
        command.enter_command_magt_page()
        self.command_name = create_new_name("command")
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(99)
        command.add_command(self.command_name, timeout, command_content)
        command.refresh()
        self.need_cancel = 0
        self.task_name = None
        self.host_group0 = ini._get("CLUSTER.GROUP0", "CLUSTER_NAME1.GROUP0")
        self.host_group1 = ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP1")
        self.host1 = ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTNAME1")
        self.host_group2 = ini._get("CLUSTER.GROUP2", "CLUSTER_NAME1.GROUP2")
        self.host2 = ini._get("CLUSTER.GROUP2.HOST", "CLUSTER_NAME1.GROUP2.HOSTNAME2")
        self.host3 = ini._get("CLUSTER.GROUP2.HOST", "CLUSTER_NAME1.GROUP2.HOSTNAME3")
        yield
        try:
            if self.need_cancel:
                command.click_cancel_button()
            command.delete_command(self.command_name)
            if self.task_name:
                command.delete_task(self.task_name)
        except (NameError, TimeoutException):
            pass

    def test_add_task_001_invalid_task_name(self, command):
        """
        新建任务 - 校验任务名
        """
        self.need_cancel = 1
        characters = string.ascii_letters + string.digits + ''.join(set(string.punctuation) - set("><"))
        # 任务名称为空
        command.enter_add_task_page()
        task_name = ''
        command.input_task_name(task_name)
        command.add_task()
        assert command.get_item_explain_error("form_item_task_name") in ("请输入任务名称", "Please enter the task name")
        command.click_cancel_button()

        # 任务名称长度超过128个字符
        command.enter_add_task_page()
        length = generate_random_number(129, 999)
        task_name = ''.join(random.choices(characters, k=length))
        command.input_task_name(task_name)
        command.add_task()
        assert command.get_item_explain_error("form_item_task_name") in ("任务名称不能超过128字符", "Name cannot exceed 128 characters")

    def test_add_task_002_invalid_host_group(self, command):
        """
        新建任务 - 校验主机组
        """
        self.need_cancel = 1
        # 主机组为空
        command.enter_add_task_page()
        command.select_host_group("")
        command.add_task()
        assert command.get_item_explain_error("form_item_host_group") in ("请选择主机组", "Please select the host group")

        # 选中的主机组下没有添加主机
        command.select_host_group(self.host_group0)
        assert command.get_notice_text() in ("当前选择主机组下没有主机，请选择其他主机组", "There are no hosts in the currently selected host group. Please select another host group.")

    def test_add_task_003_invalid_host(self, command):
        """
        新建任务 - 校验主机（主机为空）
        """
        self.need_cancel = 1
        command.enter_add_task_page()
        command.select_host_group(self.host_group1)
        command.select_host("")
        command.add_task()
        assert command.get_item_explain_error("form_item_host_group") in ("请选择主机", "Please select the host")

    def test_add_task_004_verify_host(self, command):
        """
        新建任务 - 校验是否显示主机信息
        """
        self.need_cancel = 1
        # 选中主机后，显示主机信息
        command.enter_add_task_page()
        command.select_host_group(self.host_group1)
        command.select_host(self.host1)
        new_loc = command.replace_locator_text(command_elem['selected_host'], self.host1)
        assert command.find_element(new_loc)

        # 删除主机，主机信息消失
        # 方式一：重复选择同一台主机
        command.select_host(self.host1)
        new_loc = command.replace_locator_text(command_elem['selected_host'], self.host1)
        assert not command.find_element(new_loc)

        # 方式二：点击所选主机后的x
        command.select_host(self.host1)
        command.delete_selected_content_method_1(self.host1)
        new_loc = command.replace_locator_text(command_elem['selected_host'], self.host1)
        assert not command.find_element(new_loc)

        # 方式三：点击所选主机列表操作栏的删除按钮
        command.select_host(self.host1)
        command.click_element(command_elem['task_name_label'])
        command.delete_selected_host_method_2(self.host1)
        new_loc = command.replace_locator_text(command_elem['selected_host'], self.host1)
        assert not command.find_element(new_loc)

    def test_add_task_005_invalid_command(self, command):
        """
        新建任务 - 校验命令（命令为空）
        """
        self.need_cancel = 1
        command.enter_add_task_page()
        command.select_command("")
        command.add_task()
        assert command.get_item_explain_error("form_item_command_list") in ("请选择", "Please select")

    def test_add_task_006_verify_command(self, command):
        """
        新建任务 - 校验是否显示所选命令信息
        """
        self.need_cancel = 1
        # 选中命令后，显示命令信息
        command.enter_add_task_page()
        time.sleep(1)
        command.select_command(self.command_name)
        new_loc = command.replace_locator_text(command_elem['item_list'], self.command_name)
        assert command.find_element(new_loc)

        # 删除命令，命令信息消失
        # 方式一：重复选择同一条命令
        command.select_command(self.command_name)
        new_loc = command.replace_locator_text(command_elem['item_list'], self.command_name)
        assert not command.find_element(new_loc)

        # 方式二：点击所选命令后的x
        command.select_command(self.command_name)
        command.delete_selected_content_method_1(self.command_name)
        new_loc = command.replace_locator_text(command_elem['item_list'], self.command_name)
        assert not command.find_element(new_loc)

        # 方式三：点击所选命令列表操作栏的删除按钮
        command.select_command(self.command_name)
        command.click_element(command_elem['task_name_label'])
        command.delete_selected_command_method_2(self.command_name)
        new_loc = command.replace_locator_text(command_elem['item_list'], self.command_name)
        assert not command.find_element(new_loc)

    def test_add_task_007_check_command_select_consistency(self, command):
        """
        新建任务 - 命令选择数据一致性检查
        """
        self.need_cancel = 1
        command_text = command.get_command_list()
        command_name_list = command.get_command_select_list()
        for command_name_line in command_name_list:
            assert command_name_line in command_text

    def test_add_task_008_single_host_single_command(self, command):
        """
        新建单主机单命令任务
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
        command.click_refresh_button()
        new_loc = command.replace_locator_text(command_elem['item_list'], self.task_name)
        assert command.find_element(new_loc)

    def test_add_task_009_multi_host_single_command(self, command):
        """
        新建多主机单命令任务
        """
        self.task_name = create_new_name("task")
        command.enter_add_task_page()
        command.input_task_name(self.task_name)
        command.select_host_group(self.host_group2)
        command.select_host(self.host2)
        command.select_host(self.host3)
        command.select_command(self.command_name)
        command.click_element(command_elem['task_name_label'])
        command.add_task()
        assert command.get_notice_text() in ("创建成功", "Create Successfully")
        command.click_refresh_button()
        new_loc = command.replace_locator_text(command_elem['item_list'], self.task_name)
        assert command.find_element(new_loc)

    def test_add_task_010_single_host_multi_command(self, command):
        """
        新建单主机多命令任务
        """
        self.command_name2 = create_new_name("command-2")
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(99)
        command.add_command(self.command_name2, timeout, command_content)
        command.refresh()

        self.task_name = create_new_name("task")
        command.enter_add_task_page()
        command.input_task_name(self.task_name)
        command.select_host_group(self.host_group1)
        command.select_host(self.host1)
        command.select_command(self.command_name)
        command.select_command(self.command_name2)
        command.click_element(command_elem['task_name_label'])
        command.add_task()
        assert command.get_notice_text() in ("创建成功", "Create Successfully")
        command.click_refresh_button()
        new_loc = command.replace_locator_text(command_elem['item_list'], self.task_name)
        assert command.find_element(new_loc)
        command.delete_command(self.command_name2)
        time.sleep(1)

    def test_add_task_011_multi_host_multi_command(self, command):
        """
        新建多主机多命令任务
        """
        self.command_name2 = create_new_name("command-2")
        timeout = generate_random_number(1, 86400)
        command_content = generate_content(99)
        command.add_command(self.command_name2, timeout, command_content)
        command.refresh()

        self.task_name = create_new_name("task")
        command.enter_add_task_page()
        command.input_task_name(self.task_name)
        command.select_host_group(self.host_group2)
        command.select_host(self.host2)
        command.select_host(self.host3)
        command.select_command(self.command_name)
        command.select_command(self.command_name2)
        command.click_element(command_elem['task_name_label'])
        command.add_task()
        assert command.get_notice_text() in ("创建成功", "Create Successfully")
        command.click_refresh_button()
        new_loc = command.replace_locator_text(command_elem['item_list'], self.task_name)
        assert command.find_element(new_loc)
        command.delete_command(self.command_name2)
        time.sleep(1)


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/command_magt/test_add_task.py', '-s'])

