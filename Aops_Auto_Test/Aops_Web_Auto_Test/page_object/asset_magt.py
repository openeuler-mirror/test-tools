# -*-coding:utf-8-*-
import math
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *

asset = Element('asset_magt')


class AssetMagtPage(WebPage):
    """Asset management page: including host management and host group management"""

    def enter_host_magt_page(self):
        """进入主机管理菜单"""
        if self.element_displayed(asset['host_magt_menu']):
            sleep(5)
            self.click_element(asset['host_magt_menu'])
        else:
            self.click_element(asset['asset_magt_menu'])
            self.click_element(asset['host_magt_menu'])

    def enter_host_group_magt_page(self):
        """进入主机组管理菜单"""
        if self.element_displayed(asset['host_group_magt_menu']):
            sleep(5)
            self.click_element(asset['host_group_magt_menu'])
        else:
            self.click_element(asset['asset_magt_menu'])
            self.click_element(asset['host_group_magt_menu'])

    def select_cluster(self, cluster_name):
        """选择集群"""
        self.select_value_by_dropdown(asset["cluster"], cluster_name)

    def select_host_group(self, group_name):
        """选择主机组"""
        self.select_value_by_dropdown(asset["host_group"], group_name)

    def add_host(self, hostname, cluster, hostgroup, host_ip, port, node, host_user, host_login_password):
        """添加单个主机"""
        self.click_element(asset['add_host_button'])
        self.input_text(asset['hostname'], hostname)
        self.select_cluster(cluster)
        self.select_host_group(hostgroup)
        self.input_text(asset['ip'], host_ip)
        self.input_text(asset['port'], port)
        self.select_value_by_radio_button(node)
        self.input_text(asset['host_user'], host_user)
        self.input_text(asset['host_login_password'], host_login_password)
        self.click_element(asset['submit'])

    def batch_add_host(self, cluster, file_name):
        """批量添加主机"""
        self.click_element(asset['batch_add_host_button'])
        self.select_cluster(cluster)
        sleep(5)
        self.upload_file(file_name)
        sleep(10)
        self.click_element(asset['upload_file_submit'])
        self.click_element(asset['pop-up_close_button'])
        sleep(1)
        self.click_refresh_button()

    def delete_host(self, hostip):
        """删除单个主机"""
        new_loc = self.replace_locator_text(asset['delete_host'], hostip)
        self.click_element(new_loc)
        self.find_element(asset['confirm_page'])
        self.click_delete_button()

    def get_host_info_from_table(self, hostname):
        """从列表获取host基本信息"""
        host_info = []
        new_loc = self.replace_locator_text(asset['host_list_column'],hostname)
        loc_num = self.elements_num(new_loc)
        for i in range(2,loc_num):
            lst = list(new_loc)
            lst[1] = lst[1]+'[%d]' %i
            locator = tuple(lst)
            host_info.append(self.element_text(locator))
            print("获取到已添加成功的host信息：", host_info)
        return host_info

    def get_host_ip_from_table(self):
        """从列表获取所有的host ip"""
        total_num_text = self.element_text(asset['total_host'])
        total_num = int(total_num_text[3:-1])
        host_ip_list = []
        if total_num == 0:
            host_ip_list = []
        else:
            total_page = math.ceil(total_num/10)
            for i in range(1, total_page+1):
                host_num = self.elements_num(asset['tr_num'])
                for j in range(host_num):
                    new_loc = self.replace_locator_text(asset['host_ip'], str(j + 1))
                    host_ip_list.append(self.element_text(new_loc))
                if not self.get_element_attr(asset['next_page'], 'aria-disabled'):
                    self.click_element(asset['next_page'])
        return host_ip_list

    def get_host_ip_from_excel(self, filename):
        """从excel中获取到host_ip"""
        excel_path = cm.BASE_DIR + '/test_data/' + filename
        data_frame = self.read_file(excel_path)
        host_name_column = data_frame['host_ip']
        data_array = host_name_column.values.tolist()
        print("获取到excel中host_ip列： ", data_array)
        return data_array

    def add_host_group(self, cluster, groupname, group_description):
        """增加主机组"""
        self.click_element(asset['add_host_group'])
        self.find_element(asset['add_host_group_windows'])
        self.select_cluster(cluster)
        self.input_text(asset['host_group_name'], groupname)
        self.input_text(asset['host_group_description'], group_description)
        self.click_confirm_button()

    def delete_host_group(self, groupname):
        """删除主机组"""
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

    def item_explain_error_info(self, filed):
        """获取字段的错误提示信息"""
        locator = self.replace_locator_text(asset['item_explain_error'], filed)
        return self.element_text(locator)

















