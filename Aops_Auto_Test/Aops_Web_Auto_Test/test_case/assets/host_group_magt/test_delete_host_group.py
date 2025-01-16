# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage

asset = Element('asset_magt')


class TestDeleteHostGroup:

    @pytest.fixture(scope="class", autouse=True)
    def add_host(self, drivers):
        group = AssetMagtPage(drivers)
        global group_name1
        group_name1 = createtestdata.group()
        group_desc = createtestdata.group_desc()
        group.enter_host_group_magt_page()
        group.add_host_group('local-cluster', group_name1, group_desc)
        global group_name2
        group_name2 = createtestdata.group()
        group_desc = createtestdata.group_desc()
        group.enter_host_group_magt_page()
        group.add_host_group('local-cluster', group_name2, group_desc)
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        host_ip = createtestdata.host_ip()
        group.enter_host_magt_page()
        group.add_host(host_name, 'local-cluster', group_name2, host_ip, port, '监控节点', 'root', 'openEuler12#$')
        assert group.get_host_info_from_table(host_ip)
        yield
        group.enter_host_magt_page()
        group.delete_host(host_ip)
        group.refresh()
        group.enter_host_group_magt_page()
        group.delete_host_group(group_name2)

    def test_delete_host_group_001_empty_group(self, drivers):
        """删除空闲的主机组"""
        group = AssetMagtPage(drivers)
        group_locator = group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name1)
        group.enter_host_group_magt_page()
        group.delete_host_group(group_name1, action='cancel')
        assert group.element_displayed(group_locator)
        group.delete_host_group(group_name1)
        assert group.element_invisibility(group_locator)

    def test_delete_host_group_002_with_host(self, drivers):
        """删除存在主机的主机组"""
        group = AssetMagtPage(drivers)
        group.enter_host_group_magt_page()
        group.delete_host_group(group_name2, False, expected_reason="主机组内有主机时无法删除")
        group_locator = group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name2)
        assert group.element_displayed(group_locator)


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_group_magt/test_delete_host_group.py', '-s'])
