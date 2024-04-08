# -*-coding:utf-8-*-
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *

base_page = Element('common')
asset = Element('host_list')


class HoleMagtPage(WebPage):
    def enter_hole_magt_page(self):
        """进入主机列表页面"""
        self.click_element(asset['host_list'])
        sleep(5)

    def enter_host_list_page(self):
        self.click_element(asset['host_list'])
        sleep(5)

    def enter_cves_page(self):
        self.click_element(asset['cves'])
        sleep(5)

    def add_repo(self, reponame, filename):
        """添加REPO"""
        self.click_element(asset['add_repo'])
        sleep(3)
        self.input_text(asset['add_repo_name'], reponame)
        sleep(3)
        self.upload_file(filename)
        sleep(5)
        self.click_element(base_page['confirm'])
        sleep(5)

    def setup_repo_no_host(self, taskname, reponame):
        """设置REPO no host"""
        self.click_element(asset['setup_repo'])
        sleep(3)
        self.input_text(asset['task_name'], taskname)
        self.select_value_by_dropdown(reponame)
        sleep(3)
        self.click_element(asset['create_repo'])
        sleep(3)
        self.click_element(asset['close'])
        sleep(3)

    def setup_repo_one_host(self, taskname, reponame):
        """设置REPO one host"""
        self.click_element(asset['checkbox_1'])
        self.click_element(asset['setup_repo'])
        sleep(3)
        self.input_text(asset['task_name'], taskname)
        self.select_value_by_dropdown(reponame)
        sleep(3)
        self.click_element(asset['execute_immediately'])
        sleep(2)
        self.click_element(asset['close'])
        sleep(3)

    def setup_repo_more_host(self, taskname, reponame):
        """设置REPO more host"""
        self.click_element(asset['checkbox_1'])
        self.click_element(asset['checkbox_2'])
        self.click_element(asset['setup_repo'])
        sleep(3)
        self.input_text(asset['task_name'], taskname)
        self.select_value_by_dropdown(reponame)
        sleep(3)
        self.click_element(base_page['cancel'])

    def hole_scan_no_host(self):
        """漏洞扫描 no host"""
        self.click_element(asset['hole_scan'])
        sleep(5)
        self.click_element(base_page['confirm'])
        sleep(3)

    def export_hole_scan_no_host(self):
        """导出no host"""
        self.click_element(asset['export'])
        sleep(1)

    def export_hole_scan_one_host(self):
        """导出one host"""
        self.click_element(asset['host_name'])
        sleep(5)
        self.click_element(asset['export_cve_info'])
        sleep(5)

    def create_cve_task_nocve(self, taskname):
        """生成修复任务　no cve"""
        self.click_element(asset['create_repair_task'])
        sleep(3)
        self.input_text(asset['task_name'], taskname)
        sleep(3)
        self.click_element(asset['create_repo'])
        sleep(3)
        self.click_element(asset['close'])
        sleep(3)

    def create_cve_task_onecve(self, taskname):
        """生成修复任务　one cve"""
        self.click_element(asset['checkbox_1'])
        self.click_element(asset['create_repair_task'])
        sleep(3)
        self.input_text(asset['task_name'], taskname)
        sleep(3)
        self.click_element(asset['execute_immediately'])
        sleep(3)
        self.click_element(asset['close'])
        sleep(3)

    def create_cve_task_morecve(self, taskname):
        """生成修复任务　one cve"""
        self.click_element(asset['checkbox_1'])
        self.click_element(asset['checkbox_2'])
        self.click_element(asset['create_repair_task'])
        sleep(3)
        self.input_text(asset['task_name'], taskname)
        sleep(3)
        self.click_element(base_page['cancel'])
        sleep(3)

    def view_nocve(self):
        """生成修复任务　no cve"""
        self.click_element(asset['no_cve'])
        sleep(3)

    def view_onecve(self):
        """生成修复任务　no cve"""
        self.click_element(asset['one_cve'])
        sleep(3)

    def view_host1(self):
        """生成修复任务　no cve"""
        self.click_element(asset['host_name'])
        sleep(3)

    def view_task(self):
        """查看task页面"""
        self.click_element(asset['task'])
        self.click_element(asset['task_page'])

    def delete_task(self):
        """删除task"""
        self.click_element(asset['delete_task'])
        self.click_element(asset['batch_delete_task'])
        sleep(3)
        self.click_element(base_page['confirm'])
        sleep(5)

    def delete_host(self):
        """删除host"""
        self.click_element(asset['delete_task'])
        sleep(3)
        self.click_element(base_page['batch_delete'])
        sleep(3)
        self.click_element(base_page['delete'])
        sleep(5)

    def delete_host_group(self):
        """删除host group"""
        self.click_element(asset['delete_task'])
        sleep(3)
        self.click_element(base_page['batch_delete'])
        sleep(3)
        self.click_element(base_page['delete'])
        sleep(5)

    def delete_repo(self):
        """删除repo"""
        self.click_element(asset['repo_delete2'])
        sleep(3)
        self.click_element(base_page['delete'])
        sleep(5)
