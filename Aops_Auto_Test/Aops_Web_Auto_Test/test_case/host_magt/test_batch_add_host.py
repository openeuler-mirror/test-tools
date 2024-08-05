# -*-coding:utf-8-*-
import pytest

from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.utils.times import sleep
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage


class TestBatchAddHost:

    @pytest.fixture(autouse=True)
    def delete_host(self, drivers):
        host = AssetMagtPage(drivers)
        yield
        excel = host.get_host_ip_from_excel("template.csv")
        for host_ip in excel:
            sleep(10)
            host.delete_host(host_ip)

    def test_batch_add_host_01_valid_data(self, drivers):
        """批量添加有效主机"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host.batch_add_host("local-cluster", "template.csv")
        sleep(2)
        excel = host.get_host_ip_from_excel("template.csv")
        table_value = host.get_host_ip_from_table()
        for item in excel:
            assert item in table_value


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_magt/test_batch_add_host.py','-s'])
