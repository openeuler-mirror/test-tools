import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage

login = Element('common')


@pytest.fixture(scope='module', autouse=True)
def login_aops(drivers):
    """登录"""
    user = UserMagtPage(drivers)
    user.get_url(ini.url)
    user.user_login(ini.user, ini.password)
    assert ini.user in user.get_source





