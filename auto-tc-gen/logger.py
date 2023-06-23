# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
# @Author    	:   buchengjie
# @Contact   	:   mf21320006@smail.nju.edu.cn
# @Date      	:   2023-5-29 12:00:00
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   软件包编译
#####################################

#coding=UTF-8

import os
import logging

class MyLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def create_directory(self, file_path):
        """
        根据文件路径创建目录

        Args:
            file_path (str): 文件路径
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def info(self, message, file_path):
        """
        输出 INFO 级别的日志消息到指定文件

        Args:
            message (str): 日志消息
            file_path (str): 日志文件路径
        """
        self.create_directory(file_path)
        with open(file_path, 'a') as file:
            file_handler = logging.StreamHandler(file)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            self.logger.info(message)
            self.logger.removeHandler(file_handler)

    def debug(self, message, file_path):
        """
        输出 ERROR 级别的日志消息到指定文件

        Args:
            message (str): 日志消息
            file_path (str): 日志文件路径
        """
        self.create_directory(file_path)
        with open(file_path, 'a') as file:
            file_handler = logging.StreamHandler(file)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            self.logger.debug(message)
            self.logger.removeHandler(file_handler)

    def warning(self, message, file_path):
        """
        输出 WARNING 级别的日志消息到指定文件

        Args:
            message (str): 日志消息
            file_path (str): 日志文件路径
        """
        self.create_directory(file_path)
        with open(file_path, 'a') as file:
            file_handler = logging.StreamHandler(file)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            self.logger.warning(message)
            self.logger.removeHandler(file_handler)

    def error(self, message, file_path):
        """
        输出 ERROR 级别的日志消息到指定文件

        Args:
            message (str): 日志消息
            file_path (str): 日志文件路径
        """
        self.create_directory(file_path)
        with open(file_path, 'a') as file:
            file_handler = logging.StreamHandler(file)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            self.logger.error(message)
            self.logger.removeHandler(file_handler)


log = MyLogger()

# 用法
if __name__ == '__main__':
    log.info("This is an info message", "/root/to/log.txt")
    log.warning("This is a warning message", "/root/to/log.txt")
    log.error("This is an error message", "/root/to/log.txt")
