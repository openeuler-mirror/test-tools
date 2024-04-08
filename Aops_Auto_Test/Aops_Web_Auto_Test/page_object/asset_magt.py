# -*-coding:utf-8-*-
import math
import pandas
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *

asset = Element('host_magt')


class AssetMagtPage(WebPage):
    """Asset management page: including host management and host group management"""

    def enter_host_magt_page(self):
        """进入主机管理菜单"""
        self.click_element(asset['asset_magt_menu'])
        sleep(5)
        self.click_element(asset['host_magt_menu'])

    def enter_host_group_magt_page(self):
        """进入主机组管理菜单"""
        self.click_element(asset['asset_magt_menu'])
        sleep(5)
        self.click_element(asset['host_group_magt_menu'])

    def add_host(self, hostname, hostgroup,ip,port, node,host_user,host_login_password):
        """添加单个主机"""
        self.click_element(asset['add_host_button'])
        sleep(5)
        global global_hostname
        global_hostname = hostname + str(dt_strftime('%H%M%S'))
        self.input_text(asset['hostname'], global_hostname)
        self.select_value_by_dropdown(hostgroup)
        self.input_text(asset['ip'], ip)
        self.input_text(asset['port'], port)
        self.select_value_by_radio_button(node)
        self.input_text(asset['host_user'], host_user)
        self.input_text(asset['host_login_password'], host_login_password)
        self.click_element(asset['submit'])

    def batch_add_host(self,file_name):
        """批量添加主机"""
        self.click_element(asset['batch_add_host_button'])
        self.upload_file(file_name)
        sleep(10)
        self.click_element(asset['upload_file_submit'])
        self.click_element(asset['pop-up_close_button'])
        sleep(1)
        self.click_refresh_button()
        sleep(10)

    def delete_host(self, hostname):
        """删除单个主机"""
        new_loc = self.replace_locator_text(asset['delete_host'], hostname)
        self.click_element(new_loc)
        self.click_element(asset['delete_confirm'])

    def get_host_info_from_table(self):
        """从列表获取host基本信息"""
        host_info = []
        new_loc = self.replace_locator_text(asset['host_list_column'],global_hostname)
        loc_num = self.elements_num(new_loc)
        for i in range(2,loc_num):
            lst = list(new_loc)
            lst[1] = lst[1]+'[%d]' %i
            locator = tuple(lst)
            host_info.append(self.element_text(locator))
            print("获取到已添加成功的host信息：", host_info)
        return host_info

    def get_host_name_from_table(self):
        """从列表获取所有的hostname"""
        total_num_text = self.element_text(asset['total_host'])
        total_num = int(total_num_text[3:-1])
        host_name_list = []
        total_page = math.ceil(total_num/10)
        for i in range(1, total_page+1):
            host_name_num = self.elements_num(asset['tr_num'])
            for j in range(host_name_num):
                new_loc = self.replace_locator_text(asset['host_name'], str(j + 1))
                host_name_list.append(self.element_text(new_loc))
            if not self.get_element_attr(asset['next_page'], 'aria-disabled'):
                self.click_element(asset['next_page'])
        return host_name_list

    def batch_delete_host(self,filename):
        """批量删除主机"""
        host_list = self.get_host_name_from_excel(filename)
        for host_ip in host_list:
            new_loc = self.replace_locator_text(asset['host_list_checkbox_column'], str(host_ip))
            self.click_element(new_loc)
        self.click_element(asset['batch_delete'])

    @staticmethod
    def get_host_name_from_excel(filename):
        """从excel中获取到host_ip"""
        excel_path = cm.BASE_DIR + '/test_data/' + filename
        data_frame = pandas.read_excel(excel_path)
        host_name_column = data_frame['host_ip']
        data_array = host_name_column.values.tolist()
        print("获取到excel中host_ip列： ", data_array)
        return data_array

    def add_host_group(self, groupname, group_description):
        """增加主机组"""
        global global_groupname
        global_groupname = groupname + str(dt_strftime('%H%M%S'))
        self.click_element(asset['add_host_group'])
        self.find_element(asset['add_host_group_windows'])
        self.input_text(asset['host_group'], global_groupname)
        self.input_text(asset['host_group_description'], group_description)
        self.click_confirm_button()

    def delete_single_host_group(self, groupname):
        """删除单个主机组"""
        new_loc = self.replace_locator_text(asset['host_group_delete'], groupname)
        self.click_element(new_loc)

    def batch_delete_host_group(self,group_list):
        """批量删除主机组"""
        for group_name in group_list:
            new_loc = self.replace_locator_text(asset['host_group_list_checkbox_column'], str(group_name))
            self.click_element(new_loc)
        self.click_element(asset['batch_delete'])

    def view_host_in_group(self, groupname):
        """查看组内主机"""
        new_loc = self.replace_locator_text(asset['host_group_check_host'], groupname)
        self.click_element(new_loc)

















