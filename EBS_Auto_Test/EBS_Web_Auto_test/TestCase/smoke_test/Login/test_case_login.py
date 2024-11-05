# -*- coding: utf-8 -*-
"""
@Time ： 2023/9/22 0022 17:46
@Auth ： ysc
@File ：test_case_login.py
@IDE ：PyCharm
"""
import time
import unittest
from Page.login_page import LoginPage
from Lib.parseConFile import ReadConfig
from Config.config import CONF_PATH
from Lib.log import log
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginCase(unittest.TestCase):
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    @classmethod
    def setUpClass(cls) -> None:
        log.info("Start to config params of the case.")
        # 窗口最大化
        cls.driver.maximize_window()
        cls.config = ReadConfig(CONF_PATH)
        log.info("End to config params of the case.")

    @classmethod
    def tearDownClass(cls) -> None:
        log.info("Start to config params of the case.")
        cls.driver.quit()
        log.info("End to config params of the case.")

    def setUp(self) -> None:
        log.info("No params need to config.")

    def tearDown(self) -> None:
        time.sleep(5)
        log.info("No params need to config.")

    def test_01_login_success(self):
        """用户登录检查"""
        log.info('用户登录')
        login = LoginPage(self.driver)
        login.load_url(self.config.BASIC_URL)
        login.user_login()
        time.sleep(10)
        login.login_valid(self.config.NAME, self.config.PASSWORD)
        time.sleep(25)
        if self.assertEqual(self.driver.current_url, self.config.BASIC_URL) is None:
            log.info("跳转到登录页面，输入正确的用户名密码，登录成功!")
        else:
            log.info("跳转到登录页面，输入正确的用户名密码，登录失败")

    def test_02_image_build(self):
        """镜像定制按钮检查"""
        log.info('镜像定制按钮检查')
        login = LoginPage(self.driver)
        login.load_url(self.config.BASIC_URL)
        time.sleep(3)
        login.image_build()
        current_url = self.config.BASIC_URL + "images"
        WebDriverWait(self.driver, 30).until(EC.url_contains(current_url))
        if self.assertEqual(self.driver.current_url, self.config.BASIC_URL + "images") is None:
            log.info("查看镜像定制按钮成功")
        else:
            log.info("查看镜像定制按钮失败")

    def test_03_projects_build(self):
        """工程构建按钮检查"""
        log.info('镜像定制按钮检查')
        login = LoginPage(self.driver)
        login.load_url(self.config.BASIC_URL)
        time.sleep(3)
        login.projects_build()
        current_url = self.config.BASIC_URL + "projects"
        WebDriverWait(self.driver, 30).until(EC.url_contains(current_url))
        if self.assertEqual(self.driver.current_url, self.config.BASIC_URL + "projects", ) is None:
            log.info("查看工程构建查看按钮生效")
        else:
            log.info("查看工程构建查看按钮失败")

    def test_04_user_page(self):
        """用户空间页面检查"""
        log.info('用户空间页面检查')
        login = LoginPage(self.driver)
        login.load_url(self.config.BASIC_URL)
        time.sleep(3)
        login.user_selector()
        time.sleep(3)
        login.user_page()
        time.sleep(3)
        if self.assertEqual(self.driver.current_url, self.config.BASIC_URL + "space/created") is None:
            log.info("查看用户空间按钮生效")
        else:
            log.info("查看用户空间按钮失败")

    def test_05_user_logout(self):
        """用户注销按钮检查"""
        log.info('用户注销按钮检查')
        login = LoginPage(self.driver)
        login.load_url(self.config.BASIC_URL)
        time.sleep(3)
        login.user_selector()
        time.sleep(5)
        login.user_logout()
        WebDriverWait(self.driver, 30).until(EC.url_contains(self.config.BASIC_URL))
        if self.assertEqual(self.driver.current_url, self.config.BASIC_URL) is None:
            log.info("查看用户注销按钮不生效")
        else:
            log.info("查看用户注销按钮失败")

    def test_06_switch_language(self):
        """中英文切换检查"""
        log.info('中英文切换检查')
        login = LoginPage(self.driver)
        login.load_url(self.config.BASIC_URL)
        time.sleep(3)
        login.switch_language()
        time.sleep(2)
        login.switch_English()
        text_1 = login.alert_message()
        if self.assertEqual(text_1, "Switch Language Success") is None:
            log.info("语言栏切换英文成功")
        else:
            log.info("语言栏切换英文成功失败")

        time.sleep(3)
        login.switch_language()
        time.sleep(2)
        login.switch_Chinese()
        text_2 = login.alert_message()
        if self.assertEqual(text_2, "切换语言成功") is None:
            log.info("语言栏切换中文成功")
        else:
            log.info("语言栏切换中文失败")

if __name__ == '__main__':
    unittest.main()
