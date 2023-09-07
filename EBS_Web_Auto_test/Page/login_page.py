# -*- coding: utf-8 -*-
"""
@Time ： 2023/9/22 0022 14:49
@Auth ： ysc
@File ：login_page.py
@IDE ：PyCharm
"""

import time
from Page.base_page import BasePage
from Lib.readelement import Element
from Lib.log import log

user = Element('login')


class LoginPage(BasePage):
    """首页和登录页面元素"""
    usernameBy = None
    passwordBy = None
    submitBy = None
    permission = None

    def user_button(self):
        """
        用户登录按钮
        """
        try:
            self.click(user["login"][0], user["login"][1])
        except Exception as e:
            log.error("error: found user_button timeout")
            log.info(e)

    def user_login(self):
        """登录"""
        try:
            self.user_button()
            time.sleep(2)
            # 用户名输入框
            self.usernameBy = self.find_element(user["username"][0], user["username"][1])

            # 密码输入框
            self.passwordBy = self.find_element(user["password"][0], user["password"][1])
            # 协议选项
            self.permission = self.find_element(user["permission"][0], user["permission"][1])
            # 登录按钮
            self.submitBy = self.find_element(user["submit"][0], user["submit"][1])
        except Exception as e:
            log.error("error: found user_login timeout")
            log.info(e)

    def login_valid(self, username, password):
        """
        登录验证、输入相关用户名、密码
        """
        self.usernameBy.send_keys(username)
        self.passwordBy.send_keys(password)
        self.permission.click()
        self.submitBy.click()

    def user_selector(self):
        """
        用户登录成功后点击用户下拉框
        """
        try:
            self.click(user["user_list"][0], user["user_list"][1])
        except Exception as e:
            log.error("error: found user_selector timeout")
            log.info(e)

    def user_logout(self):
        """
        用户退出按钮
        """
        try:
            self.click(user["logout"][0], user["logout"][1])
        except Exception as e:
            log.error("error: found user_logout timeout")
            log.info(e)

    def user_page(self):
        """
        用户空间按钮
        """
        try:
            self.click(user["user_space"][0], user["user_space"][1])
        except Exception as e:
            log.error("error: found user_page timeout")
            log.info(e)

    def image_build(self):
        """
        镜像定制查看按钮
        """
        try:
            self.click(user["image_build"][0], user["image_build"][1])
        except Exception as e:
            log.error("error: found image_build timeout")
            log.info(e)

    def projects_build(self):
        """
        构建工程查看按钮
        """
        try:
            self.click(user["projects_build"][0], user["projects_build"][1])
        except Exception as e:
            log.error("error: found projects_build timeout")
            log.info(e)

    def switch_language(self):
        """
        语言栏选择界面
        """
        try:
            self.mouse_move(user["lang_list"][0], user["lang_list"][1])
        except Exception as e:
            log.error("error: found switch_language timeout")
            log.info(e)

    def alert_message(self):
        """
        获取弹窗元素
        """
        self.mouse_move(user["assert"][0], user["assert"][1])
        alert = self.find_element(user["assert"][0], user["assert"][1])

        return alert.text

    def switch_English(self):
        """
        切换英文
        """
        try:
            self.click(user["lang_en"][0], user["lang_en"][1])
        except Exception as e:
            log.error("error: found switch_English timeout")
            log.info(e)

    def switch_Chinese(self):
        """
        切换中文
        """
        try:
            self.click(user["lang_ch"][0], user["lang_ch"][1])
        except Exception as e:
            log.info("error: found switch_chinese timeout")
            log.info(e)
