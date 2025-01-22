"""
Subject: test Automated execution -> Script Management -> Operation Management -> New Operation
"""
import pytest
from selenium.common.exceptions import ElementClickInterceptedException

from Aops_Web_Auto_Test.page_object.script_magt import ScriptManagementPage
from Aops_Web_Auto_Test.utils.LogUtil import my_log
from Aops_Web_Auto_Test.page_object.operation_magt import OptMagtPage
from Aops_Web_Auto_Test.common.createtestdata import correct_operation_name

log = my_log()


@pytest.fixture(scope='class')
def page(drivers) -> OptMagtPage:
    return OptMagtPage(drivers)


@pytest.fixture(scope='class')
def script_page(drivers) -> ScriptManagementPage:
    return ScriptManagementPage(drivers)


class TestNewOperation:
    @pytest.fixture(autouse=True)
    def setup_and_clear(self, page):
        self.operation_name = None
        self.need_cancel = 0
        yield
        if self.need_cancel:
            try:
                page.click_cancel_button()
            except ElementClickInterceptedException:
                log.warn(f"have a ElementClickInterceptedException @page.cancel_button.click")
        if self.operation_name:
            page.delete_operation(self.operation_name)
        page.refresh()
        page.page_resoure_load_complete()

    def test_new_operation_001_right_input(self, page):
        """
        新建操作-正常输入验证
        """
        test_data = correct_operation_name()

        page.add_new_operation(test_data)
        log.info(f"search new operation '{test_data}'")
        self.operation_name = test_data

        td = page.search_name_tabledata(test_data)
        assert td

    def test_new_operation_003_empty_input(self, page):
        """
        新建操作-空输入验证
        """
        page.operation_management_tag.click()
        page.refresh()
        page.new_operation_tag.click()
        page.click_confirm_button()
        self.need_cancel = 1
        assert page.get_item_explain_error('form_item_operate_name') in ('请输入操作名称', 'Please enter the operate')

    def test_new_operation_004_too_long_input(self, page):
        """
        新建操作-超长输入验证
        """
        test_data = correct_operation_name(129, 500)
        self.need_cancel = 1
        page.add_new_operation(test_data, return_operation=False)
        notice_info = page.get_item_explain_error('form_item_operate_name')
        assert notice_info in ('操作名称不能超过128字符', 'Operate Name cannot exceed 128 characters')

    def test_new_operation_005_duplicate_input(self, page):
        """
        新建操作-重复操作名验证
        """
        test_data = correct_operation_name()

        page.add_new_operation(test_data)

        td = page.search_name_tabledata(test_data)
        assert td

        page.add_new_operation(test_data, return_operation=False)

        notice_text = page.get_top_right_notice_text().strip()

        self.need_cancel = 1
        self.operation_name = test_data

        assert notice_text == 'data has existed'

    def test_new_operation_006_cancel_submit(self, page):
        """
        新建操作-取消新增操作名验证
        """
        test_data = correct_operation_name()

        page.new_operation_tag.click()
        page.operate_name_form_input_tag.send_keys(test_data)
        page.click_cancel_button()
        td = page.search_name_tabledata(test_data)
        assert td is None

    def test_new_operation_007_proper_display(self, page, script_page):
        """
        新建操作 - 新增操作名在页面显示验证
        """
        test_data = correct_operation_name(5, 12)
        # add operation name.
        page.add_new_operation(test_data)
        self.operation_name = test_data

        # check in script form
        page.script_management_tag.click()
        script_operation_names = script_page.get_script_operate_list()

        assert self.operation_name in script_operation_names

    def test_new_operation_008_edit_operation(self, page, script_page):
        """
        编辑操作-操作名未应用在脚本时编辑验证
        """
        new_operation, operation_name = page.add_unused_operation(script_page)
        new_operation_name = operation_name + '_new'

        new_operation = page.rename_operation(operation_name, new_operation_name)
        log.info(f'rename operation {operation_name} --> {new_operation_name}')
        self.operation_name = new_operation_name

        assert new_operation

    def test_new_operation_011_delete_unused_operation(self, page, script_page):
        """
        删除操作-操作名未应用在脚本时删除验证
        """
        # add operation
        new_operation, operation_name = page.add_unused_operation(script_page)
        assert new_operation
        # delete operation
        page.delete_operation(operation_name)
        page.refresh()
        page.operation_management_tag.click()

        empty_operation = page.search_name_tabledata(operation_name)
        assert empty_operation is None


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/script_magt/test_new_operation.py', '-s'])
