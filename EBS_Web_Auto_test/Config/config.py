# -*- coding: utf-8 -*-
import time
import os

# 项目名称
PRO = "EulerMaker"

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 页面元素目录
ELEMENT_PATH = os.path.join(ROOT_DIR, 'page_element')
# 报告目录
REPORT_DIR = os.path.join(ROOT_DIR, 'Report')
if not os.path.exists(REPORT_DIR): os.mkdir(REPORT_DIR)
# ui对象库config.json文件所在目录
CONF_PATH = os.path.join(ROOT_DIR, 'Config', 'config.json')
# 当前时间
CURRENT_TIME = time.asctime(time.localtime(time.time()))
REPORT_TIME = time.strftime('%Y-%m-%d-%Hh-%Mm-%Ss', time.localtime())

# 报告名称
HTML_NAME = '{}_Test_Report_{}.html'.format(PRO, REPORT_TIME)
# print(HTML_NAME)

