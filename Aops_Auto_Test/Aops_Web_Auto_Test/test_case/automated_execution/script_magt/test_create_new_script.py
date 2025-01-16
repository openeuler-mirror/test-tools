# -*-coding:utf-8-*-
import pytest
import os
from Aops_Web_Auto_Test.page_object.script_magt import ScriptManagementPage
from Aops_Web_Auto_Test.page_object.operation_magt import OptMagtPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.common.createtestdata import *
from Aops_Web_Auto_Test.config.conf import cm
from selenium.common.exceptions import ElementClickInterceptedException
from Aops_Web_Auto_Test.utils.LogUtil import my_log

log = my_log()
script_elem = Element('script_magt')


@pytest.fixture(scope='class')
def script_mgmt(drivers) -> ScriptManagementPage:
    return ScriptManagementPage(drivers)


@pytest.fixture(scope='class')
def operate_mgmt(drivers) -> OptMagtPage:
    return OptMagtPage(drivers)


class TestCreateNewScript:

    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, script_mgmt, operate_mgmt):
        script_mgmt.enter_script_mgmt_page()
        self.operate_name_pre = None
        self.operate_name_002 = None
        self.script_name_pre = None
        self.task_name_pre = None
        self.need_cancel = 0
        self.need_delete_files = []
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
            if self.operate_name_002:
                new_loc = script_mgmt.replace_locator_text(script_elem['script_delete'], self.operate_name_pre)
                script_mgmt.element_invisibility(new_loc)
                operate_mgmt.delete_operation(self.operate_name_002)
            if self.script_name_pre:
                script_mgmt.delete_script(self.script_name_pre)
            if self.task_name_pre:
                script_mgmt.delete_script_exec_task(self.task_name_pre)
            if self.need_delete_files:
                for file_name in self.need_delete_files:
                    script_mgmt.delete_test_file(file_name)
        except Exception as e:
            print(f"清理环境过程报错：{e}")
            pass

    def test_create_new_script_001_data_consistency(self, script_mgmt, operate_mgmt):
        """新建脚本-数据一致性检查"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        operate_name_list = script_mgmt.get_script_operate_list()
        operate_text = script_mgmt.get_operate_list()
        for operate_name_line in operate_name_list:
            assert operate_name_line in operate_text

    def test_create_new_script_002_create_new_operate(self, script_mgmt, operate_mgmt):
        """新建脚本-创建不存在的操作"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.operate_name_002 = create_new_name("operate_name_002")
        script_mgmt.create_script_operate(self.operate_name_002, "confirm")
        script_mgmt.click_cancel_button()
        operate_text = script_mgmt.get_operate_list()
        assert self.operate_name_002 in operate_text

    def test_create_new_script_003_create_exist_operate(self, script_mgmt, operate_mgmt):
        """新建脚本-创建已存在的操作"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        script_mgmt.create_script_operate(self.operate_name_pre, "confirm")
        log_info = script_mgmt.get_top_right_notice_text()
        script_mgmt.click_element(script_elem['script_operate_cancel'])
        self.need_cancel = 1
        assert "data has existed" in log_info

    def test_create_new_script_004_create_operate_cancel(self, script_mgmt):
        """新建脚本-创建操作过程中取消"""
        operate_name = create_new_name("operate_name")
        script_mgmt.create_script_operate(operate_name, "cancel")
        operate_text = script_mgmt.get_operate_list()
        script_text = script_mgmt.get_script_operate_list()
        assert operate_name not in operate_text
        assert operate_name not in script_text

    def test_create_new_script_005_check_arch(self, script_mgmt):
        """新建脚本-架构检查"""
        arch_text = script_mgmt.get_arch_list()
        assert "aarch64" in arch_text
        assert "x86_64" in arch_text

    def test_create_new_script_006_check_os(self, script_mgmt):
        """新建脚本-操作系统检查"""
        os_text = script_mgmt.get_os_list()
        assert "openEuler" in os_text
        assert "CentOS" in os_text

    def test_create_new_script_007_upload_script(self, script_mgmt):
        """新建脚本-正常文件上传与删除"""
        script_mgmt.enter_new_script()
        script_mgmt.upload_file("script_mgmt_testfile.sh")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "script_mgmt_testfile.sh")
        script_mgmt.element_displayed(new_loc)
        upload_script_text1 = script_mgmt.element_text(script_elem['upload_script'])
        assert "script_mgmt_testfile.sh" in upload_script_text1
        script_mgmt.click_element(script_elem['delete_upload_script'])
        script_mgmt.element_invisibility(script_elem['delete_upload_script'])
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        self.need_cancel = 1
        assert "script_mgmt_testfile.sh" not in upload_script_text

    def test_create_new_script_008_upload_script_size(self, script_mgmt):
        """新建脚本-文件大小限制"""
        script_mgmt.enter_new_script()
        script_mgmt.create_test_file("test_script_2G.sh", 2)
        script_mgmt.create_test_file("test_script_3G.sh", 3)
        script_mgmt.upload_file("test_script_2G.sh")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "test_script_2G.sh")
        script_mgmt.element_displayed(new_loc)
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        assert "test_script_2G.sh" in upload_script_text
        script_mgmt.upload_file("test_script_3G.sh")
        log_info = script_mgmt.get_notice_text()
        self.need_cancel = 1
        self.need_delete_files = ["test_script_2G.sh", "test_script_3G.sh"]
        assert "文件大小超过2G" in log_info

    def test_create_new_script_009_upload_script_num(self, script_mgmt):
        """新建脚本-文件数量限制"""
        script_mgmt.enter_new_script()
        for i in range(101):
            script_mgmt.upload_file("script_mgmt_testfile.sh")
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        self.need_cancel = 1
        assert "最多上传100个文件" in upload_script_text

    def test_create_new_script_010_upload_script_type(self, script_mgmt):
        """新建脚本-文件类型限制"""
        script_mgmt.enter_new_script()
        script_mgmt.copy_test_file("script_mgmt_testfile.sh", "test_script.txt")
        script_mgmt.upload_file("test_script.txt")
        script_mgmt.copy_test_file("script_mgmt_testfile.sh", "test_script.doc")
        script_mgmt.upload_file("test_script.doc")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "test_script.doc")
        script_mgmt.element_displayed(new_loc)
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        self.need_cancel = 1
        self.need_delete_files = ["test_script.txt", "test_script.doc"]
        assert "test_script.txt" in upload_script_text
        assert "test_script.doc" in upload_script_text

    def test_create_new_script_011_upload_script_name(self, script_mgmt):
        """新建脚本-文件名称限制"""
        script_mgmt.enter_new_script()
        self.script_name_len_255 = test_script_name(252) + '.sh'
        script_mgmt.copy_test_file("script_mgmt_testfile.sh", self.script_name_len_255)
        script_mgmt.upload_file(self.script_name_len_255)
        script_mgmt.copy_test_file("script_mgmt_testfile.sh", "test@#%script.sh")
        script_mgmt.upload_file("test@#%script.sh")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "test@#%script.sh")
        script_mgmt.element_displayed(new_loc)
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        self.need_cancel = 1
        self.need_delete_files = [self.script_name_len_255, "test@#%script.sh"]
        assert self.script_name_len_255 in upload_script_text
        assert "test@#%script.sh" in upload_script_text

    def test_create_new_script_012_upload_script_open(self, script_mgmt):
        """新建脚本-上传打开的文件"""
        script_mgmt.enter_new_script()
        file_name = cm.BASE_DIR + '/test_data/' + "script_mgmt_testfile.sh"
        file = open(file_name, "r")
        script_mgmt.upload_file("script_mgmt_testfile.sh")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "script_mgmt_testfile.sh")
        script_mgmt.element_displayed(new_loc)
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        self.need_cancel = 1
        file.close()
        assert "script_mgmt_testfile.sh" in upload_script_text

    def test_create_new_script_013_upload_script_privilege(self, script_mgmt):
        """新建脚本-文件权限管理"""
        script_mgmt.enter_new_script()
        script_mgmt.copy_test_file("script_mgmt_testfile.sh", "test_script1.sh")
        file_name = cm.BASE_DIR + '/test_data/' + "test_script1.sh"
        os.chmod(file_name, 0o666)
        script_mgmt.upload_file("script_mgmt_testfile.sh")
        script_mgmt.upload_file("test_script1.sh")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "test_script1.sh")
        script_mgmt.element_displayed(new_loc)
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        self.need_cancel = 1
        self.need_delete_files = ["test_script1.sh"]
        assert "script_mgmt_testfile.sh" in upload_script_text
        assert "test_script1.sh" in upload_script_text

    def test_create_new_script_014_create_task(self, script_mgmt, operate_mgmt):
        """新建脚本-生成有效任务"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.script_name_pre = create_new_name("script_name_pre")
        script_mgmt.create_script_task(self.operate_name_pre, self.script_name_pre, "aarch64", "openEuler", "3", "ls")
        new_loc = script_mgmt.replace_locator_text(script_elem['script_delete'], self.script_name_pre)
        script_mgmt.element_displayed(new_loc)
        create_script_text = script_mgmt.get_script_list()
        assert self.script_name_pre in create_script_text

    def test_create_new_script_015_create_exist_task(self, script_mgmt, operate_mgmt):
        """新建脚本-生成重复任务"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.script_name_pre = create_new_name("script_name_pre")
        script_mgmt.create_script_task(self.operate_name_pre, self.script_name_pre, "aarch64", "openEuler", "3", "ls")
        script_mgmt.create_script_task(self.operate_name_pre, self.script_name_pre, "aarch64", "openEuler", "3", "ls")
        log_info = script_mgmt.get_top_right_notice_text()
        self.need_cancel = 1
        assert "data has existed" in log_info

    def test_create_new_script_016_create_invalid_task(self, script_mgmt, operate_mgmt):
        """新建脚本-生成无效任务"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.script_name_pre = create_new_name("script_name_pre")
        self.task_name_pre = create_new_name("task_name_pre")
        script_mgmt.create_script_task(self.operate_name_pre, self.script_name_pre, "x86_64", "CentOS", "3", "uname -a")
        script_mgmt.create_script_exec_task(self.task_name_pre, "group1", "host1", self.operate_name_pre)
        new_loc = script_mgmt.replace_locator_text(script_elem['task_exec_button'], self.task_name_pre)
        script_mgmt.click_element(new_loc)
        log_info = script_mgmt.get_top_right_notice_text()
        assert "task start failed" in log_info

    def test_create_new_script_017_create_task_cancel(self, script_mgmt, operate_mgmt):
        """新建脚本-生成有效任务时取消"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        script_name = create_new_name("script_name_pre")
        script_mgmt.create_script_task(self.operate_name_pre, script_name, "aarch64", "openEuler", "3", "ls", "cancel")
        create_script_text = script_mgmt.get_script_list()
        assert script_name not in create_script_text


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/script_magt/test_create_new_script.py', '-s'])
