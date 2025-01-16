# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.LogUtil import my_log
user = Element('user_magt')


class TestLogout:

    def test_logout(self, drivers, open_aops):
        logout = UserMagtPage(drivers)
        logout.user_login(ini.user, ini.password)
        assert logout.get_user_element(ini.user), '登录失败！'
        logout.user_logout(ini.user)
        assert logout.login_page(), '退出系统失败！'


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/test_logout.py','-s'])
