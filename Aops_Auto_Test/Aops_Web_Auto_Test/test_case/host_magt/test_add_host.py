# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.utils.times import sleep
from Aops_Web_Auto_Test.common import createtestdata
class TestAddHost:

    def test_add_host_01_valid_data(self, drivers, add_host_group):
        """所有信息正确，添加有效的主机"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        host_ip = createtestdata.host_ip()
        host.add_host(host_name, 'local-cluster', add_host_group, host_ip, port, '监控节点', 'root','openEuler12#$')
        sleep(10)
        input_host_info = ['local-cluster', add_host_group]
        for i in input_host_info:
            assert i in host.get_host_info_from_table(host_ip)


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_magt/test_add_host.py','-s'])
