"""
operation management page objects
"""
from typing import List, Tuple, Union

from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementClickInterceptedException

from Aops_Web_Auto_Test.common.createtestdata import correct_operation_name
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.base_page import CommonPagingWebPage
from Aops_Web_Auto_Test.page_object.script_magt import ScriptManagementPage
from Aops_Web_Auto_Test.utils.LogUtil import my_log


opt_page = Element('operation_magt')
log = my_log()


class ElementNotFoundError(Exception):
    pass


class OptMagtPage(CommonPagingWebPage):
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
        self.operation_management_tag.click()
        operation = self.search_in_column(operation_name)
        if not operation:
            return
        del_button = self.find_element(self.replace_locator_text(opt_page['delete_operation'], operation_name))
        del_button.click()
        try:
            self.click_confirm_button()
        except ElementClickInterceptedException:
            log.warn(f"have a ElementClickInterceptedException @delete_operation")

    def search_name_tabledata(self, name) -> WebElement:
        return self.find_element(self.replace_locator_text(opt_page['operation_name_td'], name))

    def add_new_operation(self, test_data, return_operation=True) -> Union[WebElement, None]:
        self.script_management_tag.click()
        self.refresh()
        self.new_operation_tag.click()
        self.operate_name_form_input_tag.send_keys(test_data)
        self.click_confirm_button()
        if not return_operation:
            return None
        return self.search_in_column(test_data)

    def get_used_operation_list(self, script_page: ScriptManagementPage) -> List[str]:

        script_page.enter_script_mgmt_page()
        script_page.refresh()
        used_ops = self.get_table_column_data(2)
        if used_ops:
            return list(map(lambda d: d.text, used_ops))
        return []

    def get_unused_operation_name(self, script_page) -> str:
        self.script_management_tag.click()
        used_operation_names = self.get_used_operation_list(script_page)

        operation_name = correct_operation_name(5, 10)
        for _ in range(15):
            if operation_name not in used_operation_names:
                break
            operation_name = correct_operation_name(5, 10)
        return operation_name

    def rename_operation(self, old_name: str, new_name: str) -> WebElement:
        self.operation_management_tag.click()
        edit_button = self.find_element(self.replace_locator_text(opt_page['edit_operation'], old_name))
        edit_button.click()
        self.clear_before_input_text(opt_page['operate_name_form'], new_name)
        self.click_confirm_button()
        new_element = self.search_name_tabledata(new_name)
        return new_element

    def add_unused_operation(self, script_page) -> Tuple[WebElement, str]:
        operation_name = self.get_unused_operation_name(script_page)
        new_operation = self.add_new_operation(operation_name)
        return new_operation, operation_name
