# -*-coding:utf-8-*-
import logging

from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *

user = Element('user_magt')


class UserMagtPage(WebPage):

    def user_login(self, username, password):
        """用户登录"""
        sleep(2)
        try:
            self.input_text(user['username'], username)
            self.input_text(user['password'], password)
            self.click_element(user['login'])
        except Exception as e:
            print('登录失败： ',e)

    def user_logout(self, username):
        """退出登录"""
        self.new_user = self.replace_locator_text(user['user'], username)
        sleep(2)
        self.click_element(self.new_user)
        self.click_element(user['logout'])
        self.find_element(user['info_windows'])
        self.click_confirm_button()

    def user_register(self, username, password, confirm_password, email):
        """注册用户"""
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

    def user_password_modify(self, username, current_password, new_password, confirm_password):
        """修改用户密码"""
        self.new_user = self.replace_locator_text(user['user'], username)
        sleep(10)
        self.click_element(self.new_user)
        self.click_element(user['modify_password'])
        self.input_text(user['current_password'], current_password)
        self.input_text(user['new_password'], new_password)
        self.input_text(user['confirm_password'], confirm_password)

    # def click_confirm_button(self):
    #     self.click_element(base_page['confirm'])
    #     self.log.info("点击确定按钮： {}".format(base_page['confirm']))

    def close_welcome_tips(self):
        """关闭提醒窗口"""
        self.click_element(user['notice_close'])

    def get_notification_text(self):
        text = self.element_text(user['notification_content'])
        logging.info("获取notice的文本：{}".format(text))
        return text


