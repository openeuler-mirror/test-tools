# -*-coding:utf-8-*-
import math
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *

auto = Element('automated_execution.yaml')


class AutomatedExecutionPage(WebPage):

    def enter_command_magt_page(self):
        """进入命令管理菜单"""
        expanded = self.get_element_attr(auto['automated_execution_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(auto['automated_execution_menu'])
        self.click_element(auto['command_magt_menu'])

    def enter_script_magt_page(self):
        """进入脚本管理菜单"""
        expanded = self.get_element_attr(auto['automated_execution_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(auto['automated_execution_menu'])
        self.click_element(auto['script_magt_menu'])




