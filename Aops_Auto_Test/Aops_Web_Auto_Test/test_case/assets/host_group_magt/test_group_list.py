# -*-coding:utf-8-*-
import pytest

from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage

asset = Element('asset_magt')


class TestGroupList:

    @pytest.fixture(scope="class", autouse=True)
    def add_delete_group_and_host(self, drivers):
        group = AssetMagtPage(drivers)
        global group_name
        group_name = createtestdata.group()
        group_desc = createtestdata.group_desc()
        group.enter_host_group_magt_page()
        group.add_host_group('local-cluster', group_name, group_desc)
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        global host_ip
        host_ip = createtestdata.host_ip()
        group.enter_host_magt_page()
        group.add_host(host_name, 'local-cluster', group_name, host_ip, port, '监控节点', 'root', 'openEuler12#$')
        assert group.get_host_info_from_table(host_ip)
        yield
        group.refresh()
        group.enter_host_magt_page()
        group.delete_host(host_ip)
        group.refresh()
        group.enter_host_group_magt_page()
        group.delete_host_group(group_name)

    def test_group_list_001_view_host_in_group(self, drivers):
        """查看组内主机"""
        group = AssetMagtPage(drivers)
        group.enter_host_group_magt_page()
        assert group.view_host_in_group(group_name) == host_ip

    def test_group_list_002_check_group_num(self, drivers):
        """查看主机组列表总数正确,包含table左上角显示的数字，列表实际的行数，翻页的总数"""
        group = AssetMagtPage(drivers)
        group.enter_host_group_magt_page()
        assert group.get_table_num_from_lower_right() == group.get_table_num_from_upper_left()\
               == group.get_total_table_rows()


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_group_magt/test_group_list.py','-s'])
