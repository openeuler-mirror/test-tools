# -*- coding: utf-8 -*-
"""
@Time ： 2023/5/8 0008 9:47
@Auth ： ysc
@File ：run.py
@IDE ：PyCharm
"""
import unittest
from BeautifulReport import BeautifulReport
from Config.config import REPORT_DIR, HTML_NAME, PRO


if __name__ == '__main__':
    # 加载目录下所有用例模块
    case_path = "TestCase/smoke_test/Login"

    # start_dir是用例模块的路径，pattern是模块名
    discover = unittest.defaultTestLoader.discover(start_dir=case_path, pattern="test_case*.py")

    # 实例化一个运行器
    br = BeautifulReport(discover)
    br.report(filename=HTML_NAME, description="{}_测试报告".format(PRO), report_dir=REPORT_DIR, theme="theme_candy")
