from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementClickInterceptedException

from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.utils.LogUtil import my_log


opt_page = Element('operation_magt')
log = my_log()


class ElementNotFoundError(Exception):
    pass


class OptMagtPage(WebPage):
    @property
    def automated_execution_tag(self) -> WebElement:
        e = self.find_element(opt_page['automated_execution'])
        if not isinstance(e, WebElement):
            raise ElementNotFoundError('automated execution element not Found')
        expanded = e.get_attribute('aria-expanded')
        if expanded == "false":
            e.click()
        return e

    @property
    def script_management_tag(self) -> WebElement:
        ae = self.automated_execution_tag
        if not ae:
            ElementNotFoundError('automated execution element not Found')

        se = self.find_element(opt_page['script_management'])
        if not isinstance(se, WebElement):
            raise ElementNotFoundError('script management element not Found')
        se.click()
        return se

    @property
    def operation_management_tag(self) -> WebElement:
        self.script_management_tag.click()
        oe = self.find_element(opt_page['operation_management'])
        if not isinstance(oe, WebElement):
            raise ElementNotFoundError('Operation Management element not Found')
        oe.click()
        return oe

    @property
    def new_operation_tag(self) -> WebElement:
        self.operation_management_tag.click()
        noe = self.find_element(opt_page['new_operation'])
        if not isinstance(noe, WebElement):
            raise ElementNotFoundError('New Operation element not Found')
        return noe

    @property
    def operate_name_form_input_tag(self) -> WebElement:
        onf = self.find_element(opt_page['operate_name_form'])
        if not isinstance(onf, WebElement):
            raise ElementNotFoundError('form_item_operate_name element not Found')
        return onf

    def delete_operation(self, operation_name: str):
        del_button = self.find_element(self.replace_locator_text(opt_page['delete_operation'], operation_name))
        del_button.click()
        try:
            self.click_confirm_button()
        except ElementClickInterceptedException:
            log.warn(f"have a ElementClickInterceptedException @delete_operation")

    def search_name_tabledata(self, name) -> WebElement:
        return self.find_element(self.replace_locator_text(opt_page['operation_name_td'], name))

    def get_notification_text(self):
        text = self.element_text(opt_page['notification_content'])
        log.info("获取notice的文本：{}".format(text))
        return text

    def add_new_operation(self, test_data):
        self.new_operation_tag.click()
        self.operate_name_form_input_tag.send_keys(test_data)
        self.click_confirm_button()
