# -*-coding:utf-8-*-
import pytest
import os
from selenium.common import TimeoutException
from Aops_Web_Auto_Test.page_object.script_magt import ScriptManagementPage
from Aops_Web_Auto_Test.utils.times import *
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.common.createtestdata import *
from Aops_Web_Auto_Test.config.conf import cm

script_elem = Element('script_magt')


class TestCreateNewScript:
    @pytest.fixture(scope='function', autouse=True)
    def enter_script_mgmt_page(self, drivers):
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_script_mgmt_page()

    @pytest.fixture(scope='function')
    def prepare_and_clean_data(self, drivers):
        script_mgmt = ScriptManagementPage(drivers)
        global operate_name_pre
        operate_name_pre = create_new_name("operate_name_pre")
        script_mgmt.create_new_operation(operate_name_pre)
        yield
        try:
            script_mgmt.click_element(script_elem['operation_mgmt'])
            script_mgmt.delete_operation(operate_name_pre)
            try:
                new_loc = script_mgmt.replace_locator_text(script_elem['operate_delete'], operate_name_pre)
                script_mgmt.element_invisibility(new_loc)
                script_mgmt.delete_operation(operate_name_002)
            except Exception as e:
                print(f"该操作名不存在：{e}")
                pass
        except Exception as e:
            print(f"清理环境过程报错：{e}")
            pass

    def test_create_new_script_001_data_consistency(self, drivers, prepare_and_clean_data):
        """新建脚本-数据一致性检查"""
        script_mgmt = ScriptManagementPage(drivers)
        operate_text = script_mgmt.get_operate_list()
        script_mgmt.enter_new_script()
        script_text = script_mgmt.get_script_operate_list()
        operate_name_list = script_text.split("\n")
        for operate_name_line in operate_name_list:
            assert operate_name_line in operate_text

    def test_create_new_script_002_create_new_operate(self, drivers, prepare_and_clean_data):
        """新建脚本-创建不存在的操作"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_new_script()
        global operate_name_002
        operate_name_002 = create_new_name("operate_name")
        script_mgmt.create_script_operate(operate_name_002, "confirm")
        script_mgmt.click_cancel_button()
        operate_text = script_mgmt.get_operate_list()
        assert operate_name_002 in operate_text
        script_mgmt.click_element(script_elem['operation_mgmt'])

    def test_create_new_script_003_create_exist_operate(self, drivers, prepare_and_clean_data):
        """新建脚本-创建已存在的操作"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_new_script()
        script_mgmt.create_script_operate(operate_name_pre, "confirm")
        log_info = script_mgmt.get_top_right_notice_text()
        script_mgmt.click_element(script_elem['script_operate_cancel'])
        script_mgmt.click_cancel_button()
        assert "data has existed" in log_info

    def test_create_new_script_004_create_operate_cancel(self, drivers):
        """新建脚本-创建操作过程中取消"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_new_script()
        operate_name = create_new_name("operate_name")
        script_mgmt.create_script_operate(operate_name, "cancel")
        operate_text = script_mgmt.get_operate_list()
        script_mgmt.enter_new_script()
        script_text = script_mgmt.get_script_operate_list()
        assert operate_name not in operate_text
        assert operate_name not in script_text

    def test_create_new_script_005_check_arch(self, drivers):
        """新建脚本-架构检查"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_new_script()
        arch_text = script_mgmt.get_arch_list()
        assert "aarch64" in arch_text
        assert "x86_64" in arch_text

    def test_create_new_script_006_check_os(self, drivers):
        """新建脚本-操作系统检查"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_new_script()
        os_text = script_mgmt.get_os_list()
        assert "openEuler" in os_text
        assert "CentOS" in os_text

    def test_create_new_script_007_upload_script(self, drivers):
        """新建脚本-正常文件上传与删除"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_new_script()
        script_mgmt.upload_file("script_mgmt_testfile.sh")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "script_mgmt_testfile.sh")
        script_mgmt.element_displayed(new_loc)
        upload_script_text1 = script_mgmt.element_text(script_elem['upload_script'])
        assert "script_mgmt_testfile.sh" in upload_script_text1
        script_mgmt.click_element(script_elem['delete_upload_script'])
        script_mgmt.element_invisibility(script_elem['delete_upload_script'])
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        script_mgmt.click_cancel_button()
        assert "script_mgmt_testfile.sh" not in upload_script_text

    def test_create_new_script_008_upload_script_size(self, drivers):
        """新建脚本-文件大小限制"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.create_test_file("test_script_2G.sh", 2)
        script_mgmt.create_test_file("test_script_3G.sh", 3)
        script_mgmt.enter_new_script()
        script_mgmt.upload_file("test_script_2G.sh")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "test_script_2G.sh")
        script_mgmt.element_displayed(new_loc)
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        assert "test_script_2G.sh" in upload_script_text
        script_mgmt.delete_test_file("test_script_2G.sh")
        script_mgmt.upload_file("test_script_3G.sh")
        log_info = script_mgmt.get_notice_text()
        assert "文件大小超过2G" in log_info
        script_mgmt.click_cancel_button()
        script_mgmt.delete_test_file("test_script_3G.sh")

    def test_create_new_script_009_upload_script_num(self, drivers):
        """新建脚本-文件数量限制"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_new_script()
        for i in range(101):
            script_mgmt.upload_file("script_mgmt_testfile.sh")
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        assert "最多上传100个文件" in upload_script_text
        script_mgmt.click_cancel_button()

    def test_create_new_script_010_upload_script_type(self, drivers):
        """新建脚本-文件类型限制"""
        script_mgmt = ScriptManagementPage(drivers)
        script_mgmt.enter_new_script()
        script_mgmt.copy_test_file("script_mgmt_testfile.sh", "test_script.txt")
        script_mgmt.upload_file("test_script.txt")
        script_mgmt.copy_test_file("script_mgmt_testfile.sh", "test_script.doc")
        script_mgmt.upload_file("test_script.doc")
        new_loc = script_mgmt.replace_locator_text(script_elem['upload_file_name'], "test_script.doc")
        script_mgmt.element_displayed(new_loc)
        upload_script_text = script_mgmt.element_text(script_elem['upload_script'])
        script_mgmt.click_cancel_button()
        assert "test_script.txt" in upload_script_text
        assert "test_script.doc" in upload_script_text
        script_mgmt.delete_test_file("test_script.txt")
        script_mgmt.delete_test_file("test_script.doc")


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/script_magt/test_create_new_script.py', '-s'])
