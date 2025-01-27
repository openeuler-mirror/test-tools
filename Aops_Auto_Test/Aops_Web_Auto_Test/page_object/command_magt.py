# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element

command_elem = Element('command_magt')


class CommandManagementPage(WebPage):

    def enter_command_magt_page(self):
        """进入命令管理菜单"""
        expanded = self.get_element_attr(command_elem['automated_execution_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(command_elem['automated_execution_menu'])
        self.click_element(command_elem['command_magt_menu'])

    def add_command(self, command_name, command_timeout, command_content, action='confirm'):
        """新建命令"""
        self.click_element(command_elem['new_command'])
        self.find_element(command_elem['new_windows'])
        self.input_text(command_elem['command_name'], command_name)
        self.input_text(command_elem['timeout'], command_timeout)
        self.input_text(command_elem['content'], command_content)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action参数必须是confirm或者cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def delete_command(self, command_name, action='confirm'):
        """删除命令"""
        self.click_element(command_elem['command_magt'])
        new_loc = self.replace_locator_text(command_elem['delete_command'], command_name)
        self.click_element(new_loc)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action参数必须是confirm或者cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def edit_command(self, command_name, command_name_new, timeout, command_content, action='confirm'):
        """编辑命令"""
        self.click_element(command_elem['command_magt'])
        new_loc = self.replace_locator_text(command_elem['edit_command'], command_name)
        self.click_element(new_loc)
        self.find_element(command_elem['new_windows'])
        self.clear_before_input_text(command_elem['command_name'], command_name_new)
        self.clear_before_input_text(command_elem['timeout'], timeout)
        self.clear_before_input_text(command_elem['content'], command_content)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action参数必须是confirm或者cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def add_task_input_task_name(self, task_name):
        """新建任务-输入任务名"""
        self.click_element(command_elem['new_task'])
        self.find_element(command_elem['new_windows'])
        self.input_text(command_elem['task_name'], task_name)

    def select_command(self, command_name):
        """新建任务-选择命令"""
        if command_name != '':
            self.select_value_by_dropdown(command_elem["command_select"], command_name)

    def add_task(self, action='confirm'):
        """新建任务"""
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action参数必须是confirm或者cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def delete_task(self, task_name, action='confirm'):
        """删除任务"""
        new_loc = self.replace_locator_text(command_elem['delete_task'], task_name)
        self.click_element(new_loc)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action参数必须是confirm或者cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def delete_selected_content_method_1(self, item):
        """删除所选的主机/命令（方式一）"""
        new_loc = self.replace_locator_text(command_elem['delete_x'], item)
        self.click_element(new_loc)

    def delete_selected_host_method_2(self, host_name):
        """删除所选的主机（方式二）"""
        new_loc = self.replace_locator_text(command_elem['host_delete_button'], host_name)
        self.click_element(new_loc)

    def delete_selected_command_method_2(self, command_name):
        """删除所选的命令（方式二）"""
        new_loc = self.replace_locator_text(command_elem['command_delete_button'], command_name)
        self.click_element(new_loc)
