# -*-coding:utf-8-*-
import os
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *
from Aops_Web_Auto_Test.common.createtestdata import *

script_elem = Element('script_magt')


class ScriptManagementPage(WebPage):

    def enter_script_mgmt_page(self):
        """进入脚本管理菜单"""
        expanded = self.get_element_attr(script_elem['automated_execution_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(script_elem['automated_execution_menu'])
        self.click_element(script_elem['script_mgmt_menu'])

    def create_new_operation(self, operate_name):
        """新建操作"""
        self.click_element(script_elem['operation_mgmt'])
        self.click_element(script_elem['new_operation'])
        self.click_element(script_elem['enter_the_operate'])
        self.input_text(script_elem['enter_the_operate'], operate_name)
        self.click_element(script_elem['determine'])

    def delete_operation(self, operate_name):
        """删除操作"""
        new_loc = self.replace_locator_text(script_elem['operate_delete'], operate_name)
        self.click_element(new_loc)
        self.click_element(script_elem['confirm'])

    def get_operate_list(self):
        """获取操作列表"""
        self.click_element(script_elem['operation_mgmt'])
        operate_text = self.element_text(script_elem['operate_table'])
        return operate_text

    def enter_new_script(self):
        """进入新建脚本页面"""
        self.click_element(script_elem['script_mgmt'])
        self.click_element(script_elem['new_script'])

    def get_script_operate_list(self):
        """获取新建脚本中的操作列表"""
        self.click_element(script_elem['enter_operate_name'])
        script_operate_text = self.element_text(script_elem['operate_list'])
        self.click_cancel_button()
        return script_operate_text

    def create_script_operate(self, operate_name, action='confirm'):
        """新建脚本中的新建操作"""
        self.click_element(script_elem['new_script_operate'])
        self.click_element(script_elem['enter_the_operate'])
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
        self.click_element(script_elem['enter_arch'])
        script_arch_text = self.element_text(script_elem['arch_list'])
        self.click_cancel_button()
        return script_arch_text

    def get_os_list(self):
        """获取新建脚本中的操作系统列表"""
        self.click_element(script_elem['enter_os'])
        script_os_text = self.element_text(script_elem['os_list'])
        self.click_cancel_button()
        return script_os_text

    def create_test_file(self, file_name, size_gb):
        """创建测试文件"""
        size_bytes = size_gb * 1024 ** 3
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        with open(file_path, 'wb') as file:
            file.seek(size_bytes - 1)
            file.write(b'\0')

    def delete_test_file(self, file_name):
        """删除测试文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"文件{file_path}不存在")

    def copy_test_file(self, file_name, file_name_new):
        """复制测试文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        file_path_new = cm.BASE_DIR + '/test_data/' + file_name_new
        if os.path.exists(file_path):
            os.system(f"cp {file_path} {file_path_new}")
        else:
            print(f"文件{file_path}不存在")
