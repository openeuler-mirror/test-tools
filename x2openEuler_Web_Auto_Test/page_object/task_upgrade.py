"""
@Time : 2024/12/28 10:30
@Auth : ysc
@File : task_upgrade.py
@IDE  : PyCharm
"""
from x2openEuler_Web_Auto_Test.common.readelement import Element
from x2openEuler_Web_Auto_Test.page_object.base_page import BasePage
from x2openEuler_Web_Auto_Test.common.log import log

task_upgrade = Element('task_upgrade')


class TaskUpgrade(BasePage):
    """
    os upgrade task page
    """

    def create_task_upgrade(self, task_name=None):
        """
        新建升级任务
        :param task_name: 任务名称，str
        :return:
        """
        self.click(task_upgrade["title"])
        self.click(task_upgrade["new_task_button"])
        if self.is_element_exist(30, task_upgrade["upgrade_button"]):
            self.click(task_upgrade["upgrade_button"])
            if task_name:
                self.clear(task_upgrade["task_name_input"])
                self.send_keys(task_upgrade["task_name_input"], task_name)
        else:
            log.error("系统升级按钮不存在，升级任务失败 !")

    def add_Service_Software(self, node):
        """
        添加业务软件相关信息
        :param node: 节点信息
        :return:
        """
        service_list = ["business_rpms", "business_dirs", "persist_rpms", "install_rpms"]
        for service in service_list:
            if node.get(service):
                self.send_keys(task_upgrade[service], node.get(service))
            else:
                log.info(f"{service} service does not need to be configured !")

    def add_advance_setting_conf(self, node):
        """
        添加高级配置等相关信息
        :param node: 节点列表
        :return:
        """
        setting_list = ["back_path", "back_save_path", "back_ignore_path", "conflict_software_config",
                        "cmdline_config", "swap_software_config", "migrate_file", "migrate_permission"]
        for setting in setting_list:
            if node.get(setting):
                self.send_keys(task_upgrade[setting], node.get(setting))
            else:
                log.info(f"{setting} service does not need to be configured !")

    def add_custom_scripts_conf(self, node):
        """
        添加自定义脚本配置
        :param node: 节点列表
        :return:
        """
        scripts_list = ["custom_script", "pre_upgrade_script", "post_upgrade_script_before_reboot",
                        "post_upgrade_script_after_reboot", "SMT_custom_script"]
        for script in scripts_list:
            if node.get(script):
                self.click(task_upgrade[script])
                self.send_keys(task_upgrade[f"{script}_path"], node.get(f"{script}_path"))
            else:
                log.info(f"{script} script does not need to be configured !")

    def add_single_node_upgrade(self, node):
        """
        通过添加节点方式添加单节点
        :param node: 节点信息，dict
        :return:
        """
        # 创建节点按钮
        self.click(task_upgrade["add_node_button"])
        # SSH传输须知
        self.click(task_upgrade["trans_notes"])
        # 待升级节点IP
        if node.get('ip_version') == 'IPv6':
            self.click(task_upgrade["ipv6_button"])
            self.sleep(1)
            self.clear(task_upgrade["ipv6_input"])
            if node.get('ip').find(':') >= 0:
                self.send_keys(task_upgrade["ipv6_input"], node.get('ip').replace(':', '.'))
            else:
                self.send_keys(task_upgrade["ipv6_input"], node.get('ip'))
            if node.get('NIC'):
                self.send_keys(task_upgrade["nic_input"], node.get("NIC"))
            else:
                log.info("No specific network card name !")
        else:
            self.send_keys(task_upgrade["ipv4_input"], node.get('ip'))

        # 节点别名
        self.send_keys(task_upgrade["alias_input"], node.get('nick_name'))
        # 端口
        self.send_keys(task_upgrade["port_input"], node.get('port'))
        # 用户认证
        self.send_keys(task_upgrade["user_name_input"], node.get('user_name'))
        self.send_keys(task_upgrade["passwd_input"], node.get('password'))
        if node.get('user_name') != "root":
            self.send_keys(task_upgrade["passwd_input"], node.get('root_password'))
        else:
            log.info("The current user is root !")
        # 源操作系统版本
        self.send_keys(task_upgrade["src_os_input"], node.get('source_sys_version'))
        self.sleep(1)
        self.click(("xpath", f"//li[contains(.,'{node.get('source_sys_version')}')]"))
        self.sleep(1)
        # 目标操作系统
        self.send_keys(task_upgrade["target_os_input"], node.get('target_sys_version'))
        self.sleep(1)
        self.click(("xpath", f"//li[contains(.,'{node.get('target_sys_version')}')]"))
        self.sleep(1)
        # repo名称
        self.click_element_by_js(task_upgrade["repo_input"])
        self.click(("xpath", f"//span[text()='Repository' or text()= 'repo源名称']"
                             f"//ancestor::div[2]//div[text()='{node.get('repo_name')}']"))
        self.click(task_upgrade["repo_confirm"])

        # 添加业务软件信息配置
        if node.get('add_service_flag'):
            self.add_Service_Software(node)
        else:
            log.info("Configuration of the current node without business software !")

        # 添加高级配置
        if node.get('add_advance_setting_flag'):
            self.click_element_by_js(task_upgrade["advance_setting_button"])
            self.sleep(1)
            self.add_advance_setting_conf(node)
        else:
            log.info("There is no advanced configuration for the current node !")

        # 自定义脚本配置
        if node.get('add_scripts_flag'):
            self.add_custom_scripts_conf(node)
        else:
            log.info("Configuration of the current node without custom scripts !")

        self.click_element_by_js(task_upgrade["add_node_confirm_button"])
        self.is_element_exist(60, task_upgrade["alert_confirm_button"])
        self.click_element_by_js(task_upgrade["alert_confirm_button"])
        self.sleep(1)

    def env_check(self):
        """
        环境检查
        :return:
        """
        self.click(task_upgrade["add_node_task_confirm"])
        self.click(task_upgrade["view_details_button"])
        self.is_element_exist(1800, task_upgrade["start_check_button"])
        self.sleep(1)
        self.refresh()

    def upgrade_check(self):
        """
        升级前检查
        :return:
        """
        self.is_element_exist(1800, task_upgrade["start_check_button"])
        self.click_element_by_js(task_upgrade["start_check_button"])
        self.is_element_exist(1800, task_upgrade["task_upgrade_button"])
        self.sleep(1)
        self.refresh()

    def check_res(self, stage_flag):
        """
        环境巡检结果
        :return: 返回相关检查结果
        """
        stage_flag_list = {'env': "env_check_res", 'pre_upgrade': "pre_upgrade_check_res",
                           'upgrade': "upgrade_check_res", 'upgrade_after_reboot': "upgrade_after_reboot_res",
                           'post_upgrade': "post_upgrade_check_res", 'roll_back': "roll_back_res",
                           'roll_back_after_reboot': "roll_back_after_reboot_res"}
        if stage_flag in stage_flag_list:
            return self.get_element_text(task_upgrade[stage_flag_list[stage_flag]])
        else:
            log.error("stage_flag is not exist!")
            return None

    def upgrade_node(self):
        """
        升级节点
        :return:
        """
        self.is_element_exist(1800, task_upgrade["task_upgrade_button"])
        self.click_element_by_js(task_upgrade["task_upgrade_button"])
        self.is_element_exist(30, task_upgrade["alert_node_confirm"])
        self.click(task_upgrade["alert_node_confirm"])
        self.is_element_exist(4800, task_upgrade["reboot_node_button"])
        self.refresh()

    def upgrade_retry_node(self):
        """
        升级失败重试节点
        :return:
        """
        self.is_element_exist(1800, task_upgrade["retry_button"])
        self.click_element_by_js(task_upgrade["retry_button"])
        self.is_element_exist(30, task_upgrade["alert_node_confirm"])
        self.click(task_upgrade["alert_node_confirm"])
        self.is_element_exist(2400, task_upgrade["reboot_node_button"])
        self.refresh()

    def reboot_retry_node(self):
        """
        重启超时重试节点
        :return:
        """
        self.is_element_exist(1800, task_upgrade["retry_button"])
        self.click_element_by_js(task_upgrade["retry_button"])
        self.is_element_exist(30, task_upgrade["alert_node_confirm"])
        self.click(task_upgrade["alert_node_confirm"])
        self.sleep(300)
        self.is_element_exist(300, task_upgrade["task_upgrade_button"])

    def reboot_node(self):
        """
        重启节点
        :return:
        """
        self.is_element_exist(1800, task_upgrade["reboot_node_button"])
        self.click_element_by_js(task_upgrade["reboot_node_button"])
        self.is_element_exist(30, task_upgrade["alert_node_confirm"])
        self.click(task_upgrade["alert_node_confirm"])
        self.is_element_exist(3600, task_upgrade["start_check_button"])
        self.refresh()

    def post_upgrade_check(self):
        """
        升级后环境巡检
        :return:
        """
        self.is_element_exist(1800, task_upgrade["start_check_button"])
        self.sleep(1)
        self.click_element_by_js(task_upgrade["start_check_button"])
        self.is_element_exist(1800, task_upgrade["clean_up_button"])

    def rollback_node(self):
        """
        回退节点
        :return:
        """
        self.is_element_exist(1800, task_upgrade["roll_back_button"])
        self.sleep(2)
        self.click(task_upgrade["roll_back_button"])
        self.is_element_exist(30, task_upgrade["alert_node_confirm"])
        self.click(task_upgrade["alert_node_confirm"])
        self.is_element_exist(4800, task_upgrade["reboot_node_button"])
        self.refresh()

    def rollback_reboot_node(self):
        """
        回退后重启节点
        :return:
        """
        self.is_element_exist(1800, task_upgrade["reboot_node_button"])
        self.click_element_by_js(task_upgrade["reboot_node_button"])
        self.is_element_exist(30, task_upgrade["alert_node_confirm"])
        self.click(task_upgrade["alert_node_confirm"])
        self.is_element_exist(3600, task_upgrade["task_upgrade_button"])
        self.refresh()

    def del_node(self):
        """
        删除节点
        :return:
        """
        if self.is_element_exist(5, task_upgrade["delete_button"]):
            self.click(task_upgrade["delete_button"])
            self.click(task_upgrade["alert_node_confirm"])
        elif self.is_element_exist(5, task_upgrade["cancel_button"]):
            self.click(task_upgrade["cancel_button"])
            self.click(task_upgrade["alert_task_confirm"])
            log.info("节点不存在，无需删除 !")
        else:
            log.error("删除按钮不存在，删除节点失败 !")
