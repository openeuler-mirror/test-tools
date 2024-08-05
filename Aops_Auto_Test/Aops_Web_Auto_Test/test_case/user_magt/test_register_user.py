# -*-coding:utf-8-*-
import time

import pytest
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage


class TestRegister:

    def test_register_user_01_valid_data(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test","123456", "123456","test@163.com")
        time.sleep(2)
        assert "登 录" in register.get_source

    def test_register_user_02_invalid_user(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test2%^&*","123456", "123456","test@163.com")
        assert "请输入5-20位字母或数字组成的用户名!" in register.get_source

    def test_register_user_03_invalid_psd(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test","!@#$%^&*()", "!@#$%^&*()","test@163.com")
        assert "请输入6-20位字母或数字组成的密码!" in register.get_source

    def test_register_user_04_invalid_email(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test","123456", "123456","123456")
        assert "请输入正确的邮箱格式!" in register.get_source

    def test_register_user_05_miss_match_psd(self, drivers):
        register = UserMagtPage(drivers)
        register.user_register("test","123456", "1234567","123456@163.com")
        assert "请确保前后两次输入的密码保持一致！" in register.get_source

if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/test_register_user.py', '-s'])
