import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage

login = Element('user_magt')


@pytest.fixture(scope='module', autouse=True)
def user_login_logout(drivers):
    """用户登录"""
    user = UserMagtPage(drivers)
    user.get_url(ini.url)
    user.user_login(ini.user, ini.password)
    yield
    user.user_logout(ini.user)


@pytest.fixture(scope='function', autouse=True)
def refresh_page(drivers):
    """刷新页面"""
    user = UserMagtPage(drivers)
    yield
    user.refresh()









