# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage

asset = Element('asset_magt')


class TestDeleteHostGroup:

    @pytest.fixture(scope="function")
    def add_group(self, drivers):
        group = AssetMagtPage(drivers)
        global group_name
        group_name = createtestdata.group()
        group_desc = createtestdata.group_desc()
        group.enter_host_group_magt_page()
        group.add_host_group('local-cluster', group_name, group_desc)

    @pytest.fixture(scope="function")
    def add_host(self, drivers, add_group):
        host = AssetMagtPage(drivers)
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        host_ip = createtestdata.host_ip()
        host.enter_host_magt_page()
        host.add_host(host_name, 'local-cluster', group_name, host_ip, port, '监控节点', 'root', 'openEuler12#$')
        yield
        host.enter_host_magt_page()
        host.delete_host(host_ip)
        host.enter_host_group_magt_page()
        host.delete_host_group(group_name)
        host.click_delete_button()

    def test_delete_host_group_001(self, drivers, add_group):
        """删除空闲的主机组"""
        group = AssetMagtPage(drivers)
        group.enter_host_group_magt_page()
        group.delete_host_group(group_name)
        group.click_delete_button()
        group_locator = group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name)
        assert not group.element_displayed(group_locator)

    def test_delete_host_group_002(self, drivers, add_host):
        """删除存在主机的主机组"""
        group = AssetMagtPage(drivers)
        group.enter_host_group_magt_page()
        group.delete_host_group(group_name)
        assert group.element_text(asset['delete_group_confirm_title']) == "主机组内有主机时无法删除"
        group.click_confirm_button()
        group_locator = group.replace_locator_text(Element('asset_magt')['group_name_column'], group_name)
        assert group.element_displayed(group_locator)


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_group_magt/test_delete_host_group.py', '-s'])
