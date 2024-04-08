# -*-coding:utf-8-*-
import pytest
import re
import os
import pandas as pd

from Aops_Web_Auto_Test.page_object.asset_magt import AssetMagtPage
from Aops_Web_Auto_Test.page_object.cve_magt import HoleMagtPage
from Aops_Web_Auto_Test.utils.times import *


class TestHoleMagt:
    def test_set_up_repo_nohost(self, drivers):
        """设置REPO"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_no_host('nohost', '22.03-LTS')
        sleep(2)
        hole.view_task()
        assert "REPO设置任务nohost" in hole.get_source
        hole.delete_task()

    def test_set_up_repo_onehost(self, drivers):
        """设置REPO"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        sleep(6)
        hole.view_task()
        assert "REPO设置任务onehost" in hole.get_source
        assert "为以下1个主机设置Repo" in hole.get_source
        hole.delete_task()

    def test_set_up_repo_morehost(self, drivers):
        """设置REPO"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_more_host('morehost', '22.03-LTS')
        sleep(6)
        hole.view_task()
        sleep(3)
        assert "REPO设置任务morehost" not in hole.get_source

    def test_hole_scan(self, drivers):
        """漏洞扫描"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        hole.hole_scan_no_host()
        sleep(12)
        scan_time = dt_strftime('%Y-%m-%d')
        scan_num = re.search("[0-9]/[1-9]", hole.get_source)
        print(scan_time, scan_num, type(scan_num))
        assert scan_time in hole.get_source
        assert "None" not in str(scan_num)
        sleep(2)
        hole.view_task()
        sleep(2)
        hole.delete_task()

    def test_export_hole_scan_nohost(self, drivers):
        """导出 nohost"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        hole.hole_scan_no_host()
        sleep(12)
        hole.export_hole_scan_no_host()
        assert "请至少选择一组主机" in hole.get_source
        sleep(2)
        hole.view_task()
        sleep(2)
        hole.delete_task()

    def test_export_hole_scan_onehost(self, drivers):
        """导出 onehost"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        hole.export_hole_scan_one_host()
        sleep(12)
        file_cve = pd.read_csv('/data/BlueCloud/host/liujingjing/下载/host1.csv')
        os.remove('/data/BlueCloud/host/liujingjing/下载/host1.csv')
        print(str(file_cve))
        assert "cve_id" in str(file_cve)
        assert "status" in str(file_cve)
        assert "fix_status" in str(file_cve)
        assert "support_hp" in str(file_cve)
        assert "fixed_by_hp" in str(file_cve)
        sleep(2)
        hole.view_task()
        sleep(2)
        hole.delete_task()
        sleep(2)

    def test_cve_repair_nocve(self, drivers):
        """修复no cve"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        sleep(5)
        hole.hole_scan_no_host()
        sleep(12)
        hole.enter_cves_page()
        hole.create_cve_task_nocve('nocve')
        sleep(2)
        hole.view_task()
        sleep(2)
        assert "CVE修复任务nocve" in hole.get_source
        hole.view_nocve()
        assert "待修复" in hole.get_source
        hole.view_task()
        sleep(2)
        hole.delete_task()

    def test_cve_repair_onecve(self, drivers):
        """修复 one cve"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        sleep(5)
        hole.hole_scan_no_host()
        sleep(12)
        hole.enter_cves_page()
        hole.create_cve_task_onecve('onecve')
        sleep(2)
        hole.view_task()
        sleep(2)
        assert "CVE修复任务onecve" in hole.get_source
        hole.view_onecve()
        assert "待修复" not in hole.get_source
        hole.view_task()
        sleep(2)
        hole.delete_task()

    def test_cve_repair_morecve(self, drivers):
        """修复 more cve"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        sleep(5)
        hole.hole_scan_no_host()
        sleep(12)
        hole.enter_cves_page()
        hole.create_cve_task_morecve('morecve')
        sleep(2)
        hole.view_task()
        sleep(2)
        assert "CVE修复任务morecve" not in hole.get_source

    def test_host_cve_repair_nocve(self, drivers):
        """修复 host no cve"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        sleep(2)
        hole.hole_scan_no_host()
        sleep(12)
        hole.view_host1()
        hole.create_cve_task_nocve('nocve')
        sleep(2)
        hole.view_task()
        sleep(2)
        assert "CVE修复任务nocve" in hole.get_source
        hole.view_nocve()
        assert "待修复" in hole.get_source
        hole.view_task()
        sleep(2)
        hole.delete_task()

    def test_host_cve_repair_onecve(self, drivers):
        """修复 host one cve"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        sleep(5)
        hole.hole_scan_no_host()
        sleep(12)
        hole.view_host1()
        hole.create_cve_task_onecve('onecve')
        sleep(2)
        hole.view_task()
        sleep(2)
        assert "CVE修复任务onecve" in hole.get_source
        hole.view_onecve()
        assert "待修复" not in hole.get_source
        hole.view_task()
        sleep(2)
        hole.delete_task()

    def test_host_cve_repair_morecve(self, drivers):
        """修复 host more cve"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        sleep(5)
        hole.hole_scan_no_host()
        sleep(12)
        hole.view_host1()
        hole.create_cve_task_morecve('morecve')
        sleep(2)
        hole.view_task()
        sleep(2)
        assert "CVE修复任务morecve" not in hole.get_source
        sleep(2)
        hole.delete_task()
        sleep(2)
        host = AssetMagtPage(drivers)
        host.enter_host_magt_page()
        sleep(3)
        hole.delete_host()
        sleep(3)
        hole.enter_hole_magt_page()
        sleep(3)
        hole.enter_host_list_page()
        sleep(3)
        hole.delete_repo()
        sleep(3)
        host.enter_host_group_magt_page()
        sleep(3)
        hole.delete_host_group()


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_list/test_cve_repair_task.py', '-vs'])
