# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.utils.times import sleep
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.LogUtil import my_log
log = my_log()


class TestLogin:

    def test_login_01_valid_data(self, drivers, open_aops, logout):
        login = UserMagtPage(drivers)
        login.user_login(ini.user, ini.password)
        sleep(2)
        assert ini.user in login.get_source

    def test_login_02_invalid_username(self, drivers):
        login = UserMagtPage(drivers)
        login.user_login("invaliduser", ini.password)
        sleep(2)
        assert "incorrect username or password" in login.get_notification_text()

    def test_login_03_invalid_password(self, drivers):
        login = UserMagtPage(drivers)
        login.user_login(ini.user, "invalidpassword")
        sleep(2)
        assert "incorrect username or password" in login.get_notification_text()

    def test_login_04_invalid_password(self, drivers):
        login = UserMagtPage(drivers)
        login.user_login("invaliduser", "invalidpassword")
        sleep(2)
        assert "incorrect username or password" in login.get_notification_text()




if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/login_test.py','-s'])
