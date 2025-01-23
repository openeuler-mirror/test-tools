# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.script_magt import ScriptManagementPage
from Aops_Web_Auto_Test.page_object.operation_magt import OptMagtPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.common.createtestdata import *
from Aops_Web_Auto_Test.common.readconfig import ini

script_elem = Element('script_magt')


@pytest.fixture(scope='class')
def script_mgmt(drivers) -> ScriptManagementPage:
    return ScriptManagementPage(drivers)


@pytest.fixture(scope='class')
def operate_mgmt(drivers) -> OptMagtPage:
    return OptMagtPage(drivers)


class TestDeleteScriptTask:

    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, script_mgmt, operate_mgmt):
        script_mgmt.enter_script_mgmt_page()
        self.task_name_pre = None
        self.need_delete = 0
        self.host1 = ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTNAME1")
        self.group1 = ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP1")
        self.operate_name_pre = create_new_name("operate_name_pre")
        self.script_name_pre = create_new_name("script_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        script_mgmt.create_script_task(self.operate_name_pre, self.script_name_pre, "aarch64", "openEuler", "10", "top")
        yield
        try:
            script_mgmt.click_element(script_elem['operation_mgmt'])
            operate_mgmt.delete_operation(self.operate_name_pre)
            if self.need_delete:
                script_mgmt.delete_script(self.script_name_pre)
            if self.task_name_pre:
                script_mgmt.delete_script_exec_task(self.task_name_pre)
        except Exception as e:
            print(f"清理环境过程报错：{e}")
            pass

    def test_delete_script_task_001_delete_unused_script(self, script_mgmt):
        """删除脚本-删除未使用的脚本"""
        self.task_name_pre = create_new_name("task_name_pre")
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        script_mgmt.delete_script(self.script_name_pre)
        create_script_text = script_mgmt.get_script_list()
        assert self.script_name_pre not in create_script_text

    def test_delete_script_task_002_delete_script_in_use(self, script_mgmt):
        """删除脚本-删除正在使用的脚本"""
        self.task_name_pre = create_new_name("task_name_pre")
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        new_loc = script_mgmt.replace_locator_text(script_elem['task_exec_button'], self.task_name_pre)
        script_mgmt.click_element(new_loc)
        script_mgmt.click_element(script_elem['script_mgmt'])
        new_loc = script_mgmt.replace_locator_text(script_elem['script_delete'], self.script_name_pre)
        script_mgmt.element_displayed(new_loc)
        script_mgmt.delete_script(self.script_name_pre)
        create_script_text = script_mgmt.get_script_list()
        assert self.script_name_pre not in create_script_text

    def test_delete_script_task_003_delete_script(self, script_mgmt):
        """删除脚本-删除脚本(通用)"""
        script_mgmt.delete_script(self.script_name_pre)
        create_script_text = script_mgmt.get_script_list()
        assert self.script_name_pre not in create_script_text

    def test_delete_script_task_004_delete_script_cancel(self, script_mgmt):
        """删除脚本-取消删除脚本"""
        script_mgmt.delete_script(self.script_name_pre, "cancel")
        create_script_text = script_mgmt.get_script_list()
        self.need_delete = 1
        assert self.script_name_pre in create_script_text


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/script_magt/test_delete_script_task.py', '-s'])
