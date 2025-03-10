# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.user_magt import UserMagtPage
from Aops_Web_Auto_Test.utils.times import sleep

psd = Element('user_magt')


@pytest.mark.skip(reason="修改用户密码功能存在bug")
class TestModifyUserPassword:

    def test_modify_user_password_01(self, drivers, register_user, logout):
        """修改登录密码-所有数据均正确"""
        password = UserMagtPage(drivers)
        password.user_login(register_user[0], register_user[1])
        password.user_password_modify(register_user[0], register_user[1], '1234567', '1234567')
        password.click_confirm_button()
        assert "成功" in password.get_notice_text()

    def test_modify_user_password_02(self, drivers, login_aops, close_change_psd_page):
        """修改登录密码-当前密码错误"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.user, "invalidpassword", "123456", "123456")
        password.click_confirm_button()
        assert password.element_text(psd["notification_content"]) == "password error"

    def test_modify_user_password_03(self, drivers, login_aops, close_change_psd_page):
        """修改登录密码-新密码长度小于5"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.user, ini.password, '12345', '12345')
        password.click_confirm_button()
        assert password.element_text(psd["new_password_error_msg"]) == "请输入6-20位字母或数字组成的密码!"

    def test_modify_user_password_04(self, drivers,login_aops, close_change_psd_page):
        """修改登录密码-新密码长度大于20"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.user, ini.password, '123456789012345678901', '123456789012345678901')
        password.click_confirm_button()
        assert password.element_text(psd["new_password_error_msg"]) == "请输入6-20位字母或数字组成的密码!"

    def test_modify_user_password_05(self, drivers, login_aops, close_change_psd_page):
        """修改登录密码-确认密码和新密码不一致"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.user, ini.password, '123456', '1234567')
        password.click_confirm_button()
        assert password.element_text(psd["confirm_password_error_msg"]) == "请确保前后两次输入的密码保持一致！"

    def test_modify_user_password_06(self, drivers, login_aops):
        """修改登录密码-取消修改密码"""
        password = UserMagtPage(drivers)
        password.user_password_modify(ini.user, ini.password, '1234567890123456789', '1234567890123456789')
        password.click_cancel_button()
        sleep(1)
        assert not password.element_displayed(psd["modify_psd_page_title"])


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/user_magt/test_update_password.py'])
