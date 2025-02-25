# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.script_magt import ScriptManagementPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.page_object.operation_magt import OptMagtPage
from selenium.common.exceptions import ElementClickInterceptedException
from Aops_Web_Auto_Test.utils.LogUtil import my_log
from Aops_Web_Auto_Test.common.createtestdata import *
from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.common.readconfig import ini

log = my_log()
script_elem = Element('script_magt')
base_page = Element('common')


@pytest.fixture(scope='class')
def script_mgmt(drivers) -> ScriptManagementPage:
    return ScriptManagementPage(drivers)


@pytest.fixture(scope='class')
def operate_mgmt(drivers) -> OptMagtPage:
    return OptMagtPage(drivers)


class TestCreateExecTask:

    @pytest.fixture(scope='function', autouse=True)
    def prepare_and_clean_data(self, script_mgmt, operate_mgmt):
        script_mgmt.enter_script_mgmt_page()
        self.task_name_pre = None
        self.need_cancel = 0
        self.host1 = ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTNAME1")
        self.host2 = ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTNAME2")
        self.group1 = ini._get("CLUSTER.GROUP1", "CLUSTER_NAME1.GROUP1")
        self.host1_ip = ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTIP1")
        self.host2_ip = ini._get("CLUSTER.GROUP1.HOST", "CLUSTER_NAME1.GROUP1.HOSTIP2")
        self.operate_name_pre = None
        yield
        if self.need_cancel:
            try:
                script_mgmt.click_cancel_button()
            except ElementClickInterceptedException:
                log.warn(f"have a ElementClickInterceptedException @page.cancel_button.click")
        try:
            if self.operate_name_pre:
                script_mgmt.click_element(script_elem['operation_mgmt'])
                operate_mgmt.delete_operation(self.operate_name_pre)
            if self.task_name_pre:
                script_mgmt.delete_script_exec_task(self.task_name_pre)
        except Exception as e:
            print(f"清理环境过程报错：{e}")
            pass

    def test_create_exec_task_001_check_task_name_length(self, script_mgmt):
        """新建任务-任务名称长度校验"""
        script_task_name = repo_name(128)
        task_page_text = script_mgmt.create_script_exec_task_name(script_task_name, "cancel")
        assert "任务名称不能超过128字符" not in task_page_text
        script_task_name = repo_name(129)
        task_page_text = script_mgmt.create_script_exec_task_name(script_task_name, "cancel")
        assert "任务名称不能超过128字符" in task_page_text

    def test_create_exec_task_002_check_task_name(self, script_mgmt, operate_mgmt):
        """新建任务-任务名称校验"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.task_name_pre = create_new_name("task_name_pre")
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        exec_page_text = script_mgmt.get_script_exec_list()
        assert self.task_name_pre in exec_page_text
        script_mgmt.delete_script_exec_task(self.task_name_pre)
        self.task_name_pre = self.task_name_pre + '#$%^&*@#!'
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        exec_page_text = script_mgmt.get_script_exec_list()
        assert self.task_name_pre in exec_page_text
        task_page_text = script_mgmt.create_script_exec_task_name("", "cancel")
        assert "请输入任务名称" in task_page_text

    def test_create_exec_task_003_check_character_type(self, script_mgmt, operate_mgmt):
        """新建任务-任务名称字符类型校验"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.task_name_pre = create_new_name("task_name_中文")
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        exec_page_text = script_mgmt.get_script_exec_list()
        assert self.task_name_pre in exec_page_text
        script_mgmt.delete_script_exec_task(self.task_name_pre)
        self.task_name_pre = create_new_name("task_name_123456")
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        exec_page_text = script_mgmt.get_script_exec_list()
        assert self.task_name_pre in exec_page_text

    def test_create_exec_task_004_check_group_select(self, script_mgmt, drivers):
        """新建任务-主机组选择校验"""
        host_group = AssetMagtPage(drivers)
        script_exec_group_list = script_mgmt.get_script_exec_group_list()
        host_group.enter_host_group_magt_page()
        host_group_text = script_mgmt.element_text(script_elem['host_group_table'])
        script_mgmt.enter_script_mgmt_page()
        for group_line in script_exec_group_list:
            assert group_line in host_group_text

    def test_create_exec_task_005_check_host_select(self, script_mgmt, operate_mgmt):
        """新建任务-主机选择校验"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.task_name_pre = create_new_name("task_name_pre")
        exec_text = script_mgmt.create_script_exec_task(self.task_name_pre, self.group1,
                                                        self.host1, self.operate_name_pre)
        assert "请选择主机" not in exec_text
        self.host = self.host1 + 'absent'
        exec_text = script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host,
                                                        self.operate_name_pre, "cancel")
        assert "请选择主机" in exec_text
        exec_text = script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, "",
                                                        self.operate_name_pre, "cancel")
        assert "请选择主机" in exec_text

    def test_create_exec_task_006_check_host_range(self, script_mgmt, operate_mgmt):
        """新建任务-主机范围校验"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        self.task_name_pre = create_new_name("task_name_pre")
        host_list = [self.host1, self.host2]
        exec_text = script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, host_list,
                                                        self.operate_name_pre, "confirm", "mul")
        script_exec_text = script_mgmt.get_script_exec_list()
        assert self.host1 + '\n' + self.host2 in exec_text
        assert self.task_name_pre in script_exec_text
        exec_text = script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, "0.0.0.0",
                                                        self.operate_name_pre, "cancel")
        assert "请选择主机" in exec_text

    def test_create_exec_task_007_host_copy_paste(self, script_mgmt):
        """新建任务-主机剪切板粘贴复制"""
        script_mgmt.enter_create_new_task_page()
        script_mgmt.click_element(script_elem['batch_import_host'])
        script_mgmt.script_exec_batch_import_host(self.host1_ip, "paste")
        batch_host_text = script_mgmt.element_text(script_elem['new_task_page'])
        assert self.host1 + " " + self.host1_ip in batch_host_text
        script_mgmt.element_invisibility(base_page['notice'])
        test_data = test_script_name(10)
        script_mgmt.script_exec_batch_import_host(test_data, "paste")
        log_info = script_mgmt.get_notice_text()
        self.need_cancel = 1
        assert "未找到以下IP的主机" and "已帮您自动剔除未找到的主机" in log_info

    def test_create_exec_task_008_invalid_batch_host(self, script_mgmt):
        """新建任务-批量主机导入"""
        script_mgmt.enter_create_new_task_page()
        script_mgmt.click_element(script_elem['batch_import_host'])
        host_ip_str = self.host1_ip + ',' + self.host2_ip
        script_mgmt.script_exec_batch_import_host(host_ip_str)
        batch_host_text = script_mgmt.element_text(script_elem['new_task_page'])
        assert self.host1 + " " + self.host1_ip and self.host2 + " " + self.host2_ip in batch_host_text
        test_symbol_random = set(test_symbol(1)) - {','}
        test_symbol_random = ''.join(map(str, test_symbol_random))
        host_ip_str = self.host1_ip + test_symbol_random + self.host2_ip
        script_mgmt.element_invisibility(base_page['notice'])
        script_mgmt.script_exec_batch_import_host(host_ip_str)
        log_info = script_mgmt.get_notice_text()
        self.need_cancel = 1
        assert "未找到以下IP的主机" and "已帮您自动剔除未找到的主机" in log_info

    def test_create_exec_task_009_invalid_host_format(self, script_mgmt):
        """新建任务-主机格式检查"""
        script_mgmt.enter_create_new_task_page()
        script_mgmt.click_element(script_elem['batch_import_host'])
        script_mgmt.script_exec_batch_import_host(self.host1_ip)
        batch_host_text = script_mgmt.element_text(script_elem['new_task_page'])
        assert self.host1 + " " + self.host1_ip in batch_host_text
        test_data = repo_data(10)
        script_mgmt.element_invisibility(base_page['notice'])
        script_mgmt.script_exec_batch_import_host(test_data)
        log_info = script_mgmt.get_notice_text()
        self.need_cancel = 1
        assert "未找到以下IP的主机" and "已帮您自动剔除未找到的主机" in log_info

    def test_create_exec_task_010_invalid_host(self, script_mgmt):
        """新建任务-非法主机"""
        script_mgmt.enter_create_new_task_page()
        script_mgmt.click_element(script_elem['batch_import_host'])
        test_data = host_ip() + ".256"
        script_mgmt.element_invisibility(base_page['notice'])
        script_mgmt.script_exec_batch_import_host(test_data)
        log_info = script_mgmt.get_notice_text()
        assert "未找到以下IP的主机" + test_data in log_info
        script_mgmt.element_invisibility(base_page['notice'])
        test_data = test_data + ',' + test_data
        script_mgmt.script_exec_batch_import_host(test_data)
        log_info = script_mgmt.get_notice_text()
        self.need_cancel = 1
        assert "未找到以下IP的主机" + test_data in log_info

    def test_create_exec_task_011_check_timed_task(self, script_mgmt):
        """新建任务-检查定时任务"""
        script_mgmt.enter_create_new_task_page()
        timed_text = script_mgmt.element_text(script_elem['new_task_page'])
        assert "执行策略\n单次执行\n周期执行" not in timed_text
        test_date = str(dt_strftime('%Y-%m-%d', 1))
        script_mgmt.script_exec_timed_task(test_date)
        timed_text = script_mgmt.element_text(script_elem['new_task_page'])
        self.need_cancel = 1
        assert "执行策略\n单次执行\n周期执行" in timed_text

    def test_create_exec_task_012_check_calendar_select(self, script_mgmt):
        """新建任务-日历选择校验"""
        script_mgmt.enter_create_new_task_page()
        test_date = str(dt_strftime('%Y-%m-%d'))
        script_mgmt.element_displayed(script_elem['new_task_page'])
        script_mgmt.script_exec_timed_task(test_date)
        timed_text = script_mgmt.element_text(script_elem['new_task_page'])
        script_mgmt.click_cancel_button()
        assert "任务执行时间不能早于当前时间" in timed_text
        script_mgmt.enter_create_new_task_page()
        test_date = str(dt_strftime('%Y-%m-%d', 1))
        script_mgmt.element_displayed(script_elem['new_task_page'])
        script_mgmt.script_exec_timed_task(test_date)
        timed_text = script_mgmt.element_text(script_elem['new_task_page'])
        self.need_cancel = 1
        assert "任务执行时间不能早于当前时间" not in timed_text

    def test_create_exec_task_013_cron_select(self, script_mgmt):
        """新建任务-cron表达式校验"""
        script_mgmt.enter_create_new_task_page()
        script_mgmt.element_displayed(script_elem['new_task_page'])
        script_mgmt.script_exec_timed_task('', "cycle", s_design_list=["1"],  mi_design_list=["1"], h_design_list=["1"],
                                           d_design_list=["1"], mo_design_list=["1"], w_design_list=["1"],
                                           y_design_list=["1"],)
        timed_text = script_mgmt.element_displayed(script_elem['input_cron']).get_attribute('value')
        self.need_cancel = 1
        assert "0,1 0,1 0,1 * * ? *" in timed_text

    def test_create_exec_task_014_operate_select(self, script_mgmt, operate_mgmt):
        """新建任务-操作列表及选择校验"""
        self.operate_name_pre = create_new_name("operate_name_pre")
        operate_mgmt.add_new_operation(self.operate_name_pre)
        operate_name_list = script_mgmt.get_task_operate_list()
        operate_text = script_mgmt.get_operate_list()
        for operate_name_line in operate_name_list:
            assert operate_name_line in operate_text
        self.task_name_pre = create_new_name("task_name_pre")
        script_mgmt.create_script_exec_task(self.task_name_pre, self.group1, self.host1, self.operate_name_pre)
        new_loc = script_mgmt.replace_locator_text(script_elem['task_delete_button'], self.task_name_pre)
        script_mgmt.element_displayed(new_loc)
        exec_text = script_mgmt.element_text(script_elem['script_exec_table'])
        assert self.task_name_pre in exec_text

    def test_create_exec_task_015_push_dir_select(self, script_mgmt):
        """新建任务-操作列表及选择校验"""
        script_mgmt.enter_create_new_task_page()
        script_mgmt.element_displayed(script_elem['new_task_page'])
        script_mgmt.element_is_editable(script_elem['enter_only_push'])
        script_mgmt.click_element(script_elem['enter_only_push'])
        push_dir_text = script_mgmt.enter_push_dir("")
        assert "请输入推送目录" in push_dir_text
        dir_name = task_name() + "."
        push_dir_text = script_mgmt.enter_push_dir(dir_name)
        assert "推送目录不能包含 . 或 .. ，请填写绝对路径" in push_dir_text
        dir_name = task_name() + ".."
        push_dir_text = script_mgmt.enter_push_dir(dir_name)
        assert "推送目录不能包含 . 或 .. ，请填写绝对路径" in push_dir_text
        dir_name = task_name().replace(".", "")
        push_dir_text = script_mgmt.enter_push_dir(dir_name)
        self.need_cancel = 1
        assert "请输入推送目录" not in push_dir_text


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/automated_execution/script_magt/test_create_exec_task.py', '-s'])
