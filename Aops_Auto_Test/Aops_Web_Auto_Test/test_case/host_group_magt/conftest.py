import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.times import sleep

login = Element('common')


@pytest.fixture(scope='module', autouse=True)
def user_login(drivers):
    """用户登录"""
    user = UserMagtPage(drivers)
    user.get_url(ini.url)
    user.user_login(ini.user, ini.password)
    user.close_right_notice()

@pytest.fixture(scope='module')
def create_data(drivers):
    """准备测试数据"""
    user = UserMagtPage(drivers)
    user.get_url(ini.url)
    user.user_login(ini.user, ini.password)
    group = AssetMagtPage(drivers)
    group.enter_host_group_magt_page()
    group_list = []
    for i in range(3):
        group.add_host_group("pre_group","pre_desc")
        group_list.append(group.global_groupname)
    group.enter_host_magt_page()
    group.add_host('pre_host', group_list[-1], '172.168.2.2',22, '监控节点','root','openEuler12#$')
    yield group_list



