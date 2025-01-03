# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage


class TestBatchAddHost:

    @pytest.fixture(scope='class', autouse=True)
    def setup_and_teardown(self, drivers):
        """添加主机组"""
        host = AssetMagtPage(drivers)
        host.enter_host_group_magt_page()
        host.add_host_group('local-cluster', 'batch_group', 'group description')
        yield
        excel = host.get_host_ip_from_excel("template.csv")
        for host_ip in excel:
            host.refresh()
            host.delete_host(host_ip)
        host.enter_host_group_magt_page()
        host.delete_host_group('batch_group')

    def test_batch_add_host_01_valid_data(self, drivers):
        """批量添加有效主机"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host.batch_add_host("local-cluster", "template.csv")
        excel = host.get_host_ip_from_excel("template.csv")
        host.refresh()
        table_value = host.get_host_ip_from_table()
        for item in excel:
            assert item in table_value


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_magt/test_batch_add_host.py','-s'])
