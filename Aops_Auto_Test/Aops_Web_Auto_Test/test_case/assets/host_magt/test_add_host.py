# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.common import createtestdata


class TestAddHost:
    @pytest.fixture(scope='class', autouse=True)
    def add_host_group(self, drivers):
        """添加主机组"""
        host = AssetMagtPage(drivers)
        host.enter_host_group_magt_page()
        global host_group
        host_group = createtestdata.group()
        host.add_host_group('local-cluster', host_group, 'group description')
        yield host_group

    def test_add_host_01_valid_data(self, drivers):
        """所有信息正确，添加有效的主机"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        host_ip = createtestdata.host_ip()
        host.add_host(host_name, 'local-cluster', host_group, host_ip, port, '监控节点', 'root','openEuler12#$')
        input_host_info = ['local-cluster', host_group]
        assert any(value in host.get_host_info_from_table(host_ip) for value in input_host_info)

    def test_add_host_02_duplicate_ip(self, drivers):
        """重复的主机ip"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        host_ip = createtestdata.host_ip()
        host.add_host(host_name, 'local-cluster', host_group, host_ip, port, '监控节点', 'root','openEuler12#$')
        input_host_info = ['local-cluster', host_group]
        assert any(value in host.get_host_info_from_table(host_ip) for value in input_host_info), "主机添加失败"
        host.add_host(host_name, 'local-cluster', host_group, host_ip, port, '监控节点', 'root','openEuler12#$')
        assert "Data.Exist" in host.get_top_right_notice_text()

    def test_add_host_03_error_ip(self, drivers):
        """主机ip格式错误"""
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        host_name = createtestdata.host_name()
        port = createtestdata.host_port()
        host.add_host(host_name, 'local-cluster', host_group, '255.255.255.256', port, '监控节点', 'root','openEuler12#$')
        assert host.item_explain_error_info("IP地址") == "请输入IP地址在 0.0.0.0~255.255.255.255 区间内"


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_magt/test_add_host.py', '-s'])
