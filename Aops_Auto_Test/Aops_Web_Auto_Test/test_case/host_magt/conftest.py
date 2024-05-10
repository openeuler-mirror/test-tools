import pytest

from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object import asset_magt
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.times import sleep

login = Element('user_magt')
asset = Element('host_magt')


@pytest.fixture(scope='class', autouse=True)
def user_login(drivers):
    """用户登录"""
    try:
        user = UserMagtPage(drivers)
        user.get_url(ini.url)
        user.input_text(login['username'], 'admin')
        user.input_text(login['password'], 'changeme')
        user.click_element(login['login'])
        sleep(5)
        assert 'admin' in user.get_source
    except Exception as e:
        print('登录失败')


@pytest.fixture(scope='function', autouse=False)
def add_host(drivers):
    """添加单个主机"""
    host = AssetMagtPage(drivers)
    host.enter_host_magt_page()
    host.add_host('host', asset_magt.global_groupname, '1.1.1.1', 22, '监控节点', 'root', 'openEuler12#$')

@pytest.fixture(scope='function', autouse=False)
def add_host_group(drivers):
    """添加主机组"""
    host = AssetMagtPage(drivers)
    host.enter_host_group_magt_page()
    host.add_host_group('group', 'group description')
    assert asset_magt.global_groupname in host.find_element(asset['host_group_list'])


@pytest.fixture(scope='function', autouse=False)
def batch_add_host_group(drivers):
    """批量添加主机组"""
    group_list = []
    host = AssetMagtPage(drivers)
    host.enter_host_group_magt_page()
    for i in range(5):
        host.add_host_group('group', 'group description')
        assert asset_magt.global_groupname in host.find_element(asset['host_group_list'])
        group_list.append(asset_magt.global_groupname)
    return group_list



