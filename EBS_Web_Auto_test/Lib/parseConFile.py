# -*- coding: utf-8 -*-
"""
@Time ： 2023/5/8 0008 15:12
@Auth ： ysc
@File ：parseConFile.py
@IDE ：PyCharm
"""
import json
from Config.config import CONF_PATH


def load_config(file: str):
    """
    加载配置文件
    """
    with open(file, 'r') as f:
        config_file = json.load(f)
    return config_file


class ReadConfig:
    def __init__(self, file):
        """
        初始化配置类
        """
        config_list = load_config(file)
        self.BASIC_URL = config_list['basic_url']
        self.NAME = config_list['user_name']
        self.PASSWORD = config_list['password']
        self.REPO_ARM = config_list['repo_arm']
        self.REPO_X86 = config_list['repo_x86']
        self.kernel_param = config_list['kernel_param']


if __name__ == '__main__':
    config = ReadConfig(CONF_PATH)
    print(config.BASIC_URL)
    print(config.NAME)
    print(config.PASSWORD)

