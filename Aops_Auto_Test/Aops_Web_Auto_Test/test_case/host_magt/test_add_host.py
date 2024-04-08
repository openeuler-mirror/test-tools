# -*-coding:utf-8-*-
import pytest

from Aops_Web_Auto_Test.page_object import asset_magt
from Aops_Web_Auto_Test.utils.times import sleep
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage


class TestAddHost:

    def test_add_host_001(self, drivers):
        """所有信息正确，添加有效的主机"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host.add_host('host','group1','1.1.1.1',22, '监控节点','root','openEuler12#$')
        input_host_info = [asset_magt.global_hostname, 'group1', '1.1.1.1']
        for i in input_host_info:
            assert i in host.get_host_info_from_table()

    def test_batch_add_host_001(self, drivers):
        """批量添加有效主机"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host.batch_add_host("add_host.xlsx")
        sleep(2)
        excel = host.get_host_name_from_excel("add_host.xlsx")
        table_value = host.get_host_name_from_table()
        for item in excel:
            assert item in table_value

    def test_delete_single_host_001(self, add_host, drivers):
        """删除未加入工作流的主机"""
        host = AssetMagtPage(drivers)
        host.delete_host(asset_magt.global_hostname)
        sleep(2)
        assert asset_magt.global_hostname not in host.get_source

    def test_batch_delete_host_001(self,drivers):
        """批量删除未加入工作流的主机"""
        host = AssetMagtPage(drivers)
        host.batch_delete_host("add_host.xlsx")
        host.click_cancel_button()
        excel = host.get_host_name_from_excel("add_host.xlsx")
        table_value = host.get_host_name_from_table()
        for item in excel:
            assert item in table_value
        host.click_refresh_button()
        host.batch_delete_host("add_host.xlsx")
        host.click_delete_button()
        excel = host.get_host_name_from_excel("add_host.xlsx")
        table_value = host.get_host_name_from_table()
        for item in excel:
            assert item not in table_value


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/login_test.py','-s'])
