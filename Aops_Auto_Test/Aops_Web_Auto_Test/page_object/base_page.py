# -*-coding:utf-8-*-

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.utils.times import *
from Aops_Web_Auto_Test.utils.LogUtil import my_log


base_page = Element('common')
driver = None

class WebPage(object):
    """selenium基类"""

    def __init__(self,driver):
        self.driver = driver
        self.log = my_log()
        self.timeout = 20
        self.wait = WebDriverWait(self.driver, self.timeout)

    def get_url(self, url):
        """打开网址并验证"""
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(60)
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            self.log.info("打开网页：%s" % url)
        except TimeoutException:
            raise TimeoutException("打开%s失败" % url)

    @staticmethod
    def element_locator(func, locator):
        """元素定位器"""
        name, value = locator
        return func(cm.LOCATE_MODE[name], value)

    @staticmethod
    def replace_locator_text(locator,value):
        """替换元素值"""
        lst = list(locator)
        lst[1] = lst[1].replace('****',value)
        locator = tuple(lst)
        return locator

    def find_element(self, locator):
        """寻找单个元素"""
        try:
            return WebPage.element_locator(lambda *args: self.wait.until(
                EC.presence_of_element_located(args)), locator)
        except TimeoutException as e:
            self.log.error('元素未找到：',locator)

    def find_elements(self, locator):
        """查找多个相同的元素"""
        return WebPage.element_locator(lambda *args: self.wait.until(
            EC.presence_of_all_elements_located(args)), locator)

    def elements_num(self, locator):
        """获取相同元素的个数"""
        number = len(self.find_elements(locator))
        self.log.info("相同元素：{}".format((locator, number)))
        return number

    def input_text(self, locator, txt):
        """输入(输入前先清空)"""
        ele = self.find_element(locator)
        ele.clear()
        ele.send_keys(txt)
        self.log.info("输入文本：{}".format(txt))
    def click_element(self, locator):
        """点击"""
        self.find_element(locator).click()
        self.log.info("点击元素：{}".format(locator))

    def click_element_by_javascripts(self, locator):
        """通过java_scripts点击元素"""
        ele = self.find_element(locator)
        self.driver.execute_script("arguments[0].click();", ele)
        sleep()
        self.log.info("点击元素：{}".format(locator))

    def element_text(self, locator):
        """获取元素text"""
        _text = self.find_element(locator).text
        self.log.info("获取文本：{}".format(_text))
        return _text

    def get_notice_text(self):
        """获取当前notice的text"""
        _text = self.element_text(base_page['notice'])
        self.log.info("获取notice的文本：{}".format(_text))
        return _text

    @property
    def get_source(self):
        """获取页面源代码"""
        return self.driver.page_source

    def refresh(self):
        """刷新页面F5"""
        self.driver.refresh()
        self.driver.implicitly_wait(30)

    def select_value_by_dropdown(self, value):
        """从下拉框选择值"""
        self.click_element(base_page['host_group_dropdownbar'])
        new_locator = self.replace_locator_text(base_page['list_box_value'], value)
        self.click_element(new_locator)

    def select_value_by_radio_button(self, value):
        """选择单选按钮"""
        new_locator = self.replace_locator_text(base_page['redio_button'], value)
        self.click_element(new_locator)

    def upload_file(self, file_name):
        """上传文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        self.input_text(base_page['select_file_button'],file_path)
        self.log.info("上传文件：{}".format(file_path))

    def get_element_attr(self, locator, attr):
        """获取元素属性值"""
        return self.find_element(locator).get_attribute(attr)

    def click_cancel_button(self):
        """点击取消按钮"""
        self.click_element(base_page['cancel'])

    def click_delete_button(self):
        """点击删除按钮"""
        self.click_element(base_page['delete'])

    def click_refresh_button(self):
        self.click_element(base_page['refresh'])

    def click_confirm_button(self):
        self.click_element(base_page['confirm'])
        self.log.info("点击确定按钮： {}".format(base_page['confirm']))

    def select_checkbox_from_table(self, value):
        new_loc = self.replace_locator_text(base_page['table_list_checkbox_column'], value)
        self.click_element(new_loc)

    def batch_delete_data(self, value_list):
        """批量删除数据"""
        for value in value_list:
            self.select_checkbox_from_table(value)
        self.click_element(base_page['batch_delete'])
        self.click_element(base_page['delete_confirm'])



