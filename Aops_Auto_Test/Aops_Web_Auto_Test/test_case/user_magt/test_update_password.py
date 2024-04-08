# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.times import sleep

psd = Element('user_magt')

class TestModifyUserPassword:

    def test_modify_user_password_01(self, drivers, create_user, logout):
        """修改登录密码-所有数据均正确"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.password, '123456', '123456')
        password.click_confirm_button()
        sleep(1)
        assert "修改成功" in password.get_notice_text()

    # def test_modify_user_password_02(self, drivers,login_aops, close_change_psd_page):
    #     """修改登录密码-当前密码错误"""
    #     password = UserMagtPage(drivers)
    #     password.user_password_modify("invalidpassword","123456","123456")
    #     password.click_confirm_button()
    #     assert password.element_text(psd["current_password_error_msg"]) is "password error"

    def test_modify_user_password_03(self, drivers, login_aops, close_change_psd_page):
        """修改登录密码-新密码长度小于5"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.password, '12345', '12345')
        password.click_confirm_button()
        assert password.element_text(psd["new_password_error_msg"]) == "请输入6-20位字母和数字组成的密码!"

    def test_modify_user_password_04(self, drivers,close_change_psd_page):
        """修改登录密码-新密码长度大于20"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.password, '123456789012345678901', '123456789012345678901')
        password.click_confirm_button()
        assert password.element_text(psd["new_password_error_msg"]) == "请输入6-20位字母和数字组成的密码!"

    def test_modify_user_password_05(self, drivers,close_change_psd_page):
        """修改登录密码-确认密码和新密码不一致"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.password, '123456', '1234567')
        password.click_confirm_button()
        sleep(2)
        assert password.element_text(psd["confirm_password_error_msg"]) == "确认密码和新密码必须保持一致!"

    def test_modify_user_password_06(self, drivers):
        """修改登录密码-取消修改密码"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.password, '123456789012345678901', '123456789012345678901')
        password.click_cancel_button()
        sleep(2)
        assert "display: none" in password.get_element_attr(psd['modify_password_page'], 'style')

if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/user_password_test.py'])
