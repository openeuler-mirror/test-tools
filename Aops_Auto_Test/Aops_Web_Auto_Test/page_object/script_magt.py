# -*-coding:utf-8-*-
import os
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element

script_elem = Element('script_magt')
base_page = Element('common')


class ScriptManagementPage(WebPage):

    def enter_script_mgmt_page(self):
        """进入脚本管理菜单"""
        expanded = self.get_element_attr(script_elem['automated_execution_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(script_elem['automated_execution_menu'])
        self.click_element(script_elem['script_mgmt_menu'])

    def delete_script(self, script_name, action='confirm'):
        """删除脚本"""
        try:
            table_text = self.get_script_list()
            assert script_name in table_text
        except Exception as e:
            print(f"该操作或脚本名不存在：{e}")
            pass
        else:
            new_loc = self.replace_locator_text(script_elem['script_delete'], script_name)
            self.click_element(new_loc)
            if action == "confirm":
                self.click_confirm_button()
                self.element_invisibility(new_loc)
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")

    def get_operate_list(self):
        """获取操作列表"""
        self.click_element(script_elem['operation_mgmt'])
        self.page_resoure_load_complete()
        operate_text = self.element_text(script_elem['operate_mgmt_table'])
        return operate_text

    def get_script_list(self):
        """获取脚本列表"""
        self.click_element(script_elem['script_mgmt'])
        self.click_refresh_button()
        self.page_resoure_load_complete()
        script_text = self.element_text(script_elem['script_mgmt_table'])
        return script_text

    def enter_new_script(self):
        """进入新建脚本页面"""
        self.click_element(script_elem['script_mgmt'])
        self.click_element(script_elem['new_script'])

    def get_script_operate_list(self):
        """获取新建脚本中的操作列表"""
        self.enter_new_script()
        self.click_element(script_elem['enter_operate_name'])
        script_operate_text = self.element_text(script_elem['operate_list'])
        self.click_cancel_button()
        operate_name_list = script_operate_text.split("\n")
        return operate_name_list

    def create_script_operate(self, operate_name, action='confirm'):
        """新建脚本中的新建操作"""
        self.enter_new_script()
        self.click_element(script_elem['new_script_operate'])
        self.input_text(script_elem['enter_the_operate'], operate_name)
        try:
            if action == "confirm":
                self.click_element(script_elem['script_operate_determine'])
            elif action == "cancel":
                self.click_element(script_elem['script_operate_cancel'])
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def get_arch_list(self):
        """获取新建脚本中的架构列表"""
        self.enter_new_script()
        self.click_element(script_elem['enter_arch'])
        script_arch_text = self.element_text(script_elem['arch_list'])
        self.click_cancel_button()
        return script_arch_text

    def get_os_list(self):
        """获取新建脚本中的操作系统列表"""
        self.enter_new_script()
        self.click_element(script_elem['enter_os'])
        script_os_text = self.element_text(script_elem['os_list'])
        self.click_cancel_button()
        return script_os_text

    @staticmethod
    def create_test_file(file_name, size_gb, char_count=None):
        """创建测试文件"""
        size_bytes = size_gb * 1024 ** 3
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        try:
            with open(file_path, 'wb') as file:
                if size_gb > 0:
                    file.seek(size_bytes - 1)
                    file.write(b'\0')
                else:
                    file.write(b'a' * char_count)
                    pass
            print(f"文件{file_path}已创建，大小为{size_gb}GB")
        except Exception as e:
            print(f"创建文件{file_path}时出错: {e}")

    @staticmethod
    def delete_test_file(file_name):
        """删除测试文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"文件{file_path}不存在")

    @staticmethod
    def copy_test_file(file_name, file_name_new):
        """复制测试文件"""
        file_path = cm.BASE_DIR + '/test_data/' + file_name
        file_path_new = cm.BASE_DIR + '/test_data/' + file_name_new
        if os.path.exists(file_path):
            os.system(f"cp {file_path} {file_path_new}")
        else:
            print(f"文件{file_path}不存在")

    def create_script_task(self, operate_name, script_name, arch_name, os_name, timeout, command, action='confirm'):
        """创建脚本任务"""
        self.enter_new_script()
        self.click_element(script_elem['enter_operate_name'])
        new_loc = self.replace_locator_text(script_elem['select_operate_name'], operate_name)
        self.element_displayed(new_loc)
        self.click_element(new_loc)
        self.input_text(script_elem['enter_script_name'], script_name)
        self.click_element(script_elem['enter_arch'])
        new_loc = self.replace_locator_text(script_elem['select_arch'], arch_name)
        self.click_element(new_loc)
        self.click_element(script_elem['enter_os'])
        new_loc = self.replace_locator_text(script_elem['select_os'], os_name)
        self.click_element(new_loc)
        self.input_text(script_elem['enter_timeout'], timeout)
        self.input_text(script_elem['enter_command'], command)
        self.upload_file("script_mgmt_testfile.sh")
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def enter_edit_script_task(self, script_name):
        """进入编辑脚本任务页面"""
        self.click_element(script_elem['script_mgmt'])
        new_loc = self.replace_locator_text(script_elem['operate_edit'], script_name)
        self.click_element(new_loc)

    def edit_script_task(self, script_name, arch_name, os_name, timeout, command, action='confirm'):
        """编辑脚本任务"""
        self.clear_before_input_text(script_elem['enter_script_name'], script_name)
        self.click_element(script_elem['enter_arch'])
        new_loc = self.replace_locator_text(script_elem['select_arch'], arch_name)
        self.click_element(new_loc)
        self.click_element(script_elem['enter_os'])
        new_loc = self.replace_locator_text(script_elem['select_os'], os_name)
        self.click_element(new_loc)
        self.clear_before_input_text(script_elem['enter_timeout'], timeout)
        self.clear_before_input_text(script_elem['enter_command'], command)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")

    def enter_create_new_task_page(self, ):
        """进入新建脚本执行任务页面"""
        self.click_element(script_elem['script_exec'])
        self.click_element(script_elem['open_new_task'])

    def create_script_exec_task(self, script_task_name, host_group, script_host_name,
                                operate_name, action='confirm', host_num='single'):
        """创建脚本执行任务"""
        self.create_script_exec_task_name(script_task_name)
        self.click_element(script_elem['enter_host_group_name'])
        new_loc = self.replace_locator_text(script_elem['select_host_group'], host_group)
        self.click_element(new_loc)
        try:
            if host_num == "single":
                self.select_value_by_dropdown(script_elem['enter_host_name'], script_host_name)
            elif host_num == "mul":
                for host_line in script_host_name:
                    self.select_value_by_dropdown(script_elem['enter_host_name'], host_line)
                    self.click_element(script_elem['enter_host_name'])
            else:
                raise ValueError("host_num 参数必须是single或mul")
        except Exception as e:
            self.click_confirm_button()
            print(f"处理按钮时发生错误1：{e}")
            pass
        self.select_value_by_dropdown(script_elem['enter_task_operate_name'], operate_name, "yes")
        task_page_text = self.element_text(script_elem['new_task_page'])
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是confirm或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误2：{e}")
        return task_page_text

    def create_script_exec_task_name(self, script_task_name, action='continue'):
        """创建脚本执行任务名称"""
        self.enter_create_new_task_page()
        self.clear_before_input_text(script_elem['enter_task_name'], script_task_name)
        self.click_confirm_button()
        task_page_text = self.element_text(script_elem['new_task_page'])
        try:
            if action == "continue":
                pass
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action 参数必须是空或cancel")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")
        return task_page_text

    def delete_script_exec_task(self, script_task_name):
        """删除脚本执行任务"""
        self.click_element(script_elem['script_exec'])
        self.click_refresh_button()
        script_exec_text = self.element_text(script_elem['script_exec_table'])
        try:
            assert script_task_name in script_exec_text
        except Exception as e:
            print(f"该任务名不存在：{e}")
            pass
        else:
            new_loc = self.replace_locator_text(script_elem['task_delete_button'], script_task_name)
            self.click_element(new_loc)
            self.click_confirm_button()

    def get_script_exec_list(self):
        """获取脚本执行列表"""
        self.click_element(script_elem['script_exec'])
        self.click_refresh_button()
        self.page_resoure_load_complete()
        script_exec_text = self.element_text(script_elem['script_exec_table'])
        return script_exec_text

    def get_script_exec_group_list(self):
        """获取脚本执行主机组列表"""
        self.enter_create_new_task_page()
        self.click_element(script_elem['enter_host_group_name'])
        script_group_text = self.element_text(script_elem['script_exec_group_list'])
        self.click_cancel_button()
        script_group_list = script_group_text.split("\n")
        return script_group_list

    def script_exec_batch_import_host(self, host_ip, input_model='input'):
        """批量导入主机"""
        try:
            if input_model == "input":
                self.clear_before_input_text(script_elem['enter_host_ip'], host_ip)
            elif input_model == "paste":
                self.copy_and_paste(script_elem['enter_task_name'], script_elem['enter_host_ip'], host_ip)
            else:
                raise ValueError("input_model 参数必须是input或paste")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")
        self.click_return(script_elem['enter_host_ip'])

    def script_exec_timed_task(self, date, timed_model='single', seconds_model='design', minute_model='design',
                               hour_model='design', day_model='每日', month_model='每月', week_model='unspecified',
                               year_model='每年', s_design_list=None, mi_design_list=None, h_design_list=None,
                               d_design_list=None, mo_design_list=None, w_design_list=None, y_design_list=None,
                               period_start=1, period_end=2, from_start=1, from_end=1,):
        """设置定时任务"""
        self.element_displayed(script_elem['new_task_page'])
        self.click_element(script_elem['enter_timed_task'])
        try:
            if timed_model == "single":
                self.click_element(script_elem['single_exec'])
                self.click_element(script_elem['enter_exec_time'])
                new_loc = self.replace_locator_text(script_elem['calendar_date'], date)
                self.click_element(new_loc)
                self.click_element(script_elem['calendar_determine'])
                self.click_confirm_button()
            elif timed_model == "cycle":
                self.click_element(script_elem['cycle_exec'])
                self.click_element(script_elem['cycle_exec_select'])
                self.click_element(script_elem['enter_seconds'])
                self.select_exec_plan(seconds_model, "pane-seconds", period_start, period_end,
                                      from_start, from_end, s_design_list)
                self.click_element(script_elem['enter_minute'])
                self.select_exec_plan(minute_model, "pane-minutes", period_start, period_end,
                                      from_start, from_end, mi_design_list)
                self.click_element(script_elem['enter_hour'])
                self.select_exec_plan(hour_model, "pane-Hour", period_start, period_end,
                                      from_start, from_end, h_design_list)
                self.click_element(script_elem['enter_day'])
                self.select_exec_plan(day_model, "pane-day", period_start, period_end,
                                      from_start, from_end, d_design_list)
                self.click_element(script_elem['enter_month'])
                self.select_exec_plan(month_model, "pane-month", period_start, period_end,
                                      from_start, from_end, mo_design_list)
                self.click_element(script_elem['enter_week'])
                self.select_exec_plan(week_model, "pane-weeks", period_start, period_end,
                                      from_start, from_end, w_design_list)
                self.click_element(script_elem['enter_year'])
                self.select_exec_plan(year_model, "pane-years", period_start, period_end,
                                      from_start, from_end, y_design_list)
                self.click_confirm_button()
            else:
                raise ValueError("timed_model 参数必须是single或cycle")
        except Exception as e:
            print(f"处理按钮时发生错误：{e}")
            raise

    def select_exec_plan(self, exec_plan, time_id, period_start, period_end,
                         from_start, from_end, design_list):
        if exec_plan == "period":
            new_loc = self.replace_locator_text(script_elem['select_period'], time_id)
            self.click_element(new_loc)
            new_loc = self.replace_locator_text(script_elem['input_period_start'], time_id)
            self.input_text(new_loc, period_start)
            new_loc = self.replace_locator_text(script_elem['input_period_end'], time_id)
            self.input_text(new_loc, period_end)
        elif exec_plan == "from":
            new_loc = self.replace_locator_text(script_elem['select_from'], time_id)
            self.click_element(new_loc)
            new_loc = self.replace_locator_text(script_elem['input_from_start'], time_id)
            self.input_text(new_loc, from_start)
            new_loc = self.replace_locator_text(script_elem['input_from_end'], time_id)
            self.input_text(new_loc, from_end)
        elif exec_plan == "design":
            new_loc = self.replace_locator_text(script_elem['select_design'], time_id)
            self.click_element(new_loc)
            for design_num in design_list:
                new_loc = self.replace_locator_text(script_elem['select_design_time'], time_id)
                new_loc = self.replace_locator_design_text(new_loc, "0", design_num)
                self.click_element(new_loc)
        elif exec_plan == "unspecified":
            new_loc = self.replace_locator_text(script_elem['select_unspecified'], time_id)
            self.click_element(new_loc)
        else:
            self.select_value_by_radio_button(exec_plan)

    def get_task_operate_list(self):
        """获取新建脚本中的操作列表"""
        self.enter_create_new_task_page()
        self.click_element(script_elem['enter_task_operate_name'])
        script_operate_text = self.element_text(script_elem['task_operate_list'])
        self.click_element(script_elem['enter_task_operate_name'])
        self.click_cancel_button()
        operate_name_list = script_operate_text.split("\n")
        return operate_name_list

    def enter_push_dir(self, dir_name):
        """打开推送目录"""
        self.clear_before_input_text(script_elem['input_push_dir'], dir_name)
        self.click_confirm_button()
        push_dir_text = self.element_text(script_elem['new_task_page'])
        return push_dir_text
