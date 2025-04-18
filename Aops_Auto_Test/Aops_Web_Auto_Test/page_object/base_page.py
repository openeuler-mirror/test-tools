# -*-coding:utf-8-*-
import time
from typing import List, Union, Tuple
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.utils.LogUtil import my_log
import pandas as pd
from selenium.webdriver.common.keys import Keys


base_page = Element('common')
driver = None


class WebPage(object):
    """selenium基类"""

    def __init__(self, driver):
        self.driver = driver
        self.log = my_log()
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
        except TimeoutException:
            raise TimeoutException("打开%s失败" % url)

    @staticmethod
    def element_locator(func, locator):
        """元素定位器"""
        name, value = locator
        return func(cm.LOCATE_MODE[name], value)

    @staticmethod
    def replace_locator_text(locator, new_value="", old_value="****"):
        """替换元素值"""
        lst = list(locator)
        lst[1] = lst[1].replace(old_value, new_value)
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
        """
        表单输入，不清理表单，如需要清理请调用 clear_before_input_text
        """
        ele = self.find_element(locator)
        ele.send_keys(txt)
        self.log.info("在{}中输入文本：{}".format(locator, txt))

    def clear_before_input_text(self, locator, txt):
        """输入(输入前先清空)"""
        ele = self.find_element(locator)
        ele.clear()
        ele.send_keys(txt)
        self.log.info("在{}中输入文本：{}".format(locator, txt))

    def click_element(self, locator):
        """点击元素"""

        try:
            element = self.find_element(locator)
            element.click()
            self.log.info("点击元素：{}".format(locator))
            return True
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            pass

        try:
            element = self.element_clickable(locator)
            self.driver.execute_script("arguments[0].click();", element)
            self.log.info("点击元素：{}".format(locator))
            return True
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            pass

        try:
            element = self.element_clickable(locator)
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            self.log.info("点击元素：{}".format(locator))
            return True
        except (NoSuchElementException, StaleElementReferenceException,
                ElementNotInteractableException, TimeoutException):
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
            self.log.info("获取{}元素的文本：{}".format(locator, _text))
            return _text
        except TimeoutException:
            print("获取{}元素文本失败")

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

    def select_value_by_dropdown(self, ele, value, is_scroll="no"):
        """从下拉框选择值"""
        self.click_element(ele)
        new_locator = self.replace_locator_text(base_page['dropdown_value'], value)
        if is_scroll == "no":
            self.click_element(new_locator)
        elif is_scroll == "yes":
            if self.element_displayed(new_locator):
                self.click_element(new_locator)
            else:
                self.dropdown_scroll(value)
        else:
            raise ValueError("is_scroll 参数必须是yes或no")

    def select_value_by_radio_button(self, value):
        """选择单选按钮"""
        new_locator = self.replace_locator_text(base_page['redio_button'], value)
        self.click_element(new_locator)

    def upload_file(self, file_name):
        """上传文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        self.input_text(base_page['select_file_button'], file_path)
        self.log.info("上传文件：{}".format(file_path))

    def search_by_placeholder(self, placeholder_value, search_value):
        """按照占位符搜索"""
        new_search_input_loc = self.replace_locator_text(base_page['search_placeholder'], placeholder_value)
        print("new_search_input_loc: ", new_search_input_loc)
        new_search_button_loc = self.replace_locator_text(base_page['search_button'], placeholder_value)
        self.clear_before_input_text(new_search_input_loc, search_value)
        self.click_element(new_search_button_loc)
        self.element_invisibility(base_page['table_search_position'])

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
        self.element_invisibility(base_page['table_search_position'])

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

    def select_host_group(self, group_name):
        """选择主机组"""
        if group_name != '':
            self.select_value_by_dropdown(base_page["host_group"], group_name)

    def select_host(self, host_name):
        """选择主机"""
        if host_name != '':
            self.select_value_by_dropdown(base_page["host_name"], host_name)

    def get_item_explain_error(self, item):
        """
        获取字段校验结果
        Args:
            item:

        Returns:

        """

        new_loc = self.replace_locator_text(base_page['error_info'], item)
        return self.element_text(new_loc)

    def element_is_editable(self, locator):
        """元素是否可点击"""
        try:
            return WebPage.element_locator(lambda *args: self.wait.until(
                EC.element_to_be_clickable(args)), locator)
        except TimeoutException:
            print(f"等待{locator} 元素不可点击")
            return None

    def dropdown_scroll(self, except_option):
        try:
            before_roll_list = self.element_text(base_page['dropdown_list']).split('\n')
            last_loc = self.replace_locator_text(base_page['dropdown_value'], before_roll_list[-1])
            ele = self.element_displayed(last_loc)
            ActionChains(self.driver).move_to_element(ele).perform()
            self.driver.execute_script('arguments[0].scrollIntoView(true);', ele)
            except_loc = self.replace_locator_text(base_page['dropdown_value'], except_option)
            if not self.element_displayed(except_loc):
                self.dropdown_scroll(except_option)
            else:
                self.click_element(except_loc)
        except Exception as e:
            print(f'获取元素失败！{e}')
            raise

    def copy_and_paste(self, input_ele, output_ele, txt):
        """复制和粘贴"""
        ele = self.find_element(input_ele)
        ele.clear()
        ele.send_keys(txt)
        ele.send_keys(Keys.CONTROL, "a")
        ele.send_keys(Keys.CONTROL, "c")
        ele.clear()
        ele = self.find_element(output_ele)
        ele.clear()
        ele.send_keys(Keys.CONTROL, "v")

    def click_return(self, locator):
        """点击回车"""
        ele = self.find_element(locator)
        ele.send_keys(Keys.RETURN)

    @staticmethod
    def replace_locator_design_text(locator, init_value, replace_value):
        """替换任意元素值"""
        lst = list(locator)
        lst[1] = lst[1].replace(init_value, replace_value)
        locator = tuple(lst)
        return locator

    def get_table_text(self) -> list:
        """
        获取表格的值，比如cve列表、主机列表
        :param : null
        :return: 列表的值以list格式返回
        """
        tr_list = []
        tr_len = self.elements_num(base_page['tr'])
        for tr in range(1, tr_len+1):
            new_loc = self.replace_locator_text(base_page['tr_per'], str(tr))
            text_result = self.element_text(new_loc)
            tr_list.append(text_result.split())
        return tr_list

    def sort(self, column):
        """
        按照指定列对数据进行排序

        :param column: 需要获取排序的列名
        :return: 返回排序后
        """
        new_loc = self.replace_locator_text(base_page['sort_column'], column)
        self.click_element(new_loc)
        sort_status = self.get_element_attr(new_loc, "aria-sort")
        self.log.info("对{}列进行{}排序".format(column, sort_status))

    def get_sort_status(self, column, action):
        """
        获取指定列排序后的状态（上升或下降）的类属性。

        :param column: 需要获取排序状态的列名
        :param action: 排序动作，'up' 表示上升，'down' 表示下降
        :return: 指定元素的类属性
        """
        locator_template = base_page['sort_up_status'] if action == 'up' else base_page['sort_down_status']
        new_loc = self.replace_locator_text(locator_template, column)
        return self.get_element_attr(new_loc, "class")

    def is_sorted_ascending(self,  lst: List) -> bool:
        """
        检查列表是否按升序排列。

        :param lst: 需要检查的列表
        :return: 如果列表按升序排列，则返回True；否则返回False
        """
        for i in range(len(lst) - 1):
            if lst[i] > lst[i + 1]:
                self.log.error("列表{}不是按照升序排序".format(lst))
                return False
        self.log.info("列表{}按照升序排序".format(lst))
        return True

    def is_sorted_descending(self,  lst: List) -> bool:
        """
        检查列表是否按降序排列。

        :param lst: 需要检查的列表
        :return: 如果列表按降序排列，则返回True；否则返回False
        """
        for i in range(len(lst) - 1):
            if lst[i] < lst[i + 1]:
                self.log.error("列表{}不是按照降序排序".format(lst))
                return False
        self.log.info("列表{}按照降序排序".format(lst))
        return True


class CommonPagingWebPage(WebPage):
    def get_table_column_data(self, column_index=1) -> List[WebElement]:
        return self.find_elements(self.replace_locator_text(base_page['tbody_tds'], str(column_index)))

    @property
    def first_page(self) -> Union[WebElement, None]:
        first_page = self.find_element(base_page['first_page'])
        if not isinstance(first_page, WebElement):
            return None
        return first_page

    @property
    def last_page(self) -> Union[WebElement, None]:
        last_page = self.find_element(base_page['last_page'])
        if not isinstance(last_page, WebElement):
            return None
        return last_page

    @property
    def previous_page_button(self) -> Union[WebElement, None]:
        button = self.find_element(base_page['previous_page_common'])
        if not isinstance(button, WebElement):
            return None
        return button

    @property
    def next_page_button(self) -> Union[WebElement, None]:
        button = self.find_element(base_page['next_page_common'])
        if not isinstance(button, WebElement):
            return None
        return button

    def get_column_data_all_pages(self, column_index=1) -> Tuple[int, List]:
        """

        Args:
            column_index: which column

        Returns: status_code, data_list
        status code: 0 ok. others error.
        """
        if not self.first_page:
            print(f'not found first page button')
            return 1, []

        try:
            self.first_page.click()
        except Exception as e:
            print(f'waring: first page click interrupted {e}')
            self.first_page.click()

        column_data = []
        # 从第一页开始点下一页，直到点到下一页不能点
        while True:
            table_data = self.get_table_column_data(column_index)
            if table_data:
                column_data.extend(list(map(lambda d: d.text, table_data)))
            next_button = self.next_page_button
            if not next_button:
                print(f'not found next page button @get_table_column_data_all_pages')
                break
            if next_button.get_attribute('aria-disabled') != 'false':
                break
            next_button.click()
            # 数据加载时间
            # TODO: 现在主流前端js框架<vue, react>， 对虚拟DOM的局部修改， 不会反应在document.readystate状态上。
            #  目前python没有很好的办法监控dom局部变更状态。 暂定用sleep等table更新完成。
            time.sleep(2)

        return 0, column_data

    def search_in_column(self, search_text, column_index=1) -> Union[WebElement, None]:
        """

        Args:
            search_text: 查询的数据
            column_index: 查询的字段序号

        Returns: WebElement | None
        """
        if not self.first_page:
            print(f'not found first page button')
            return None
        try:
            self.first_page.click()
        except Exception as e:
            print(f'waring: first page click interrupted {e}')
            self.first_page.click()

        while True:
            table_data = self.get_table_column_data(column_index)
            if table_data:
                for td in table_data:
                    if td.text == search_text:
                        return td

            next_button = self.next_page_button
            if not next_button:
                print(f'not found next page button @get_table_column_data_all_pages')
                break
            if next_button.get_attribute('aria-disabled') != 'false':
                break
            next_button.click()
            # 数据加载时间
            # TODO: 现在主流前端js框架<vue, react>， 对虚拟DOM的局部修改， 不会反应在document.readystate状态上。
            #  目前python没有很好的办法监控dom局部变更状态。 暂定用sleep等table更新完成。
            time.sleep(2)
        return None
