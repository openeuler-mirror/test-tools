# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.script_magt import ScriptManagementPage
from Aops_Web_Auto_Test.page_object.operation_magt import OptMagtPage
from Aops_Web_Auto_Test.common.readelement import Element
from selenium.common.exceptions import ElementClickInterceptedException
from Aops_Web_Auto_Test.utils.LogUtil import my_log
from Aops_Web_Auto_Test.common.createtestdata import *

log = my_log()
script_elem = Element('script_magt')


@pytest.fixture(scope='class')
def script_mgmt(drivers) -> ScriptManagementPage:
    return ScriptManagementPage(drivers)


@pytest.fixture(scope='class')
def operate_mgmt(drivers) -> OptMagtPage:
    return OptMagtPage(drivers)


class TestEditScriptTask:

    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, script_mgmt, operate_mgmt):
        script_mgmt.enter_script_mgmt_page()
        self.task_name_pre = None
        self.need_cancel = 0
        self.operate_name_pre = create_new_name("operate_name_pre")
        self.script_name_pre = create_new_name("script_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        script_mgmt.create_script_task(self.operate_name_pre, self.script_name_pre, "aarch64", "openEuler", "10", "top")
        yield
        if self.need_cancel:
            try:
                script_mgmt.click_cancel_button()
            except ElementClickInterceptedException:
                log.warn(f"have a ElementClickInterceptedException @page.cancel_button.click")
        try:
            script_mgmt.click_element(script_elem['operation_mgmt'])
            operate_mgmt.delete_operation(self.operate_name_pre)
            script_mgmt.delete_script(self.script_name_pre)
            if self.task_name_pre:
                script_mgmt.delete_script_exec_task(self.task_name_pre)
        except Exception as e:
            print(f"清理环境过程报错：{e}")
            pass

    def test_edit_script_task_001_check_field_editable(self, script_mgmt):
        """编辑脚本-检查字段可编辑性"""
        script_mgmt.enter_edit_script_task(self.script_name_pre)
        assert script_mgmt.element_is_editable(script_elem['enter_script_name'])
        assert script_mgmt.element_is_editable(script_elem['enter_arch'])
        assert script_mgmt.element_is_editable(script_elem['enter_os'])
        assert script_mgmt.element_is_editable(script_elem['enter_timeout'])
        assert script_mgmt.element_is_editable(script_elem['enter_command'])
        self.need_cancel = 1

    def test_edit_script_task_002_edit_unused_script(self, script_mgmt):
        """编辑脚本-修改未使用的脚本"""
        script_mgmt.enter_edit_script_task(self.script_name_pre)
        self.script_name_pre = self.script_name_pre + 'new'
        script_mgmt.edit_script_task(self.script_name_pre, "x86_64", "CentOS", "1", "ls")
        new_loc = script_mgmt.replace_locator_text(script_elem['script_delete'], self.script_name_pre)
        script_mgmt.element_displayed(new_loc)
        create_script_text = script_mgmt.get_script_list()
        assert self.script_name_pre + '\n' + self.operate_name_pre + " ls x86_64 CentOS" in create_script_text


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/script_magt/test_edit_script_task.py', '-s'])
