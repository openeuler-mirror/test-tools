# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object import asset_magt
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage

asset = Element('asset_magt')


class TestDeleteHostGroup:

    def test_delete_host_group_001(self, drivers, create_data):
        """删除空闲的主机组"""
        group = AssetMagtPage(drivers)
        group.delete_single_host_group(create_data[0])
        group.click_delete_button()
        assert create_data[0] not in group.find_element(asset['host_group_list'])

    def test_delete_host_group_002(self, drivers, create_data):
        """删除存在主机的主机组"""
        group = AssetMagtPage(drivers)
        group.delete_single_host_group(create_data[-1])
        group.click_delete_button()
        assert "主机组内有主机时无法删除" in group.get_source
        group.click_confirm_button()
        assert create_data[-1] in group.find_element(asset['host_group_list'])

    def test_delete_host_group_003(self, drivers, create_data):
        """批量删除主机组"""
        group = AssetMagtPage(drivers)
        group.batch_delete_data(create_data[0:-1])
        for group in create_data[0:-1]:
            assert group not in group.find_element(asset['host_group_list'])


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/login_test.py','-s'])
