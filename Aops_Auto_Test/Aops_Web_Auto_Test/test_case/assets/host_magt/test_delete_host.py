# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage


class TestDeleteHost:

    @pytest.fixture(scope='class', autouse=True)
    def add_host_group(self, drivers):
        """添加主机组"""
        host = AssetMagtPage(drivers)
        global host_ip
        global host_group
        host_group = createtestdata.group()
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        host_ip = createtestdata.host_ip()
        host.enter_host_group_magt_page()
        host.add_host_group('local-cluster', host_group, 'group description')
        host.enter_host_magt_page()
        host.add_host(host_name, 'local-cluster', host_group, host_ip, port, '监控节点', 'root', 'openEuler12#$')
        assert host.get_host_info_from_table(host_ip)
        yield host_group, host_ip
        host.refresh()
        host.enter_host_group_magt_page()
        host.delete_host_group(host_group)

    def test_delete_host_001_valid_data(self, drivers):
        """删除存在的主机"""
        host = AssetMagtPage(drivers)
        host.delete_host(host_ip)
        host.refresh()
        assert host_ip not in host.get_host_ip_from_table()


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_magt/test_delete_host.py','-s'])
