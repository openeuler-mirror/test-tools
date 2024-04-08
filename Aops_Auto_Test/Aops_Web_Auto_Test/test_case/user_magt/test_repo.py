# -*-coding:utf-8-*-
import logging
import math

import pandas
import openpyxl

import pytest
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.page_object.base_page import WebPage
from Aops_Web_Auto_Test.common.readelement import Element
from Aops_Web_Auto_Test.utils.times import *
from selenium import webdriver
from selenium.webdriver.support.select import Select
from Aops_Web_Auto_Test.page_object.base_page import WebPage


asset = Element('host_list')


class TestRepo:
    def test_set_repo(self,drivers):
        repo = WebPage(drivers)
        repo.click_element(asset['host_list'])
        sleep(3)
        repo.click_element(asset['host_list'])
        repo_text = '''[aops-update]
    name=update
    baseurl=https:\/\/repo.openeuler.org\/openEuler-22.03-LTS\/OS\/$basearch
    enabled=1
    gpgcheck=1
    gpgkey=https:\/\/repo.openeuler.org\/openEuler-22.03-LTS\/OS/$basearch\/RPM-GPG-KEY-openEuler'''
        sleep(3)
        repo.click_element(asset['add_repo'])
        sleep(3)
        repo.input_text(asset['add_repo_name'], "20.03-LTS-SP1")
        # repo.execute_script("arguments[0].click();", ele)
        data_input = repo.find_element(asset['add_repo_data'])
        repo.driver.execute_script("arguments[0].value='"+ repo_text +"';", data_input);
        # repo.input_text(asset['add_repo_data'], repo_text)
        sleep(10)
        repo.click_element(asset['determine'])
    #
    # def add_repo(self, reponame, repodata):
    #     """添加REPO"""
    #     self.click_element(asset['add_repo'])
    #     sleep(3)
    #     self.input_text(asset['add_repo_name'], reponame)
    #     self.input_text(asset['add_repo_data'], repodata)
    #     sleep(10)
    #     self.click_element(asset['determine'])
    #
    # def setup_repo_no_host(self, reponame):
    #     """设置REPO"""
    #     self.click_element(asset['setup_repo'])
    #     sleep(3)
    #     self.select_value_by_dropdown(reponame)
    #     sleep(3)
    #     self.click_element(asset['create_repo'])