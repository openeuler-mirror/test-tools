# -*-coding:utf-8-*-

from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *
from Aops_Web_Auto_Test.page_object.base_page import WebPage

asset = Element('host_list')


class TestRepo:
    def test_set_repo(self, drivers):
        repo = WebPage(drivers)
        repo.click_element(asset['host_list'])
        repo.click_element(asset['host_list'])
        repo_text = '''[aops-update]
    name=update
    baseurl=https:\/\/repo.openeuler.org\/openEuler-22.03-LTS\/OS\/$basearch
    enabled=1
    gpgcheck=1
    gpgkey=https:\/\/repo.openeuler.org\/openEuler-22.03-LTS\/OS/$basearch\/RPM-GPG-KEY-openEuler'''
        repo.click_element(asset['add_repo'])
        repo.input_text(asset['add_repo_name'], "20.03-LTS-SP1")
        data_input = repo.find_element(asset['add_repo_data'])
        repo.driver.execute_script("arguments[0].value='"+ repo_text +"';", data_input);
        repo.click_element(asset['determine'])