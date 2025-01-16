# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage


class TestRegister:

    def test_register_user_01_valid_data(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test","123456", "123456","test@163.com")
        assert register.login_page()

    def test_register_user_02_invalid_user(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test2%^&*","123456", "123456","test@163.com")
        assert register.get_username_error_message() == "请输入5-20位字母或数字组成的用户名!"

    def test_register_user_03_invalid_psd(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test", "!@#$%^&*()", "!@#$%^&*()", "test@163.com")
        assert register.get_psd_error_message() == "请输入6-20位字母或数字组成的密码!"

    def test_register_user_04_invalid_email(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test", "123456", "123456", "123456")
        assert register.get_email_error_message() == "请输入正确的邮箱格式!"

    def test_register_user_05_miss_match_psd(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test", "123456", "1234567", "123456@163.com")
        assert register.get_confirm_psd_error_message() == "请确保前后两次输入的密码保持一致！"


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/test_register_user.py', '-s'])
