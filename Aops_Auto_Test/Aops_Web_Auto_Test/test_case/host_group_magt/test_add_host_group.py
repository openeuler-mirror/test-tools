# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object import asset_magt
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage

asset = Element('asset_magt')


class TestAddHostGroup:
    def test_add_host_group_001(self, drivers):
        """所有信息正确，添加有效的主机组"""
        host_group = AssetMagtPage(drivers)
        host_group.enter_host_group_magt_page()
        host_group.add_host_group('group','group description')
        assert asset_magt.global_groupname in host_group.find_element(asset['host_group_list'])

    def test_add_host_group_002(self, drivers):
        """添加无效的主机组"""
        host_group = AssetMagtPage(drivers)
        host_group.enter_host_group_magt_page()
        host_group.add_host_group('q！@#￥%……&*（）','group description')
        assert "名称应由数字、小写字母、英文下划线组成" in host_group.get_source
        host_group.add_host_group('!@^%asd','group description')
        assert "以小写字母开头，且结尾不能是英文下划线" in host_group.get_source
        host_group.add_host_group('group_','group description')
        assert "以小写字母开头，且结尾不能是英文下划线" in host_group.get_source


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/login_test.py','-s'])
