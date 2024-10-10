# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.utils.times import sleep
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.LogUtil import my_log
log = my_log()


class TestLogout:

    def test_logout(self, drivers, open_aops):
        login = UserMagtPage(drivers)
        login.user_login(ini.user, ini.password)
        sleep(5)
        assert ini.user in login.get_source, '登录失败'
        login.user_logout(ini.user)
        assert "登 录" in login.get_source, '退出系统失败'






if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/test_logout.py','-s'])
