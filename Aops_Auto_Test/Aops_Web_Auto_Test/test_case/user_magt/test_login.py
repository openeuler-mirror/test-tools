# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage


class TestLogin:

    def test_login_01_valid_data(self, drivers, default_logout):
        login = UserMagtPage(drivers)
        login.user_login(ini.user, ini.password)
        assert login.get_user_element(ini.user)

    def test_login_02_invalid_username(self, drivers, reload_page):
        login = UserMagtPage(drivers)
        login.user_login("invaliduser", ini.password)
        assert "incorrect username or password" in login.get_notification_text()

    def test_login_03_invalid_password(self, drivers, reload_page):
        login = UserMagtPage(drivers)
        login.user_login(ini.user, "invalidpassword")
        assert "password error" in login.get_notification_text()

    def test_login_04_invalid_user_password(self, drivers, reload_page):
        login = UserMagtPage(drivers)
        login.user_login("invaliduser", "invalidpassword")
        assert "incorrect username or password" in login.get_notification_text()


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/login_test.py','-s'])
