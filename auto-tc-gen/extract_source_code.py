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
import copy
import subprocess
from logger import log
import re
from help_parse import parse_usage_parameter, get_parameters_type, store_test_case
from python_parse.PyArgExtractor import PyArgExtractor

def extract_help_code(file_name, log_file):
    """  提取 help 信息  """
    """
        打印每个目录下需要提取源码的文件

        Args:
            file_name ([string]): [命令名称]
            log_file ([string]): [日志打印目录]

        Returns:
            [string]: 帮助信息
    """
    sub_res = ""
    try:
        # 排除掉执行 getstatusoutput 超时的命令
        sub_res = subprocess.run(file_name + " -h", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=2)
        # 当 status = 1 但是返回值包含 usage 时，当做正常处理
        sub_status1, sub_res1 = subprocess.getstatusoutput(file_name + " -h")
        # 将 Format is 、 SYNOPSIS  等语义相同的语句替换成 usage：
        sub_res1 = replace_same_word(sub_res1)
        if re.search("usage:", sub_res1, re.I) is not None:
            return sub_res1
        sub_status2, sub_res2 = subprocess.getstatusoutput(file_name + " --h")
        sub_res2 = replace_same_word(sub_res2)
        if re.search("usage:", sub_res2, re.I) is not None:
            return sub_res2
        sub_status3, sub_res3 = subprocess.getstatusoutput(file_name + " --help")
        sub_res3 = replace_same_word(sub_res3)
        if re.search("usage:", sub_res3, re.I) is not None:
            return sub_res3
        if sub_status1 * sub_status2 * sub_status3 != 0:
            log.warning("命令 " + file_name + "不存在--help/-h等命令，无法获取其帮助信息", log_file)
            return " "
        log.warning("命令 " + file_name + "存在--help/-h等命令，但帮助信息中不存在可用于解析的usage等关键词与命令的使用规则", log_file)
        return " "
    except UnicodeDecodeError:
        # 去掉 res 中的前置 b' 、 后置 ', 这里在使用split时需要转义，提前处理
        res = re.sub("b'", "", str(sub_res.stdout), 1, re.I).strip()
        res = res[0:len(res) - 1]
        res = res.replace("\\n", "\n")
        res = replace_same_word(res)
        if re.search("usage:", res, re.I) is not None:
            return res
        log.warning("命令 " + file_name + " 执行 --help 命令出错", log_file)
        return " "
    except subprocess.TimeoutExpired:
        log.warning("命令 " + file_name + " 执行 --help 命令超时", log_file)
        return " "


def replace_same_word(sub_res):
    """
        不存在 usage 的情况下， 将一些与 usage: 相同语义的词汇替换成 usage

        Args:
            sub_res ([string]): [源码存放前置目录]

        Returns:
            [string]: 命令源码目录
    """
    if re.search("usage:", sub_res, re.I) is None:
        sub_res = re.sub("Format is:", "usage:", sub_res, 1, re.I).strip()
        sub_res = re.sub("SYNOPSIS", "usage:", sub_res, 1, re.I).strip()
        sub_res = re.sub("usage is:", "usage:", sub_res, 1, re.I).strip()
    return sub_res


# 函数入口
def extract_source_code(build_dir, log_file):
    """
        提取命令的有效源码

        Args:
            build_dir (string): [build目录]
            log_file ([string]): [日志打印目录]
    """
    log.info("第六步：提取有效源码", log_file)
    file_name_list = []
    file_path_list = []
    if os.path.exists(f"{build_dir}usr/bin/"):
        sub_status, sub_res = subprocess.getstatusoutput(f"ls {build_dir}usr/bin/")
        for name in sub_res.split("\n"):
            file_name_list.append(name)
            file_path_list.append(f"{build_dir}usr/bin/")
    if os.path.exists(f"{build_dir}usr/sbin/"):
        sub_status, sub_res = subprocess.getstatusoutput(f"ls {build_dir}usr/sbin/")
        for name in sub_res.split("\n"):
            file_name_list.append(name)
            file_path_list.append(f"{build_dir}usr/sbin/")

    # 提取目录下所有文件的源码的有效部分
    for i in range(0, len(file_name_list)-1):
        file_name = file_name_list[i]
        file_path = file_path_list[i]
        sub_status, sub_res = subprocess.getstatusoutput("file " + file_path + "" + file_name)
        content = ""
        if sub_res.__contains__("shell script") or sub_res.__contains__("sh script"):
            # 源码为 shell 类型的命令暂通过帮助信息解析的方式完成解析，故此处不做处理
            file_type = "shell"
        elif sub_res.__contains__("Python script"):
            file_type = "Python"
            try:
                pyextractor = PyArgExtractor([file_path + "" + file_name], file_path)
                content, commands, value_map, help_map = pyextractor.get_cmds_args()
            except Exception as e:
                # 由于python的源码解析中存在大量尝试性的调用与模拟调用过程，
                # 由于在模拟的过程中缺少运行环境，正常情况下也会出现很多方法调用失败的异常，不做额外的打印处理。
                commands = []
            if len(commands) == 0:
                log.warning("命令 " + file_name + "使用python源码解析失败，改用帮助信息解析的方式重新进行解析", log_file)
            else:
                log.info("命令 " + file_name + "使用python源码解析成功", log_file)
                # todo 源码解析、参数赋值、脚本生成代码，后续提交的pr中开启
                # # 根据参数类型，获取并且填入参数值
                # commands_back = copy.deepcopy(commands)
                # get_parameters_type.get_parameters_type(commands, commands_back)
                # # 生成与存储pre测试用例
                # store_test_case.store_pre_case(commands_back, file_path, file_name)
                # # 生成与存储run测试用例
                # file_path = store_test_case.store_run_case(commands, file_path, file_name)
                # # 生成与存储post测试用例
                # store_test_case.store_post_case(commands_back, file_path, file_name)
                # # 将 pre、run、post写入一个脚本文件中
                # store_test_case.store_file(file_path, file_name, content, commands_back)
                continue
        elif sub_res.__contains__("Perl script"):
            file_type = "Perl"
            #  Perl类型暂时无法使用源码解析的方式进行处理，使用使用帮助信息解析的方式进行处理
        else:
            file_type = "二进制"
            #  二进制文件暂时无法使用源码解析的方式进行处理，使用使用帮助信息解析的方式进行处理
        # 提取 help 信息, 使用帮助信息解析的方式进行解析
        content = extract_help_code(file_name, log_file)
        if len(content) == 0 or content.isspace():
            continue
        else:
            log.info("命令 " + file_name + "，文件类型 " + file_type + " 获取帮助信息成功", log_file)
        # todo 源码解析、参数赋值、脚本生成代码，后续提交的pr中开启
        # # 解析参数
        # res_multiple_list, res_multiple_back_list = parse_usage_parameter.parse_usage_parameters(content, file_name)
        # # 生成与存储pre测试用例
        # store_test_case.store_pre_case(res_multiple_back_list, file_path, file_name)
        # # 生成与存储run测试用例
        # file_path = store_test_case.store_run_case(res_multiple_list, file_path, file_name)
        # # 生成与存储post测试用例
        # store_test_case.store_post_case(res_multiple_back_list, file_path, file_name)
        # # 将 pre、run、post写入一个脚本文件中
        # store_test_case.store_file(file_path, file_name, content, res_multiple_back_list)
