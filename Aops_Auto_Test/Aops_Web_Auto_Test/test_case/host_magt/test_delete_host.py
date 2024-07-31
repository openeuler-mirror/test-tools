# -*-coding:utf-8-*-
import pytest

from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.page_object import asset_magt
from Aops_Web_Auto_Test.utils.times import sleep
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage


class TestDeleteHost:

    @pytest.fixture(autouse=True)
    def host(self, drivers, add_host_group):
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        global host_ip
        host_ip = createtestdata.host_ip()
        host.add_host(host_name, 'local-cluster', add_host_group, host_ip, port, '监控节点', 'root', 'openEuler12#$')

    def test_delete_host_001_valid_data(self, drivers):
        """删除存在的主机"""
        host = AssetMagtPage(drivers)
        host.delete_host(host_ip)
        host.refresh()
        assert host_ip not in host.get_host_ip_from_table()


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_magt/test_delete_host.py','-s'])
