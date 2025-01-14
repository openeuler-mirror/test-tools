# -*-coding:utf-8-*-
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element

command_elem = Element('command_magt')


class CommandManagementPage(WebPage):

    def enter_command_magt_page(self):
        """进入命令管理菜单"""
        expanded = self.get_element_attr(command_elem['automated_execution_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(command_elem['automated_execution_menu'])
        self.click_element(command_elem['command_magt_menu'])

    def add_command(self, command_name, command_timeout, command_content, action='confirm'):
        """新建命令"""
        self.click_element(command_elem['new_command'])
        self.find_element(command_elem['new_command_windows'])
        self.input_text(command_elem['command_name'], command_name)
        self.input_text(command_elem['timeout'], command_timeout)
        self.input_text(command_elem['content'], command_content)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action参数必须是confirm或者cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def delete_command(self, command_name):
        """删除命令"""
        new_loc = self.replace_locator_text(command_elem['delete_command'], command_name)
        self.click_element(new_loc)
        conform_button = self.find_element(command_elem['confirm_page'])
        if conform_button:
            conform_button.click()

    def item_explain_error_info(self, filed):
        """获取字段的错误提示信息"""
        locator = self.replace_locator_text(command_elem['item_explain_error'], filed)
        return self.element_text(locator)
