# -*-coding:utf-8-*-
from selenium.common import TimeoutException
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *

user = Element('user_magt')


class UserMagtPage(WebPage):

    def login_page(self):
        """
        登录页面
        Returns:

        """
        return self.element_displayed(user['login'])

    def user_login(self, username, password):
        """
        用户登录
        Args:
            username:
            password:

        Returns:

        """
        try:
            self.login_page()
            self.input_text(user['username'], username)
            self.input_text(user['password'], password)
            self.click_element(user['login'])
        except Exception as e:
            print('登录失败： ', e)

    def user_logout(self, username):
        """
        Logout
        Args:
            username:

        Returns:

        """
        try:
            self.login_page()
            self.refresh()
            new_user = self.replace_locator_text(user['user'], username)
            self.click_element(new_user)
            self.click_element(user['logout'])
            self.find_element(user['info_windows'])
            self.click_confirm_button()
        except Exception as e:
            print(f"退出系统失败了！{e}")

    def user_register(self, username, password, confirm_password, email):
        """
        Register user
        Args:
            username:
            password:
            confirm_password:
            email:

        Returns:

        """
        try:
            self.click_element_by_javascripts(user['register_now'])
        except:
            self.get_url(ini.url)
            self.click_element_by_javascripts(user['register_now'])
        self.globals_username = username + str(dt_strftime('%H%M%S'))
        self.input_text(user['register_username'], self.globals_username)
        self.input_text(user['register_password'], password)
        self.input_text(user['register_confirm_password'], confirm_password)
        self.input_text(user['register_email'], email)
        self.click_element(user['register'])
        return self.globals_username, password

    def get_user_element(self, username):
        """
        Get user name from board
        Args:
            username:

        Returns:

        """
        return self.replace_locator_text(user['user'], username)

    def user_password_modify(self, username, current_password, new_password, confirm_password):
        """
        Modify user password
        Args:
            username:
            current_password:
            new_password:
            confirm_password:

        Returns:

        """
        """修改用户密码"""
        new_user = self.replace_locator_text(user['user'], username)
        self.click_element(new_user)
        self.click_element(user['modify_password'])
        self.input_text(user['current_password'], current_password)
        self.input_text(user['new_password'], new_password)
        self.input_text(user['confirm_password'], confirm_password)

    def close_welcome_tips(self):
        """关闭提醒窗口"""
        self.click_element(user['notice_close'])

    def get_notification_text(self):
        try:
            return self.element_text(user['notification_content'])
        except TimeoutException as e:
            print("获取文本超时： ", e)

    def get_username_error_message(self):
        """
        注册用户页面，获取用户字段的错误信息
        Returns:

        """
        return self.element_text(user['username_error_message'])

    def get_psd_error_message(self):
        """
        注册用户页面，获取密码的错误信息
        Returns:

        """
        return self.element_text(user['psd_error_message'])

    def get_confirm_psd_error_message(self):
        """
        注册用户页面，获取确认密码的错误信息
        Returns:

        """
        return self.element_text(user['confirm_psd_error_message'])

    def get_email_error_message(self):
        """
        注册用户页面，获取邮箱的错误信息
        Returns:

        """
        return self.element_text(user['email_error_message'])



