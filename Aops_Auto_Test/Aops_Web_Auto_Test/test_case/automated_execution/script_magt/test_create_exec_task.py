# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.script_magt import ScriptManagementPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.operation_magt import OptMagtPage
from selenium.common.exceptions import ElementClickInterceptedException
from Aops_Web_Auto_Test.utils.LogUtil import my_log
from Aops_Web_Auto_Test.common.createtestdata import *
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.common.readconfig import ini

log = my_log()
script_elem = Element('script_magt')


@pytest.fixture(scope='class')
def script_mgmt(drivers) -> ScriptManagementPage:
    return ScriptManagementPage(drivers)


@pytest.fixture(scope='class')
def operate_mgmt(drivers) -> OptMagtPage:
    return OptMagtPage(drivers)


class TestCreateExecTask:

    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, script_mgmt, operate_mgmt):
        script_mgmt.enter_script_mgmt_page()
        self.task_name_pre = None
        self.need_cancel = 0
        self.host1 = ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTNAME1")
        self.group1 = ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP1")
        self.operate_name_pre = None
        yield
        if self.need_cancel:
            try:
                script_mgmt.click_cancel_button()
            except ElementClickInterceptedException:
                log.warn(f"have a ElementClickInterceptedException @page.cancel_button.click")
        try:
            if self.operate_name_pre:
                script_mgmt.click_element(script_elem['operation_mgmt'])
                operate_mgmt.delete_operation(self.operate_name_pre)
            if self.task_name_pre:
                script_mgmt.delete_script_exec_task(self.task_name_pre)
        except Exception as e:
            print(f"清理环境过程报错：{e}")
            pass

    def test_create_exec_task_001_check_task_name_length(self, script_mgmt):
        """新建任务-任务名称长度校验"""
        script_task_name = repo_name(128)
        task_page_text = script_mgmt.create_script_exec_task_name(script_task_name, "cancel")
        assert "任务名称不能超过128字符" not in task_page_text
        script_task_name = repo_name(129)
        task_page_text = script_mgmt.create_script_exec_task_name(script_task_name, "cancel")
        assert "任务名称不能超过128字符" in task_page_text

    def test_create_exec_task_002_check_task_name(self, script_mgmt, operate_mgmt):
        """新建任务-任务名称校验"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.task_name_pre = create_new_name("task_name_pre")
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        exec_page_text = script_mgmt.get_script_exec_list()
        assert self.task_name_pre in exec_page_text
        script_mgmt.delete_script_exec_task(self.task_name_pre)
        self.task_name_pre = self.task_name_pre + '#$%^&*@#!'
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        exec_page_text = script_mgmt.get_script_exec_list()
        assert self.task_name_pre in exec_page_text
        task_page_text = script_mgmt.create_script_exec_task_name("", "cancel")
        assert "请输入任务名称" in task_page_text


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/script_magt/test_create_exec_task.py', '-s'])
