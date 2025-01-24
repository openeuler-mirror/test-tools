"""
@Time : 2024/10/28 10:00
@Auth : ysc
@File : base_page.py
@IDE  : PyCharm
"""
import time

from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as WD

from config.config import LOCATE_MODE
from common.log import log


class BasePage(object):
    """结合显示等待封装一些selenium内置方法"""

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WD(self.driver, timeout, 0.1)
        self.action = ActionChains(self.driver)

    @staticmethod
    def element_locator(func, locator):
        """
        元素定位器
        """
        name, value = locator
        return func(LOCATE_MODE[name], value)

    def get_incognito_driver(self):
        """
        加载驱动
        设置无痕模式
        :return: driver
        """
        option = webdriver.ChromeOptions()
        option.add_argument('no-sandbox')
        option.add_argument("--incognito")
        self.driver = webdriver.Chrome(options=option)
        self.driver.maximize_window()

    def find_element(self, locator):
        """
        获取单个元素
        """
        try:
            ele = BasePage.element_locator(lambda *args: self.wait.until(
                EC.presence_of_element_located(args)), locator)
            return ele
        except TimeoutException as e:
            log.error('found "{}" timeout!'.format(locator), e)

    def find_elements(self, locator):
        """
        获取多个元素
        """
        try:
            elements = BasePage.element_locator(lambda *args: self.wait.until(
                EC.presence_of_all_elements_located(args)), locator)
            return elements
        except Exception as e:
            log.error('found "{}" timeout!'.format(locator), e)

    def is_element_exist(self, timeout, locator):
        """
        判断元素是否可见
        """
        try:
            BasePage.element_locator(lambda *args: WD(self.driver, timeout).until(
                EC.presence_of_element_located(args)), locator)
        except TimeoutException:
            log.info('Error: element "{}" not exist'.format(locator))
            return False
        return True

    def is_click(self, locator):
        """
        判断元素是否可见并且是enable的
        """
        try:
            ele = BasePage.element_locator(lambda *args: self.wait.until(
                EC.element_to_be_clickable(args)), locator)
            return ele
        except TimeoutException as e:
            log.error("元素不可以点击", e)

    def get_element_text(self, locator, name=None):
        """
        获取input输入框的输入内容、元素的属性值或者text信息
        """
        try:
            element = self.find_element(locator)
            if name:
                return element.get_attribute(name)
            else:
                return element.text
        except AttributeError:
            log.error('get "{}" text failed return None'.format(locator))

    def load_url(self, url):
        """
        加载url
        """
        log.info('string upload url "{}"'.format(url))
        self.driver.maximize_window()
        self.driver.get(url)
        self.driver.implicitly_wait(10)

    def send_keys(self, locator, value=''):
        """
        写数据
        """
        log.info('input "{}"'.format(value))
        try:
            element = self.find_element(locator)
            element.send_keys(value)
        except AttributeError as e:
            log.error(e)

    def clear(self, locator):
        """
        清理input输入框内容
        """
        log.info('clearing data')
        try:
            element = self.find_element(locator)
            element.clear()
        except AttributeError as e:
            log.error(e)

    def click(self, locator):
        """
        点击某个元素
        """
        log.info('click "{}"'.format(locator))
        element = self.is_click(locator)
        if element:
            element.click()
        else:
            log.info('the "{}" unclickable!'.format(locator))

    def click_element_by_js(self, locator):
        log.info('click element "{}'.format(locator))
        ele = self.find_element(locator)
        self.driver.execute_script("arguments[0].click()", ele)

    def mouse_move(self, locator):
        """
        鼠标悬停
        """
        log.info('mouse_move "{}"'.format(locator))
        try:
            element = self.find_element(locator)
            self.action.move_to_element(element).perform()
        except Exception as e:
            log.error(e)

    @staticmethod
    def sleep(num=0):
        """
        强制等待
        """
        time.sleep(num)

    def refresh(self):
        """刷新页面F5"""
        self.driver.refresh()
        self.driver.implicitly_wait(30)


if __name__ == "__main__":
    pass
