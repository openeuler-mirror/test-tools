import pytest
from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.times import sleep

login = Element('user_magt')


@pytest.fixture(scope='module', autouse=True)
def user_login(drivers):
    """用户登录"""
    user = UserMagtPage(drivers)
    user.get_url(ini.url)
    sleep(5)
    user.user_login(ini.user, ini.password)


@pytest.fixture(scope='class', autouse=False)
def add_host_group(drivers):
    """添加主机组"""
    host = AssetMagtPage(drivers)
    host.enter_host_group_magt_page()
    host_group = createtestdata.group()
    return host.add_host_group('local-cluster', host_group, 'group description')





