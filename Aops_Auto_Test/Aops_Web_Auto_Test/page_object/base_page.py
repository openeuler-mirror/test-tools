# -*-coding:utf-8-*-

from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.utils.LogUtil import my_log
import pandas as pd



base_page = Element('common')
driver = None


class WebPage(object):
    """selenium基类"""

    def __init__(self, driver):
        self.driver = driver
        self.log= my_log()
        self.timeout = 10
        self.wait = WebDriverWait(self.driver, self.timeout, 0.1)

    def get_url(self, url):
        """打开网址并验证"""
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(60)
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            self.log.info("打开网页：%s" % url)
            # self.log.info("打开网页：%s" % url)
        except TimeoutException:
            raise TimeoutException("打开%s失败" % url)

    @staticmethod
    def element_locator(func, locator):
        """元素定位器"""
        name, value = locator
        return func(cm.LOCATE_MODE[name], value)

    @staticmethod
    def replace_locator_text(locator, value):
        """替换元素值"""
        lst = list(locator)
        lst[1] = lst[1].replace('****', value)
        locator = tuple(lst)
        return locator

    def find_element(self, locator):
        """寻找单个元素"""
        try:
            return WebPage.element_locator(lambda *args: self.wait.until(
                EC.presence_of_element_located(args)), locator)
        except TimeoutException:
            print(f"{locator} 元素未找到！")
            return None

    def element_clickable(self, locator):
        """元素可点击"""
        try:
            return WebPage.element_locator(lambda *args: self.wait.until(
                EC.element_to_be_clickable(args)), locator)
        except TimeoutException:
            print(f"{locator} 元素不可点击！")
            return None

    def find_elements(self, locator):
        """查找多个相同的元素"""
        return WebPage.element_locator(lambda *args: self.wait.until(
            EC.presence_of_all_elements_located(args)), locator)

    def element_displayed(self, locator):
        """元素可见"""
        try:
            return WebPage.element_locator(lambda *args: self.wait.until(
                EC.visibility_of_element_located(args)), locator)
        except TimeoutException:
            print(f"等待{locator} 元素变为可见超时")
            return None

    def element_invisibility(self, locator):
        """元素不可见"""
        try:
            return WebPage.element_locator(lambda *args: self.wait.until(
                EC.invisibility_of_element_located(args)), locator)
        except TimeoutException:
            print(f"等待{locator} 元素变为不可见超时")
            return None

    def elements_num(self, locator):
        """获取相同元素的个数"""
        number = len(self.find_elements(locator))
        self.log.info("相同元素：{}".format((locator, number)))
        return number

    def input_text(self, locator, txt):
        """输入(输入前先清空)"""
        ele = self.find_element(locator)
        #ele.clear()
        ele.send_keys(txt)
        self.log.info("在{}中输入文本：{}".format(locator, txt))

    def click_element(self, locator):
        """点击元素"""

        try:
            element = self.find_element(locator)
            element.click()
            return True
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            pass

        try:
            element = self.element_clickable(locator)
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            pass

        try:
            element = self.element_clickable(locator)
            actions = ActionChains()
            actions.move_to_element(element).click().perform()
            return True
        except (
        NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, TimeoutException):
            pass

        raise ElementNotInteractableException(f"无法点击元素：{locator}")

    def click_element_by_javascripts(self, locator):
        """通过java_scripts点击元素"""
        ele = self.find_element(locator)
        self.driver.execute_script("arguments[0].click();", ele)
        self.log.info("点击元素：{}".format(locator))

    def element_text(self, locator):
        """获取元素text"""
        try:
            _text = self.element_displayed(locator).text
            self.log.info("获取文本：{}".format(_text))
            return _text
        except TimeoutException:
            print("文本获取失败")

    def get_notice_text(self):
        """获取当前notice的text"""
        _text = self.element_text(base_page['notice'])
        self.log.info("获取notice的文本：{}".format(_text))
        return _text

    def get_top_right_notice_text(self):
        """获取系统右上角弹出notice的text"""
        _text = self.element_text(base_page['top_right_notice'])
        self.log.info("获取系统notice的文本：{}".format(_text))
        return _text

    def close_right_notice(self):
        """关闭右上角弹出notice"""
        self.click_element(base_page['notice_close'])

    @property
    def get_source(self):
        """获取页面源代码"""
        return self.driver.page_source

    def refresh(self):
        """刷新页面F5"""
        self.driver.refresh()
        self.driver.implicitly_wait(30)

    def select_value_by_dropdown(self, ele, value):
        """从下拉框选择值"""
        self.click_element(ele)
        new_locator = self.replace_locator_text(base_page['dropdown_value'], value)
        self.click_element(new_locator)

    def select_value_by_radio_button(self, value):
        """选择单选按钮"""
        new_locator = self.replace_locator_text(base_page['redio_button'], value)
        self.click_element(new_locator)

    def upload_file(self, file_name):
        """上传文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        self.input_text(base_page['select_file_button'], file_path)
        self.log.info("上传文件：{}".format(file_path))

    @staticmethod
    def read_file(file_path):
        """
        读取xlsx, xls, 或 csv 文件，并返回pandas DataFrame。
        """
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_path.endswith('.xls'):
                df = pd.read_excel(file_path, engine='xlrd')
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                raise ValueError(f"不支持的文件类型: {file_path}")
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"文件未找到: {file_path}")
        except Exception as e:
            raise ValueError(f"读取文件时发生错误: {e}")

    def get_element_attr(self, locator, attr):
        """获取元素属性值"""
        return self.element_displayed(locator).get_attribute(attr)

    def click_cancel_button(self):
        """点击取消按钮"""
        self.click_element(base_page['cancel'])

    def click_delete_button(self):
        """点击删除按钮"""
        self.click_element(base_page['delete'])

    def click_refresh_button(self):
        """点击刷新按钮"""
        self.click_element(base_page['refresh'])

    def click_confirm_button(self):
        """点击确定按钮"""
        self.click_element(base_page['confirm'])
        self.log.info("点击确定按钮： {}".format(base_page['confirm']))

    def select_checkbox_from_table(self, value):
        """点击复选框"""
        new_loc = self.replace_locator_text(base_page['table_list_checkbox_column'], value)
        self.click_element(new_loc)

    def batch_delete_data(self, value_list):
        """批量删除数据"""
        for value in value_list:
            self.select_checkbox_from_table(value)
        self.click_element(base_page['batch_delete'])
        self.click_element(base_page['delete_confirm'])

    def page_resoure_load_complete(self):
        finished_loading = self.driver.execute_script("return document.readyState == 'complete'")
        if finished_loading:
            print("页面资源加载完成")
        else:
            print("页面资源可能还在加载中")

    def count_table_rows(self):
        """计算表格的行数"""
        return self.elements_num(base_page["tr"])

    def has_next_page(self):
        """检查是否还有下一页"""
        try:
            return self.find_element(base_page["next_page"])
        except TimeoutException:
            return False

    def get_total_table_rows(self):
        """获取分页表格的总行数"""
        total_rows = 0
        total_rows += self.count_table_rows()
        while self.has_next_page():
            self.click_element(base_page["next_page"])
            self.find_element(base_page["table"])
            total_rows += self.count_table_rows()
        print("列表总计： ", total_rows)
        return total_rows

    def click_close_button(self):
        """
        Click "X" button in page
        Returns:

        """
        self.click_element(base_page["close_button"])

    def select_cluster(self, cluster_name):
        """选择集群"""
        self.select_value_by_dropdown(base_page["cluster"], cluster_name)

    def get_item_explain_error(self, item):
        """
        获取字段校验结果
        Args:
            item:

        Returns:

        """

        new_loc = self.replace_locator_text(base_page['error_info'], item)
        return self.element_text(new_loc)




