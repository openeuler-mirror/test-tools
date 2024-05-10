# -*-coding:utf-8-*-
import pytest

from Aops_Web_Auto_Test.page_object import asset_magt
from Aops_Web_Auto_Test.utils.times import sleep
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage


class TestHostList:

    def test_add_host_001(self, drivers):
        """所有信息正确，添加有效的主机"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host.add_host('host','group1','1.1.1.1',22, '监控节点','root','openEuler12#$')
        input_host_info = [asset_magt.global_hostname, 'group1', '1.1.1.1']
        for i in input_host_info:
            assert i in host.get_host_info_from_table()




if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/login_test.py','-s'])
