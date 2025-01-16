# -*-coding:utf-8-*-
import logging

import pytest
from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
logger = logging.getLogger(__name__)
asset = Element('asset_magt')
group_name = ""
group_desc = ""


class TestAddHostGroup:

    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, drivers):
        host_group = AssetMagtPage(drivers)
        global group_name, group_desc
        group_name = createtestdata.group()
        group_desc = createtestdata.group_desc()
        yield
        try:
            host_group.delete_host_group(group_name)
        except Exception as e:
            print(f"Teardown失败： {e}")
            pass

    def test_add_host_group_001_valid_data(self, drivers):
        """所有信息正确，添加有效的主机组"""
        host_group = AssetMagtPage(drivers)
        host_group.enter_host_group_magt_page()
        host_group.add_host_group('local-cluster', group_name, group_desc)
        group = host_group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name)
        assert host_group.element_displayed(group)

    def test_add_host_group_002_invalid_data(self, drivers):
        """添加无效的主机组"""
        host_group = AssetMagtPage(drivers)
        host_group.add_host_group('local-cluster', '@#￥%……&*（）', 'group description')
        assert "主机组名称以小写字母开头，且不以英文下划线结尾" in host_group.item_explain_error_info("主机组名称")
        host_group.click_cancel_button()
        host_group.add_host_group('local-cluster', 'q#$%^&*_', 'group description')
        assert "主机组名称以小写字母开头，且不以英文下划线结尾" in host_group.item_explain_error_info("主机组名称")
        host_group.click_cancel_button()
        host_group.add_host_group('local-cluster', '', 'group description')
        assert "请输入主机组名称" in host_group.item_explain_error_info("主机组名称")
        host_group.click_cancel_button()
        host_group.add_host_group('local-cluster', 'dssdddddddddddddddddddddddd', 'group description')
        assert "主机组名称长度应小于20" in host_group.item_explain_error_info("主机组名称")
        host_group.click_cancel_button()

    def test_add_host_group_003_exist_data(self, drivers):
        """添加已存在的主机组"""
        host_group = AssetMagtPage(drivers)
        host_group.enter_host_group_magt_page()
        host_group.add_host_group('local-cluster', group_name, group_desc)
        group = host_group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name)
        assert host_group.find_element(group)
        host_group.add_host_group('local-cluster', group_name, group_desc)
        assert host_group.get_top_right_notice_text() == "Data.Exist"

    def test_add_host_group_004_cancel(self, drivers):
        """取消添加主机组"""
        host_group = AssetMagtPage(drivers)
        host_group.enter_host_group_magt_page()
        host_group.add_host_group('local-cluster', group_name, group_desc, action='cancel')
        group = host_group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name)
        assert host_group.element_invisibility(group)


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_group_magt/test_add_host_group.py', '-s'])
