import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.utils.times import sleep

login = Element('common')


@pytest.fixture(scope='module', autouse=True)
def login_aops(drivers):
    """登录"""
    user = UserMagtPage(drivers)
    user.get_url(ini.url)
    user.user_login(ini.user, ini.password)
    sleep(5)
    assert ini.user in user.get_source


@pytest.fixture(scope='function', autouse=False)
def logout(drivers):
    yield
    sleep(5)
    user = UserMagtPage(drivers)
    user.user_logout()




