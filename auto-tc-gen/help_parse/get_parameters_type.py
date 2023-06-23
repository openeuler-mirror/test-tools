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
# @Desc      	:   获取参数类型
#####################################

#coding=UTF-8

import re
from help_parse import parse_options_parameters, parameter_classify


def get_default_value(usage_list, usage_back_list):
    """
       分隔参数值，根据参数类型获取参数并赋值

        Args:
            usage_list ([list]): [usage信息]
            usage_back_list ([list]): [usage信息备份]
    """
    for i in range(1, len(usage_list)):
        value = str(usage_list[i]).strip()
        # 如果是第一个参数，但不是特殊符号开头的，默认是子命令，不会映射到具体值，保留原样在最终命令中
        if i == 1 and re.match(r"^(\(-.*)|^(\[-.*)|^(<-.*)|^(-.*)", value, re.I) is None:
            continue
        # 后续参数以特殊符号开头的同样保留在最终命令中
        if re.match(r"^(\(-.*)|^(\[-.*)|^(<-.*)|^(-.*)", value, re.I) is not None:
            continue
        # 其他的内容全部替换为对应的取值；根据在config.ini中定义过的名称去判断
        else:
            # 去括号
            value = remove_outer_bracket(value)
            # 有多个值可选时，选一个
            value = choose_first_para(value)
            # 有多个变量时，分别赋值，如：<key>=[<value>]
            value_list = split_value(value)
            j = 0
            while j < len(value_list):
                if re.match(r"^(=)$|^( )$|^(:)$", value_list[j]):
                    j = j + 1
                    continue
                elif re.match(r"(.+=.+)|(.+:.+)|(.*\[.+].*)|(.*<.+>.*)", value_list[j]):
                    temp_list = split_value(value_list[j])
                    temp_list.reverse()
                    value_list.pop(j)
                    for m in range(0, len(temp_list)):
                        value_list.insert(j, temp_list[m])
                j = j + 1
            usage_back_list[i] = usage_list[i]
            # 赋值
            usage_list[i] = assign_usage(value_list)
    # 去空
    while '' in usage_list:
        usage_list.remove('')

def assign_usage(value_list):
    """
       参数赋值

        Args:
            value_list ([list]): [参数值]

        Returns:
            [list]: 赋值后测试用例
    """
    res = ""
    for i in range(0, len(value_list)):
        if re.match(r"^(=)$|^( )$|^(:)$|^$", value_list[i]):
            pass
        else:
            value_list[i] = parameter_classify.get_para_value(value_list[i])
        res = res + "" + value_list[i]
    return res

def split_value(value):
    """
       有多个变量时，分别赋值，如：<key>=[<value>]

        Args:
            value ([string]): [参数值]

        Returns:
            [list]: 参数值列表
    """
    value = value.replace(":]", "]:")
    value_list = []
    if value.__contains__(";"):
        value_list = value.split(";")
        i = 1
        while i < len(value_list):
            if i % 2 != 0:
                value_list.insert(i, ";")
            i = i + 1
    elif re.match(r"(.*key.*=.*value.*)", value, re.I) is not None:
        value_list.append("key")
        value_list.append("=")
        value_list.append("value")
    elif re.match(r"(.*key.*:.*value.*)", value, re.I) is not None:
        value_list.append("key")
        value_list.append(":")
        value_list.append("value")
    elif re.match(r"(\'.*\' \'.*\')", value, re.I) is not None:
        value_list = value.split("\' \'")
        value_list[0] = value_list[0][1:len(value_list[0])]
        value_list.insert(1, " ")
        value_list[2] = value_list[2][0:len(value_list[2]) - 1]
    elif re.match(r"(\[.+]:.+)", value, re.I) is not None:
        value_list = value.split("]:", 1)
        value_list[0] = value_list[0][1:len(value_list[0])]
        value_list.insert(1, ":")
    elif re.match(r"(<.+> <.+>)", value, re.I) is not None:
        value_list = value.split("> <", 1)
        value_list[0] = value_list[0][1:len(value_list[0])]
        value_list.insert(1, " ")
        value_list[2] = value_list[2][0:len(value_list[2]) - 1]
    elif re.match(r"(<.+>-<.+>)", value, re.I) is not None:
        value_list = value.split(">-<", 1)
        value_list[0] = value_list[0][1:len(value_list[0])]
        value_list.insert(1, " ")
        value_list[2] = value_list[2][0:len(value_list[2]) - 1]
    elif re.match(r"(.+<.+>\[.+])", value, re.I) is not None:
        value_list = re.split("[\[\]<>]", value)
    elif re.match(r"(.+ \[.+])|(.+\[.+])", value, re.I) is not None:
        value_list = re.split(r"\[| \[", value, 1)
        value_list.insert(1, " ")
        value_list[2] = value_list[2][0:len(value_list[2]) - 1]
    elif value.__contains__(":"):
        value_list = value.split(":")
        value_list.insert(1, ":")
    elif value.__contains__("="):
        value_list = value.split("=")
        value_list.insert(1, "=")
    else:
        value_list.append(value)
    while '' in value_list:
        value_list.remove('')
    return value_list

def choose_first_para(value):
    """
       有多个值可选时，选一个

        Args:
            value ([string]): [参数值]

        Returns:
            [string]: 参数值
    """
    if value.__contains__(","):
        value = value.strip().split(",")[0]
    elif value.__contains__(".."):
        value = value.strip().split("..")[0]
    elif value.__contains__("|"):
        value = value.strip().split("|")[0]
    elif value.__contains__("yn"):
        value = "y"
    elif value.__contains__("_or_"):
        value = value.strip().split("_or_")[0]
    elif re.match(r"^(\d*-)", value, re.I) is not None:
        value = value.strip().split("-")[0]
    elif value.__contains__("default"):
        value = " "
    return value

def remove_outer_bracket(s):
    """
       去掉最外层括号 () <> [] {} ""

        Args:
            s ([string]): [需要处理的字符串]

        Returns:
            [string]: 处理后的字符串
    """
    s = s.strip()
    if re.match(r"^(\(.*\))$|^(\[.*])$|^(\{.*})$|^(<.*>)$|^(\".*\")$", s, re.I) is not None:
        if parse_options_parameters.is_brackets_match([0, 0, 0, 0], s[1:len(s) - 1]):
            s = s[1:len(s) - 1]
    s = s.strip()
    if s.startswith(":"):
        s = s[1:len(s)]
    if s.startswith("{"):
        s = s[1:len(s)]
    if s.endswith(":"):
        s = s[0:len(s) - 1]
    if s.endswith("}"):
        s = s[0:len(s) - 1]
    if s.startswith("<"):
        s = s[1:len(s)]
    return s

def get_parameters_type(usage_multiple_list, usage_multiple_back_list):
    """
        处理参数格式，根据不同的参数类型，获取参数值
        函数入口

        Args:
            usage_multiple_list ([list]): [参数命令解析列表]
            usage_multiple_back_list ([list]): [参数命令解析列表备份]
    """
    # usage_multiple_back_list 用于备份赋值前的命令参数，便于pre、post查询使用
    for i in range(0, len(usage_multiple_list)):
        get_default_value(usage_multiple_list[i], usage_multiple_back_list[i])
