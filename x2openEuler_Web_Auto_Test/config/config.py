"""
@Time : 2024/7/27 10:23
@Auth : ysc
@File : config.py
@IDE  : PyCharm
"""
import os
import sys
from selenium.webdriver.common.by import By
from common.parse_yaml import Yaml

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELEMENT_PATH = os.path.join(ROOT_DIR, 'page_element')
Error_CODE = 519

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_PATH)
sys.path.append("/usr/local/Python-3.8.12/lib/python3.8/site-packages")

# 元素定位的类型
LOCATE_MODE = {
    'css': By.CSS_SELECTOR,
    'xpath': By.XPATH,
    'name': By.NAME,
    'id': By.ID,
    'class': By.CLASS_NAME
}

# 定义conf.yml文件路径
_config_file = os.path.join(ROOT_DIR, 'config', 'config.yaml')

# 定义test_data文件路径
data_path = os.path.join(ROOT_DIR, 'test_case')


def get_config():
    return Yaml(_config_file).data()


def get_test_config(test_config_yaml):
    """
    测试数据
    :param test_config_yaml: 测试数据存放路径
    :return:
    """
    return Yaml(test_config_yaml).data()

