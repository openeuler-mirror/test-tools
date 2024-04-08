import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.times import sleep

login = Element('common')


@pytest.fixture(scope='class', autouse=True)
def open_aops(drivers):
    """访问A-Ops网址"""
    user = UserMagtPage(drivers)
    user.get_url(ini.url)


@pytest.fixture(scope='class', autouse=False)
def register_user(drivers):
    """注册用户"""
    user = UserMagtPage(drivers)
    user.user_register('test', '123456', '123456', 'test@163.com')
    assert '欢迎来到A-Ops系统' in user.get_source


@pytest.fixture(scope='function', autouse=False)
def login_aops(drivers):
    """登录"""
    user = UserMagtPage(drivers)
    user.user_login(ini.user, ini.password)
    sleep(5)
    assert ini.user in user.get_source


@pytest.fixture(scope='function', autouse=False)
def logout(drivers):
    yield
    sleep(5)
    user = UserMagtPage(drivers)
    user.user_logout()


@pytest.fixture(scope='class', autouse=False)
def create_user(drivers):
    """注册用户"""
    user = UserMagtPage(drivers)
    user.user_register('test', ini.password, ini.password, 'test@163.com')
    assert '欢迎来到A-Ops系统' in user.get_source
    user.user_login(user.globals_username, ini.password)
    sleep(5)
    assert user.globals_username in user.get_source

@pytest.fixture(scope='function', autouse=False)
def close_change_psd_page(drivers):
    """关闭修改用户密码页面"""
    yield
    user = UserMagtPage(drivers)
    user.click_element(login["cancel"])



