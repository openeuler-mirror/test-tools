# -*-coding:utf-8-*-
import pytest
from Aops_Web_Auto_Test.page_object.cve_magt import HoleMagtPage
from Aops_Web_Auto_Test.utils.times import *


class TestSetRepo:
    def test_set_repo_01_nohost(self, drivers):
        """设置REPO"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_no_host('nohost', '22.03-LTS')
        sleep(2)
        hole.view_task()
        assert "REPO设置任务nohost" in hole.get_source
        hole.delete_task()

    def test_set_up_repo_02_onehost(self, drivers):
        """设置REPO"""
        hole = HoleMagtPage(drivers)
        hole.enter_host_list_page()
        hole.setup_repo_one_host('onehost', '22.03-LTS')
        sleep(6)
        hole.view_task()
        assert "REPO设置任务onehost" in hole.get_source
        assert "为以下1个主机设置Repo" in hole.get_source
        hole.delete_task()


if __name__ == '__main__':
    pytest.main(['Aops_Web_Auto_Test/test_case/host_list/test_cve_repair_task.py', '-vs'])
