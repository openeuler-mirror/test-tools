# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage

asset = Element('asset_magt')


class TestViewHostInGroup:

    def test_view_host_in_group(self, drivers, create_data):
        """查看组内主机"""
        group = AssetMagtPage(drivers)
        group.enter_host_group_magt_page()
        group.view_host_in_group(create_data[-1])
        assert group.find_element(asset['own_host_page'])
        table_data = group.get_host_info_from_table()
        assert create_data[-1] in table_data


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_group_magt/test_view_host_in_group.py','-s'])
