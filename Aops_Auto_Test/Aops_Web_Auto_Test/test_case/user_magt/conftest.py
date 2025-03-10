import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage

login = Element('common')


@pytest.fixture(scope='module', autouse=True)
def open_aops(drivers):
    """访问A-Ops网址"""
    user = UserMagtPage(drivers)
    user.get_url(ini.url)


@pytest.fixture(scope='class', autouse=False)
def register_user(drivers):
    """注册用户"""
    user = UserMagtPage(drivers)
    return user.user_register('test', '123456', '123456', 'test@163.com')


@pytest.fixture(scope='function', autouse=False)
def login_aops(drivers):
    """登录"""
    user = UserMagtPage(drivers)
    user.user_login(ini.user, ini.password)
    assert user.get_user_element(ini.user)


@pytest.fixture(scope='function', autouse=False)
def logout(drivers,register_user):
    user = UserMagtPage(drivers)
    username = register_user[0]
    yield username
    user.user_logout(username)



@pytest.fixture(scope='function', autouse=False)
def default_logout(drivers):
    user = UserMagtPage(drivers)
    yield
    user.user_logout(ini.user)



@pytest.fixture(scope='function', autouse=False)
def close_change_psd_page(drivers):
    """关闭修改用户密码页面"""
    yield
    user = UserMagtPage(drivers)
    user.click_element(login["cancel"])


@pytest.fixture(scope='function', autouse=False)
def reload_page(drivers):
    """刷新页面"""
    yield
    user = UserMagtPage(drivers)
    user.refresh()



