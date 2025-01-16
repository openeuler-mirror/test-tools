# -*-coding:utf-8-*-
import math
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element

asset = Element('asset_magt')
common = Element('common')


class AssetMagtPage(WebPage):

    def enter_host_magt_page(self):
        """
        Enter host magt menu
        Returns:

        """
        expanded = self.get_element_attr(asset['asset_magt_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(asset['asset_magt_menu'])
        self.click_element(asset['host_magt_menu'])
        self.element_displayed(asset['host_magt_page_title'])

    def enter_host_group_magt_page(self):
        """
        Enter host group magt menu
        Returns:

        """
        expanded = self.get_element_attr(asset['asset_magt_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(asset['asset_magt_menu'])
        self.click_element(asset['host_group_magt_menu'])
        self.element_displayed(asset['group_page_title'])

    def select_host_group(self, group_name):
        """
        Select group
        Args:
            group_name: 主机组名

        Returns:

        """
        self.select_value_by_dropdown(asset["host_group"], group_name)

    def add_host(self, hostname, cluster, hostgroup, host_ip, port, node, host_user, host_login_password):
        """
        Add single host
        Args:
            hostname: 主机名
            cluster: 集群名
            hostgroup: 主机组
            host_ip: 主机ip
            port: 端口号
            node: 管理节点/监控节点
            host_user: 登录主机时使用的用户名
            host_login_password: 登录主机时使用的密码

        Returns:

        """
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
        """
        Batch add host
        Args:
            cluster: 选择集群
            file_name: 选择批量上传的文件名

        Returns:

        """
        self.click_element(asset['batch_add_host_button'])
        self.select_cluster(cluster)
        self.upload_file(file_name)
        self.click_element(asset['upload_file_submit'])
        self.click_element(asset['pop-up_close_button'])

    def delete_host(self, hostip):
        """
        Delete host
        Args:
            hostip: hostip

        Returns:

        """
        """删除单个主机"""
        new_loc = self.replace_locator_text(asset['delete_host'], hostip)
        self.click_element(new_loc)
        self.find_element(asset['confirm_page'])
        self.click_delete_button()

    def get_host_info_from_table(self, hostip):
        """
        Retrieve all host information for the specified host from the data table
        Args:
            hostip: Input hostip

        Returns:

        """
        host_info = []
        new_loc = self.replace_locator_text(asset['host_list_column'], hostip)
        loc_num = self.elements_num(new_loc)
        for i in range(2,loc_num):
            lst = list(new_loc)
            lst[1] = lst[1]+'[%d]' %i
            locator = tuple(lst)
            host_info.append(self.element_text(locator))
        print(f"获取到主机ip是{hostip}的所有主机信息：", host_info)
        return host_info

    def get_host_ip_from_table(self):
        """
        Get all hostip from host table
        Returns:

        """
        total_num_text = self.element_text(asset['total_host'])
        total_num = int(total_num_text[2:-1])
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
        """
        从excel中获取到host_ip
        Args:
            filename: excel file

        Returns:

        """
        excel_path = cm.BASE_DIR + '/test_data/' + filename
        data_frame = self.read_file(excel_path)
        host_name_column = data_frame['host_ip']
        data_array = host_name_column.values.tolist()
        print("获取到excel中host_ip列： ", data_array)
        return data_array

    def add_host_group(self, cluster, groupname, group_description, action='confirm'):
        """
        Add host group
        Args:
            cluster: string类型，选择集群
            groupname: string类型，输入主机组名称
            group_description: string类型，输入主机组描述
            action: 'confirm' 表示点击确定按钮, 'cancel' 表示点击取消按钮

        Returns:

        """
        self.click_element(asset['add_host_group'])
        self.find_element(asset['add_host_group_windows'])
        self.select_cluster(cluster)
        self.input_text(asset['host_group_name'], groupname)
        self.input_text(asset['host_group_description'], group_description)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def delete_host_group(self, groupname, can_delete=True, action="confirm", expected_reason=None):
        """

        Args:
            groupname: 主机组名
            can_delete: 布尔值，指示是否可以删除数据。True表示可以删除，False表示不能删除
            action: 'confirm' 表示点击确定按钮, 'cancel' 表示点击取消按钮
            expected_reason: 当主机组存在主机时，主机组无法删除，需要输入无法删除的原因

        Returns:

        """
        new_loc = self.replace_locator_text(asset['host_group_delete'], groupname)
        self.click_element(new_loc)
        try:
            if can_delete:
                self.find_element(asset['confirm_page'])
                try:
                    if action == "confirm":
                        self.click_delete_button()
                        self.element_invisibility(common['delete'])
                    elif action == "cancel":
                        self.click_cancel_button()
                    else:
                        raise ValueError("action 参数必须是confirm或cancel")
                except Exception as e:
                    print(f"处理按钮时发生错误：{e}")
            else:
                try:
                    actual_reason = self.element_text(asset['delete_group_confirm_title'])
                    assert actual_reason == expected_reason
                except Exception as e:
                    print(f"处理存在主机的主机组失败： {e}")
                self.click_confirm_button()
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def view_host_in_group(self, groupname):
        """
        查看组内主机
        Args:
            groupname: 主机组名

        Returns:

        """
        new_loc = self.replace_locator_text(asset['host_group_check_host'], groupname)
        self.click_element(new_loc)
        self.find_element(asset['own_host_page'])
        return self.element_text(asset['host_in_group_hostip'])

    def get_table_num_from_upper_left(self):
        """
        Get number of tables from upper left
        Returns:

        """
        total_num_text = self.element_text(asset['table_num_upper_left'])
        return int(total_num_text[4:-5])

    def get_table_num_from_lower_right(self):
        """
        Get number of tables from lower right
        Returns:

        """
        total_num_text = self.element_text(asset['total_host'])
        return int(total_num_text[2:-1])

    def item_explain_error_info(self, filed):
        """获取字段的错误提示信息"""
        locator = self.replace_locator_text(asset['item_explain_error'], filed)
        return self.element_text(locator)

















