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
# @Date      	:   2023-6-23 12:00:00
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   保存测试用例
#####################################

#coding=UTF-8

import subprocess, os, datetime
import configparser
from help_parse import parameter_classify
from logger import log


current_dir = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read('./config.ini')
scr_dir = config.get('Directories', 'scr_dir', fallback=current_dir)
scr_dir = os.path.abspath(scr_dir) + "/"

def get_test_command(full_test_command, para_type='pre'):
    """
        获取 pre_test 测试命令

        Args:
            full_test_command ([list]): [参数命令]
            para_type (str): 参数类型

        Returns:
            [list]: para_type类型的参数信息
    """
    type_list = parameter_classify.get_all_para_type(full_test_command)
    pre_list, post_list = parameter_classify.get_all_pre_post(type_list)
    if para_type == 'pre':
        return pre_list
    else:
        return post_list


def get_run_test_command(full_test_command):
    """
        获取 run_test 测试命令

        Args:
            full_test_command ([list]): [参数命令]

        Returns:
            [list]: run信息
    """
    run_test_command = full_test_command
    return run_test_command


def store_list_to_file(test_command, file_path, file_name):
    """
        存储测试文件到本地

        Args:
            test_command ([list]): [测试用例]
            file_path ([string]): [存储路径]
            file_name ([string]): [文件名]

        Returns:
            [string]: 存储路径
    """
    file_object = open(file_path + file_name, 'w')
    # 去空
    test_command = [x for x in test_command if x]
    for command in test_command:
        str_line = ""
        for d in command:
            str_line = str_line + " " + d
        if len(str_line.strip()) == 0:
            continue
        file_object.write(str_line.strip())
        file_object.write('\n')
    file_object.close()
    return file_path

def print_format(post_test_command):
    """
        将测试用例转换成统一的打印格式

        Args:
            post_test_command ([list]): [测试用例]

        Returns:
            [list]: 处理后的测试用例
    """
    res_list = []
    for command in post_test_command:
        for d in command:
            res_list.append([d])
    return res_list


def store_case(full_test_command, package, name, param_type='pre'):
    """
        存储post测试用例

        Args:
            full_test_command ([list]): [测试用例]
            package ([string]): [软件包名称]
            name ([string]): [命令名称]
            param_type(str): 类型参数

        Returns:
            [string]: 存储路径
    """
    # 若没有需要测试的命令，直接返回
    if len(full_test_command) == 0:
        return
    # 文件存储位置,文件名称, 文件名称可由测试命令的前缀获得
    if param_type=='pre':
        file_name = "pre_test.txt"
    else:
        file_name = "post_test.txt"
    file_path = scr_dir + package + "/" + name + "/"
    os.makedirs(file_path, exist_ok=True)
    # 获取 post_test或 pre_test 测试命令
    if param_type=='pre':
        test_command = get_test_command(full_test_command, 'pre')
    else:
        test_command = get_test_command(full_test_command, 'post')
    # 转换成统一的打印格式
    test_command = print_format(test_command)
    # 存储到本地文件中
    file_path = store_list_to_file(test_command, file_path, file_name)
    return file_path


def store_run_case(full_test_command, package, name):
    """
        存储run测试用例

        Args:
            full_test_command ([list]): [测试用例]
            package ([string]): [软件包名称]
            name ([string]): [命令名称]

        Returns:
            [string]: 存储路径
    """
    # 若没有需要测试的命令，直接返回
    if len(full_test_command) == 0:
        return
    # 文件存储位置,文件名称, 文件名称可由测试命令的前缀获得
    file_name = "run_test.txt"
    file_path = scr_dir + package + "/" + name + "/"
    os.makedirs(file_path, exist_ok=True)
    # 获取 run_test 测试命令
    run_test_command = get_run_test_command(full_test_command)
    # 存储到本地文件中
    file_path = store_list_to_file(run_test_command, file_path, file_name)
    return file_path



def store_file(package, file_name, content, res_multiple_back_list, log_file):
    """
        将 pre、run、post写入一个脚本文件中

        Args:
            package ([string]): [软件包名称]
            file_name ([string]): [文件名称]
            content ([string]): [测试用例]
            res_multiple_back_list ([list]): [参数命令]
    """
    if package is None or len(package) == 0:
        return
    file_path = scr_dir + package + "/" + file_name + "/"
    os.makedirs(file_path, exist_ok=True)
    pre_file = "#!/usr/bin/bash\n\n" \
               "# Copyright (c) 2023. Huawei Technologies Co.,Ltd.ALL rights reserved.\n" \
               "# This program is licensed under Mulan PSL v2.\n" \
               "# You can use it according to the terms and conditions of the Mulan PSL v2.\n" \
               "#          http://license.coscl.org.cn/MulanPSL2\n" \
               "# THIS PROGRAM IS PROVIDED ON AN \"AS IS\" BASIS, WITHOUT WARRANTIES OF ANY KIND,\n" \
               "# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,\n" \
               "# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.\n" \
               "# See the Mulan PSL v2 for more details.\n"
    author = config.get('section', 'author')
    contact = config.get('section', 'contact')
    date = "# @Date      :   " + "" + str(datetime.date.today())
    licenses = config.get('section', 'licenses')
    desc = "# @Desc      :   Test " + file_name + " command"
    source = config.get('section', 'source')
    file_object = open(file_path + "oe_test_" + file_name + ".sh", 'w')
    # 写入开头注释部分
    file_object.write(pre_file + "\n")
    file_object.write("###################################" + "\n")
    file_object.write(author + "\n")
    file_object.write(contact + "\n")
    file_object.write(date + "\n")
    file_object.write(licenses + "\n")
    file_object.write(desc + "\n")
    file_object.write("###################################" + "\n" + "\n")
    file_object.write(source + "\n" + "\n")

    # 写入pre文件
    log_info = "    LOG_INFO \"Start to prepare the test environment.\""
    file_object.write("function pre_test() {" + "\n")
    file_object.write(log_info + "\n")
    # 读取pre文件并且写入
    with open(file_path + "" + "pre_test.txt", 'r') as f:
        for line in f.readlines():
            file_object.write("    " + line.rstrip() + "\n")
    log_info = "    LOG_INFO \"End to prepare the test environment.\""
    file_object.write(log_info + "\n")
    file_object.write("}" + "\n")

    # 写入--help帮助信息
    file_object.write("##########################################################" + "\n")
    for d in str(content).split("\n"):
        d = "#" + d
        file_object.write(d + "\n")
    file_object.write("\n")
    file_object.write("##########################################################" + "\n")

    # 写入run文件
    file_object.write("function run_test() {" + "\n")
    log_info = "    LOG_INFO \"Start to run test.\""
    file_object.write(log_info + "\n")
    #  读取run文件写入
    with open(file_path + "" + "run_test.txt", 'r') as f:
        temp = 0
        for line in f.readlines():
            file_object.write("    # " + ' '.join(res_multiple_back_list[temp]) + "\n")
            file_object.write("    " + line.rstrip() + "\n")
            file_object.write(
                "    CHECK_RESULT $? 0 0 \"" + ' '.join(res_multiple_back_list[temp]) + "\"" + "\n")
            temp = temp + 1
    log_info = "    LOG_INFO \"End to run test.\""
    file_object.write(log_info + "\n")
    file_object.write("}" + "\n")

    # 写入post文件
    log_info = "function post_test() {\n    LOG_INFO \"Start to restore the test environment.\""
    file_object.write(log_info + "\n")
    # 读取post文件写入
    with open(file_path + "" + "post_test.txt", 'r') as f:
        for line in f.readlines():
            file_object.write("    " + line.rstrip() + "\n")
    log_info = "    LOG_INFO \"End to restore the test environment.\"\n}\n\nmain \"$@\""
    file_object.write(log_info + "\n")
    file_object.close()

    print("用例存放路径：" + file_path + "oe_test_" + file_name + ".sh")