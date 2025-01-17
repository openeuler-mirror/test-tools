# -*-coding:utf-8-*-
import os
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element

script_elem = Element('script_magt')


class ScriptManagementPage(WebPage):

    def enter_script_mgmt_page(self):
        """进入脚本管理菜单"""
        expanded = self.get_element_attr(script_elem['automated_execution_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(script_elem['automated_execution_menu'])
        self.click_element(script_elem['script_mgmt_menu'])

    def delete_script(self, script_name, action='confirm'):
        """删除脚本"""
        try:
            table_text = self.get_script_list()
            assert script_name in table_text
        except Exception as e:
            print(f"该操作或脚本名不存在：{e}")
            pass
        else:
            new_loc = self.replace_locator_text(script_elem['script_delete'], script_name)
            self.click_element(new_loc)
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")

    def get_operate_list(self):
        """获取操作列表"""
        self.click_element(script_elem['operation_mgmt'])
        self.page_resoure_load_complete()
        operate_text = self.element_text(script_elem['operate_mgmt_table'])
        return operate_text

    def get_script_list(self):
        """获取脚本列表"""
        self.click_element(script_elem['script_mgmt'])
        self.click_refresh_button()
        self.page_resoure_load_complete()
        script_text = self.element_text(script_elem['script_mgmt_table'])
        return script_text

    def enter_new_script(self):
        """进入新建脚本页面"""
        self.click_element(script_elem['script_mgmt'])
        self.click_element(script_elem['new_script'])

    def get_script_operate_list(self):
        """获取新建脚本中的操作列表"""
        self.enter_new_script()
        self.click_element(script_elem['enter_operate_name'])
        script_operate_text = self.element_text(script_elem['operate_list'])
        self.click_cancel_button()
        operate_name_list = script_operate_text.split("\n")
        return operate_name_list

    def create_script_operate(self, operate_name, action='confirm'):
        """新建脚本中的新建操作"""
        self.enter_new_script()
        self.click_element(script_elem['new_script_operate'])
        self.input_text(script_elem['enter_the_operate'], operate_name)
        try:
            if action == "confirm":
                self.click_element(script_elem['script_operate_determine'])
            elif action == "cancel":
                self.click_element(script_elem['script_operate_cancel'])
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def get_arch_list(self):
        """获取新建脚本中的架构列表"""
        self.enter_new_script()
        self.click_element(script_elem['enter_arch'])
        script_arch_text = self.element_text(script_elem['arch_list'])
        self.click_cancel_button()
        return script_arch_text

    def get_os_list(self):
        """获取新建脚本中的操作系统列表"""
        self.enter_new_script()
        self.click_element(script_elem['enter_os'])
        script_os_text = self.element_text(script_elem['os_list'])
        self.click_cancel_button()
        return script_os_text

    @staticmethod
    def create_test_file(file_name, size_gb):
        """创建测试文件"""
        size_bytes = size_gb * 1024 ** 3
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        with open(file_path, 'wb') as file:
            file.seek(size_bytes - 1)
            file.write(b'\0')

    @staticmethod
    def delete_test_file(file_name):
        """删除测试文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"文件{file_path}不存在")

    @staticmethod
    def copy_test_file(file_name, file_name_new):
        """复制测试文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        file_path_new = cm.BASE_DIR + '/test_data/' + file_name_new
        if os.path.exists(file_path):
            os.system(f"cp {file_path} {file_path_new}")
        else:
            print(f"文件{file_path}不存在")

    def create_script_task(self, operate_name, script_name, arch_name, os_name, timeout, command, action='confirm'):
        """创建脚本任务"""
        self.enter_new_script()
        self.click_element(script_elem['enter_operate_name'])
        new_loc = self.replace_locator_text(script_elem['select_operate_name'], operate_name)
        self.element_displayed(new_loc)
        self.click_element(new_loc)
        self.input_text(script_elem['enter_script_name'], script_name)
        self.click_element(script_elem['enter_arch'])
        new_loc = self.replace_locator_text(script_elem['select_arch'], arch_name)
        self.click_element(new_loc)
        self.click_element(script_elem['enter_os'])
        new_loc = self.replace_locator_text(script_elem['select_os'], os_name)
        self.click_element(new_loc)
        self.input_text(script_elem['enter_timeout'], timeout)
        self.input_text(script_elem['enter_command'], command)
        self.upload_file("script_mgmt_testfile.sh")
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def enter_edit_script_task(self, script_name):
        """进入编辑脚本任务页面"""
        self.click_element(script_elem['script_mgmt'])
        new_loc = self.replace_locator_text(script_elem['operate_edit'], script_name)
        self.click_element(new_loc)

    def edit_script_task(self, script_name, arch_name, os_name, timeout, command, action='confirm'):
        """编辑脚本任务"""
        self.clear_before_input_text(script_elem['enter_script_name'], script_name)
        self.click_element(script_elem['enter_arch'])
        new_loc = self.replace_locator_text(script_elem['select_arch'], arch_name)
        self.click_element(new_loc)
        self.click_element(script_elem['enter_os'])
        new_loc = self.replace_locator_text(script_elem['select_os'], os_name)
        self.click_element(new_loc)
        self.clear_before_input_text(script_elem['enter_timeout'], timeout)
        self.clear_before_input_text(script_elem['enter_command'], command)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def enter_create_new_task_page(self, ):
        """进入新建脚本执行任务页面"""
        self.click_element(script_elem['script_exec'])
        self.click_element(script_elem['open_new_task'])

    def create_script_exec_task(self, script_task_name, host_group_name, script_host_name, operate_name, action='confirm'):
        """创建脚本执行任务"""
        self.create_script_exec_task_name(script_task_name)
        self.click_element(script_elem['enter_host_group_name'])
        new_loc = self.replace_locator_text(script_elem['select_host_group'], host_group_name)
        self.click_element(new_loc)
        self.click_element(script_elem['enter_host_name'])
        new_loc = self.replace_locator_text(script_elem['select_host'], script_host_name)
        self.click_element(new_loc)
        self.click_element(script_elem['enter_task_operate_name'])
        new_loc = self.replace_locator_text(script_elem['select_task_operate'], operate_name)
        self.click_element(new_loc)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def create_script_exec_task_name(self, script_task_name, action='continue'):
        """创建脚本执行任务名称"""
        self.enter_create_new_task_page()
        self.clear_before_input_text(script_elem['enter_task_name'], script_task_name)
        self.click_confirm_button()
        task_page_text = self.element_text(script_elem['new_task_page'])
        try:
            if action == "continue":
                pass
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是空或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")
        return task_page_text

    def delete_script_exec_task(self, script_task_name):
        """删除脚本执行任务"""
        self.click_element(script_elem['script_exec'])
        self.click_refresh_button()
        script_exec_text = self.element_text(script_elem['script_exec_table'])
        try:
            assert script_task_name in script_exec_text
        except Exception as e:
            print(f"该任务名不存在：{e}")
            pass
        else:
            new_loc = self.replace_locator_text(script_elem['task_delete_button'], script_task_name)
            self.click_element(new_loc)
            self.click_confirm_button()

    def get_script_exec_list(self):
        """获取脚本执行列表"""
        self.click_element(script_elem['script_exec'])
        self.click_refresh_button()
        self.page_resoure_load_complete()
        script_exec_text = self.element_text(script_elem['script_exec_table'])
        return script_exec_text
