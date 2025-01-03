# -*-coding:utf-8-*-
import pytest
from selenium.common import TimeoutException

from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage

asset = Element('asset_magt')


class TestAddHostGroup:
    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, drivers):
        host_group = AssetMagtPage(drivers)
        host_group.enter_host_group_magt_page()
        yield
        try:
            global group_name
            host_group.delete_host_group(group_name)
            host_group.click_delete_button()
        except (NameError, TimeoutException):
            pass

    def test_add_host_group_001_valid_data(self, drivers):
        """所有信息正确，添加有效的主机组"""
        host_group = AssetMagtPage(drivers)
        global group_name
        group_name = createtestdata.group()
        group_desc = createtestdata.group_desc()
        host_group.add_host_group('local-cluster', group_name, group_desc)
        group = host_group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name)
        assert host_group.find_element(group)

    def test_add_host_group_002_invalid_data(self, drivers):
        """添加无效的主机组"""
        host_group = AssetMagtPage(drivers)
        host_group.add_host_group('local-cluster', 'q！@#￥%……&*（）', 'group description')
        assert "名称应由数字、小写字母、英文下划线组成" in host_group.item_explain_error_info("主机组名称")
        host_group.click_cancel_button()
        host_group.add_host_group('local-cluster', '!@^%asd', 'group description')
        assert "名称应由数字、小写字母、英文下划线组成" in host_group.item_explain_error_info("主机组名称")
        host_group.click_cancel_button()
        host_group.add_host_group('local-cluster', 'group_', 'group description')
        assert "以小写字母开头，且结尾不能是英文下划线" in host_group.item_explain_error_info("主机组名称")
        host_group.click_cancel_button()

    def test_add_host_group_003_exist_data(self, drivers):
        """添加已存在的主机组"""
        host_group = AssetMagtPage(drivers)
        global group_name
        group_name = createtestdata.group()
        group_desc = createtestdata.group_desc()
        host_group.add_host_group('local-cluster', group_name, group_desc)
        group = host_group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name)
        assert host_group.find_element(group)
        host_group.add_host_group('local-cluster', group_name, group_desc)
        assert host_group.get_top_right_notice_text() == "Data.Exist"

    def test_add_host_group_004_cancal_add_group(self, drivers):
        """添加已存在的主机组"""
        host_group = AssetMagtPage(drivers)
        global group_name
        group_name = createtestdata.group()
        group_desc = createtestdata.group_desc()
        host_group.click_element(asset['add_host_group'])
        host_group.find_element(asset['add_host_group_windows'])
        host_group.select_cluster('local-cluster')
        host_group.input_text(asset['host_group_name'], group_name)
        host_group.input_text(asset['host_group_description'], group_desc)
        host_group.click_cancel_button()
        group = host_group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name)
        assert host_group.element_displayed(group) == False


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_group_magt/test_add_host_group.py', '-s'])
