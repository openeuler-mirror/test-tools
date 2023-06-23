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
# @Desc      	:   参数分类
#####################################

#coding=UTF-8

import configparser
from my_class import type_class

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')
is_auto = config.get('Directories', 'is_auto')

# 参数映射表，根据参数名称获取参数类型
para_map_table = {}

# pre 映射表，根据参数类型获取pre
pre_map_table = {}

# 参数映射表，根据参数类型获取post
post_map_table = {}

# 类型名
string_type = "string"
file_type = "file"
int_type = "int"
fixed_type = "fixed"
path_type = "path"
url_type = "url"
branch_type = "branch"

def initialize_parameters():
    """
        初始化参数映射
    """
    value = ""
    # string 类型
    type_info = get_string_type()
    append_map(type_info.name_list, string_type)
    # 文件类型
    type_info = get_file_type()
    append_map(type_info.name_list, file_type)
    # path类型
    type_info = get_path_type()
    append_map(type_info.name_list, path_type)
    # url类型
    type_info = get_url_type()
    append_map(type_info.name_list, url_type)
    # branch类型
    type_info = get_branch_type()
    append_map(type_info.name_list, branch_type)
    # int 类型
    type_info = get_int_type()
    append_map(type_info.name_list, int_type)
    # 固定参数类型
    type_info = get_fixed_type()
    append_map(type_info.name_list, fixed_type)

def append_map(name_list, para_type):
    """
        添加映射关系

        Args:
            name_list ([list]): [参数名称]
            para_type ([list]): [参数类型]
    """
    for d in name_list:
        para_map_table[d] = para_type

def get_int_type():
    """
        int类型

        Returns:
            [type_info]: 类型对应信息
    """
    default_value = config.get('int', 'default_value')
    pre = config.get('int', 'pre').split('\n')
    post = config.get('int', 'post').split('\n')
    int_list = config.get('int', 'values').split(', ')
    type_info = type_class.TypeClass(default_value, pre, post, int_list)
    return type_info

def get_file_type():
    """
        文件类型

        Returns:
            [type_info]: 类型对应信息
    """
    default_value = config.get('file', 'default_value')
    pre = config.get('file', 'pre').split('\n')
    post = config.get('file', 'post').split('\n')
    file_list = config.get('file', 'values').split(', ')
    type_info = type_class.TypeClass(default_value, pre, post, file_list)
    return type_info

def get_fixed_type():
    """
        固定参数类型

        Returns:
            [type_info]: 类型对应信息
    """
    default_value = config.get('fixed', 'default_value')
    pre = config.get('fixed', 'pre').split('\n')
    post = config.get('fixed', 'post').split('\n')
    fixed_list = config.get('fixed', 'values').split(', ')
    fixed_list.append(" ")
    fixed_list.append(",")
    type_info = type_class.TypeClass(default_value, pre, post, fixed_list)
    return type_info

def get_path_type():
    """
        path类型

        Returns:
            [type_info]: 类型对应信息
    """
    default_value = config.get('path', 'default_value')
    pre = config.get('path', 'pre').split('\n')
    post = config.get('path', 'post').split('\n')
    path_list = config.get('path', 'values').split(', ')
    type_info = type_class.TypeClass(default_value, pre, post, path_list)
    return type_info

def get_url_type():
    """
        url类型

        Returns:
            [type_info]: 类型对应信息
    """
    default_value = config.get('url', 'default_value')
    pre = config.get('url', 'pre').split('\n')
    post = config.get('url', 'post').split('\n')
    url_list = config.get('url', 'values').split(', ')
    type_info = type_class.TypeClass(default_value, pre, post, url_list)
    return type_info

def get_branch_type():
    """
        branch类型

        Returns:
            [type_info]: 类型对应信息
    """
    default_value = config.get('branch', 'default_value')
    pre = config.get('branch', 'pre').split('\n')
    post = config.get('branch', 'post').split('\n')
    branch_list = config.get('branch', 'values').split(', ')

    type_info = type_class.TypeClass(default_value, pre, post, branch_list)
    return type_info

def get_string_type():
    """
        字符串类型

        Returns:
            [type_info]: 类型对应信息
    """
    default_value = config.get('string', 'default_value')
    pre = config.get('string', 'pre').split('\n')
    post = config.get('string', 'post').split('\n')
    string_list = config.get('string', 'values').split(', ')
    type_info = type_class.TypeClass(default_value, pre, post, string_list)
    return type_info

def get_all_para_type(res_multiple_list):
    """
        根据参数名称查询所有参数类型, 根据参数类型查询对应的 pre、post

        Args:
            res_multiple_list ([list]): [解析后的参数命令]

        Returns:
            [type_info]: 类型对应信息
    """
    type_list = []
    for res_list in res_multiple_list:
        for res in res_list:
            type_name = para_map_table.get(res)
            if type_name is not None:
                type_list.append(type_name)
    # 去重
    type_list = list(set(type_list))
    return type_list

def get_all_pre_post(type_list):
    """
        根据参数类型列表, 查询对应的 pre、post

        Args:
            type_list ([list]): [参数类型]

        Returns:
            [list]: pre信息
            [list]: post信息
    """
    pre_list = []
    post_list = []
    for type_name in type_list:
        if str(type_name).__eq__(string_type):
            type_info = get_string_type()
        elif str(type_name).__eq__(file_type):
            type_info = get_file_type()
        elif str(type_name).__eq__(int_type):
            type_info = get_int_type()
        elif str(type_name).__eq__(fixed_type):
            type_info = type_class.TypeClass("", [], [], [[]])
        elif str(type_name).__eq__(path_type):
            type_info = get_path_type()
        elif str(type_name).__eq__(url_type):
            type_info = get_url_type()
        elif str(type_name).__eq__(branch_type):
            type_info = get_branch_type()
        else:
            type_info = type_class.TypeClass("", [], [], [[]])
        pre = type_info.pre
        post = type_info.post
        if len(pre) != 0:
            pre_list.append(pre)
        if len(post) != 0:
            post_list.append(post)
    return pre_list, post_list

def get_para_value(value):
    """
        获取参数值
        函数入口

        Args:
            value ([string]): [参数]

        Returns:
            [string]: 参数默认值
    """
    type_name = para_map_table.get(value)
    if str(type_name).__eq__(string_type):
        type_info = get_string_type()
    elif str(type_name).__eq__(file_type):
        type_info = get_file_type()
    elif str(type_name).__eq__(int_type):
        type_info = get_int_type()
    elif str(type_name).__eq__(fixed_type):
        type_info = type_class.TypeClass(value, [], [], [[]])
    elif str(type_name).__eq__(path_type):
        type_info = get_path_type()
    elif str(type_name).__eq__(url_type):
        type_info = get_url_type()
    elif str(type_name).__eq__(branch_type):
        type_info = get_branch_type()
    else:
        # 未找到默认值
        if not is_auto.__eq__("y"):
            # 半自动的情况下，进入人工输入参数流程
            print("无法确认参数 " + value + " 对应的参数值，请人工输入参数值")
            value_temp = input()
            type_info = type_class.TypeClass(value_temp + "", [], [], [[]])
        else:
            type_info = type_class.TypeClass(value + "", [], [], [[]])

    default_value = type_info.default_value
    return default_value