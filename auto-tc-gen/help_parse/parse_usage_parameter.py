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
# @Desc      	:   解析usage
#####################################

#coding=UTF-8

import re, copy
from logger import log
from help_parse import parse_options_parameters, split_parameter_command, get_parameters_type


def get_usage(file_list, file_name, log_file):
    """
        获取 usage

        Args:
            file_list ([list]): [帮助信息列表]
            file_name ([string]): [命令名称]
            log_file ([string]): [日志打印目录]

        Returns:
            [string]: usage使用规则
    """
    # 记录 usage
    usage_content = ""
    # 记录 usage 开始行数
    start = len(file_list)
    for i in range(0, len(file_list)):
        if re.search("usage:", file_list[i], re.I) is not None:
            usage_content = file_list[i]
            start = i + 1
            break
    #  usage 尚未结束的判断方式 ：
    # 1. usage存在，但是内容为空（可使用 len < 10 便于匹配 usage usage:）
    # 2. usage 非空 并且 下一行有前置空格 并且 不是空行
    for i in range(start, len(file_list)):
        # 对 smi开头的 几个文件特殊化处理，由于 libsmi 软件包 下的 以几个 smi 开头的命令不规范，
        # usage第一行没有前置空格，第二行有前置空格且没有提示 options 导致无法正确识别 usage, 直接取第一行作为 usage
        if str(file_name).startswith("smi"):
            break
        if len(usage_content) < 10:
            # usage 存在 但内容为空的情况下，若下一行为空行,并且下下行不包含命令名，则表示找不到 usage
            if len(file_list[i]) == 0 or str(file_list[i]).isspace():
                if len(file_list) <= i + 1:
                    log.warning("命令 " + file_name + "存在 --help , 但 --help 不包含 usage 使用规则", log_file)
                    return []
                if re.search(file_name, file_list[i + 1]) is None:
                    log.warning("命令 " + file_name + "存在 --help , 但 --help 不包含 usage 使用规则", log_file)
                    return []
            else:
                usage_content = usage_content + " " + file_list[i]
        else:
            if len(file_list[i]) == 0 or str(file_list[i]).isspace():
                # usage 内容非空，且下一行是空行的情况，表示 usage 已结束
                break
            if str(file_list[i]).startswith(" "):
                # 下一行存在前置空格，表示 usage 未结束
                usage_content = usage_content + " " + file_list[i]
            else:
                # 下一行不存在前置空格，表示 usage 已结束
                break
    usage_content = options_special_handle(usage_content)
    return usage_content

def options_special_handle(usage_content):
    """
        usage中 options异常情况处理

        Args:
            usage_content ([string]): [usage信息]

        Returns:
            [string]: usage信息
    """
    usage_content = usage_content.replace("[<option>...]", "")
    usage_content = usage_content.replace("[git-merge options]", "[options]")
    usage_content = usage_content.replace("\"some text\"", "text")
    usage_content = usage_content.replace("[...]", "")
    usage_content = usage_content.replace(" ...", "")
    usage_content = usage_content.replace("...", "")
    usage_content = usage_content.replace("$", "")
    return usage_content

def elaborate_usage(usage_content, file_name):
    """
        细化 usage 使用规则

        Args:
            usage_content ([string]): [usage信息]
            file_name ([string]): [命令名]

        Returns:
            [list]: usage使用规则
    """
    usage_content = re.sub("usage:", "", usage_content, 1, re.I).strip()
    flag = 0
    temp = ""
    usage_list = []
    usage_list_temp = usage_content.split(" ")
    i = 0
    while i < len(usage_list_temp):
        if str(usage_list_temp[i]).__eq__(""):
            i += 1
            continue
        if flag == 0 and re.search(".*[<>\[\](){}].*", usage_list_temp[i]) is None:
            # 解决命令名称是完整的路径的问题
            if usage_list_temp[i].__contains__("/CPIO/usr/") and usage_list_temp[i].__contains__("/"):
                usage_list.append(usage_list_temp[i].split("/")[-1])
            else:
                usage_list.append(usage_list_temp[i])
            i += 1
            continue
        if flag == 0 and usage_list_temp[i].startswith("("):
            temp1 = ""
            while True:
                temp1 = temp1 + " " + usage_list_temp[i]
                if usage_list_temp[i].endswith(")"):
                    usage_list.append(temp1.strip())
                    break
                i += 1
            i += 1
            continue
        if flag == 0 and usage_list_temp[i].startswith("{"):
            temp2 = ""
            while True:
                temp2 = temp2 + " " + usage_list_temp[i]
                if usage_list_temp[i].__contains__("}"):
                    usage_list.append(temp2.strip())
                    break
                i += 1
            i += 1
            continue
        temp = temp + " " + usage_list_temp[i]
        for j in range(0, len(usage_list_temp[i])):
            if usage_list_temp[i][j].__eq__("[") or usage_list_temp[i][j].__eq__("<"):
                flag += 1
            if usage_list_temp[i][j].__eq__("]") or usage_list_temp[i][j].__eq__(">"):
                flag -= 1
        if flag == 0:
            usage_list.append(temp)
            temp = ""
        i += 1
    # 去掉最外层没有含义的 |
    i = 0
    while i < len(usage_list):
        if usage_list[i].strip().__eq__("|"):
            usage_list.pop(i)
            i -= 1
        else:
            i += 1
    # 去掉前后缀空格
    for i in range(0, len(usage_list)):
        usage_list[i] = usage_list[i].strip()
    # 特殊情况处理
    special_handle(usage_list, file_name)
    return usage_list

def special_handle(usage_list, file_name):
    """
        特殊情况处理

        Args:
            usage_list ([list]): [usage使用规则]
            file_name ([string]): [命令名]
    """
    # 去掉第一个元素 java ，第二个元素 org.mozilla.javascript.tools.shell.Main  （shell中 rhino 源码不规范导致）
    if str(usage_list[0]).strip().__eq__("java"):
        usage_list.pop(0)
    if usage_list.__len__() > 0 and str(usage_list[0]).strip().__eq__("org.mozilla.javascript.tools.shell.Main"):
        usage_list.pop(0)
    # 若 usage_list 第一个元素不是文件名，需要手动加上文件名, 例如 rhino 、 evdev-joystick 、 linuxdoc 的 usage 中未给出文件名
    # 为防止 usage 给出的命令名称和 文件名不一致，同时满足 usage_list[0] 不包含 option 时，添加文件名
    if not usage_list[0].__contains__(file_name) and re.search("option", usage_list[0], re.I) is not None:
        usage_list.insert(0, file_name)
    # 统一化处理，再 usage_list[1] 出现option的情况下，将 usage_list[1] 统一转换成 options 、[] <> 保持不变
    # [OPTION] [OPTIONS] [option] [options] [<options>]   -->   [options]  可选的命令参数
    # <OPTION> <OPTIONS> <option> <options>   -->   <options>   必选的命令参数
    # [-o <mount options>] [--os-options OPTIONS]    ---->  普通参数
    for i in range(0, len(usage_list)):
        if re.search("\[option", usage_list[i], re.I) is not None:
            usage_list[i] = "[options]"
        if re.search("\[<option", usage_list[i], re.I) is not None:
            usage_list[i] = "[options]"
        if re.search("<option", usage_list[i], re.I) is not None:
            usage_list[i] = "<options>"
    # 由于 psbook 软件包的 usage 格式问题，需要去掉第二行的说明信息
    # Usage: psbook [-q] [-sSIGNATURE] [INFILE [OUTFILE]]
    # SIGNATURE must be positive and divisible by 4
    for i in range(1, len(usage_list)):
        if usage_list[i - 1].__eq__("SIGNATURE") and usage_list[i].__eq__("must"):
            for j in range(i - 1, len(usage_list)):
                usage_list.pop(i - 1)
            break

def split_usage(usage_list, file_name):
    """
        拆分 usage 保证每个 list 只代表一种类型的命令格式

        Args:
            usage_list ([list]): [usage使用规则]
            file_name ([string]): [命令名]

        Returns:
            [list]: usage使用规则
    """
    index_arr = []
    # 防止文件名称和命令名称不一致，两个都比较一下
    command_name = usage_list[0]
    for i in range(0, usage_list.__len__()):
        if usage_list[i].__contains__(file_name) or usage_list[i].__contains__(command_name):
            index_arr.append(i)
    usage_multiple_list = []
    start = 0
    end = 0
    if index_arr.__len__() == 1:
        usage_multiple_list.append(usage_list)
        return usage_multiple_list
    for i in range(1, index_arr.__len__()):
        start = index_arr[i - 1]
        end = index_arr[i]
        temp = usage_list[start:end]
        usage_multiple_list.append(temp)
    usage_multiple_list.append(usage_list[end:])
    return usage_multiple_list

def split_help_command(res_multiple_list):
    """
        对于既包含 -h 又包含其他参数的命令进行处理，拆分成单独的 -h 和其他命令

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    i = 0
    while i < len(res_multiple_list):
        if len(res_multiple_list[i]) < 3:
            i = i + 1
            continue
        if str(res_multiple_list[i][1]).__eq__("-h"):
            temp_list = res_multiple_list[i][0:2]
            res_multiple_list.insert(i, temp_list.copy())
            res_multiple_list[i + 1].pop(1)
            temp_list = res_multiple_list[i + 1]
            res_multiple_list.insert(i, temp_list.copy())
            res_multiple_list.pop(i + 2)
        i = i + 1
    # 二维元组去重
    remove_duplicate(res_multiple_list)

def remove_duplicate(res_multiple_list):
    """
        二维元组去重

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    i = 0
    while i < len(res_multiple_list):
        j = i + 1
        res_list = res_multiple_list[i]
        while j < len(res_multiple_list):
            if is_same(res_list, res_multiple_list[j]):
                res_multiple_list.pop(j)
            else:
                j = j + 1
        i = i + 1

def is_same(res_list1, res_list2):
    """
        判断两个一维元组是否相同

        Args:
            res_list1 ([list]): [元组1]
            res_list2 ([list]): [元组2]

        Returns:
            [bool]: 表示是否相同
    """
    if len(res_list1) != len(res_list2):
        return False
    for i in range(0, len(res_list1)):
        if not str(res_list1[i]).__eq__(str(res_list2[i])):
            return False
    return True

def handle_special_para(res_multiple_list):
    """
        特殊情况处理，处理出现异常或者重复出现的普通参数

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    for i in range(0, len(res_multiple_list)):
        for j in range(1, len(res_multiple_list[i])):
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).replace("<file>[<file>]", "file")
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).replace("<file[file]>", "file")
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).replace("<pattern>[<pattern>]", "pattern")
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).replace("<pkg[pkg]>", "pkg")
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).replace("file1 [file2 ]", "file")
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).replace("SIGNATURE must be positive and divisible by 4", "")
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).replace("[<A>", "A")
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).replace("<d>", " d")

def split_command(res_multiple_list):
    """
        将命令和变量拆分

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    for i in range(0, len(res_multiple_list)):
        j = 1
        while j < len(res_multiple_list[i]):
            if not str(res_multiple_list[i][j]).strip().startswith("-"):
                j = j + 1
                continue
            if str(res_multiple_list[i][j]).strip().__contains__(" "):
                temp_list = str(res_multiple_list[i][j]).strip().split(" ", 1)
                res_multiple_list[i].insert(j, temp_list[0].strip())
                res_multiple_list[i].insert(j + 1, temp_list[1].strip())
                res_multiple_list[i].pop(j + 2)
            elif str(res_multiple_list[i][j]).strip().__contains__("="):
                temp_list = str(res_multiple_list[i][j]).strip().split("=", 1)
                res_multiple_list[i].insert(j, temp_list[0].strip())
                res_multiple_list[i].insert(j + 1, temp_list[1].strip())
                res_multiple_list[i].pop(j + 2)
            j = j + 1

def get_global_para(usage_list):
    """
        处理全局变量（位置参数）

        Args:
            usage_list ([list]): [usage信息]

        Returns:
            [list]: 位置参数
    """
    # 记录全局参数
    global_para_list_tmp = set()
    i = len(usage_list) - 1
    while i >= 1:
        if usage_list[i] == usage_list[0]:
            i = i -1
            continue
        if usage_list[i-1] == usage_list[0] and not usage_list[i].__contains__("<") and not usage_list[i].__contains__("["):
            i = i - 1
            continue
        if re.search("^\W*-\w*.*$", usage_list[i]) is not None:
            i = i - 1
            continue
        if usage_list[i].__contains__("[options]") or usage_list[i].__contains__("<options>") or usage_list[
            i].__contains__("--") or usage_list[i].startswith("["):
            # if not usage_list[i].__contains__("[options]") and not usage_list[i].__contains__("<options>") and not usage_list[
            # i].__contains__("--"):
            #     usage_list.pop(i)
            i = i - 1
            continue
        global_para_list_tmp.add(str(usage_list[i]))
        usage_list.pop(i)
        i = i - 1
    if global_para_list_tmp is None or len(global_para_list_tmp) == 0:
        return []
    global_para_list = []
    global_para_list.extend(global_para_list_tmp)
    global_para_list.reverse()
    return global_para_list

def handle_global_list(global_para_list):
    """
        # 将全局变量(位置参数)处理成二维链表，考虑到多个子命令的情况

        Args:
            global_para_list ([list]): [位置参数]

        Returns:
            [list]: 参数命令
    """
    res_multiple_list = []
    if len(global_para_list) == 0:
        return []
    res_multiple_list.append(global_para_list.copy())
    for i in range(0, len(global_para_list)):
        j = 0
        while j < len(res_multiple_list):
            if re.search(r"(^\{[a-zA-Z]+.*,[a-zA-Z]+.*}$)", res_multiple_list[j][i]) is not None:
                s = res_multiple_list[j][i][1:len(res_multiple_list[j][i]) - 1]
                s_list = str(s).split(",")
                temp_list = res_multiple_list[j].copy()
                res_multiple_list.pop(j)
                s_list.reverse()
                for d in s_list:
                    temp_list.pop(i)
                    temp_list.insert(i, d)
                    res_multiple_list.insert(j, temp_list.copy())
            j = j + 1
    return res_multiple_list

def split_command_has_or(usage_multiple_list):
    '''
    进一步拆分包括"|"的命令

    Args:
        usage_multiple_list ([list]): 命令列表
    '''
    i = 1
    while i <= len(usage_multiple_list):
        has_or = False
        usage = usage_multiple_list[i-1]
        for j in range(0, len(usage)):
            # 如果包含“|”，则拆分成多个命令，删除当前的，将新的放到末尾
            if re.search("\|", usage[j]):
                # 分为多种情况去处理："XX|XX", "[ | ]", "{|}", "[XX {XX|XX}]", "[ | {}]"
                # 0. 包含{|}
                if re.search(r'\{.*\|.*\}', usage[j]) is not None:
                    usage_multiple_list.pop(i - 1)
                    has_or = True
                    match = re.search(r'\{.*\|.*\}', usage[j])
                    new_usage_item = re.sub(r'\{.*\|.*\}', "UUUUNNNN", usage[j], 1)
                    sub_items = match.group().split("|")
                    for sub_item in sub_items:
                        tmp = list()
                        tmp.extend(usage[k] for k in range(j))
                        sub_item = sub_item.replace("{", "")
                        sub_item = sub_item.replace("}", "")
                        tmp_new_usage_item = new_usage_item.replace("UUUUNNNN", sub_item)
                        tmp.append(tmp_new_usage_item)
                        tmp.extend(usage[k] for k in range(j + 1, len(usage)))
                        usage_multiple_list.insert(len(usage_multiple_list), tmp)
                    break
                # 1. "XX|XX"
                if not usage[j].__contains__("[") and not usage[j].__contains__("{"):
                    usage_multiple_list.pop(i - 1)
                    has_or = True
                    sub_items = usage[j].split("|")
                    for sub_item in sub_items:
                        tmp = list()
                        tmp.extend(usage[k] for k in range(j))
                        tmp.append(sub_item)
                        tmp.extend(usage[k] for k in range(j+1, len(usage)))
                        usage_multiple_list.insert(len(usage_multiple_list), tmp)
                    break
                # 2. "[ | ]"
                if usage[j].__contains__("[") and not usage[j].__contains__("{"):
                    usage_multiple_list.pop(i - 1)
                    has_or = True
                    sub_items = usage[j].split("|")
                    for sub_item in sub_items:
                        tmp = list()
                        tmp.extend(usage[k] for k in range(j))
                        if sub_item.startswith("[") and not sub_item.endswith("]"):
                            tmp.append(sub_item + " ]")
                        elif not sub_item.startswith("[") and sub_item.endswith("]"):
                            tmp.append("[ " + sub_item)
                        else:
                            tmp.append("[ " + sub_item + " ]")
                        tmp.extend(usage[k] for k in range(j + 1, len(usage)))
                        usage_multiple_list.insert(len(usage_multiple_list), tmp)
                    break
                # 3. "{|}"
                if not usage[j].__contains__("[") and usage[j].__contains__("{"):
                    usage_multiple_list.pop(i - 1)
                    has_or = True
                    sub_items = usage[j].split("|")
                    for sub_item in sub_items:
                        tmp = list()
                        tmp.extend(usage[k] for k in range(j))
                        if sub_item.startswith("{") and not sub_item.endswith("}"):
                            tmp.append(sub_item + " }")
                        elif not sub_item.startswith("{") and sub_item.endswith("}"):
                            tmp.append("{ " + sub_item)
                        else:
                            tmp.append("{ " + sub_item + " }")
                        tmp.extend(usage[k] for k in range(j + 1, len(usage)))
                        usage_multiple_list.insert(len(usage_multiple_list), tmp)
                    break
                # 4. "[|{}]" "[{}|]"
                if usage[j].__contains__("[") and usage[j].__contains__("{"):
                    usage_multiple_list.pop(i - 1)
                    has_or = True
                    sub_items = usage[j].split("|")
                    for sub_item in sub_items:
                        tmp = list()
                        tmp.extend(usage[k] for k in range(j))
                        if sub_item.startswith("[") and not sub_item.endswith("]"):
                            tmp.append(sub_item + " ]")
                        elif not sub_item.startswith("[") and sub_item.endswith("]"):
                            tmp.append("[ " + sub_item)
                        else:
                            tmp.append("[ " + sub_item + " ]")
                        tmp.extend(usage[k] for k in range(j + 1, len(usage)))
                        usage_multiple_list.insert(len(usage_multiple_list), tmp)
                    break
        if not has_or:
            i = i + 1

def retrieve_supported_commands(content):
    '''
    根据帮助文档获取在命令中可以被替换成具体取值的那些参数

    Args:
        content (string): 帮助文档
    '''
    commands_map = dict()
    lines = content.split("\n")
    start = False
    tmp_command = ""
    tmp_values = []
    for line_index in range(0, len(lines)):
        if lines[line_index].startswith("Supported"):
            if tmp_command != "":
                commands_map[tmp_command] = tmp_values
                tmp_values = []
            start = True
            tmp_command = lines[line_index].split("Supported ")[1].split(" ")[0]
            continue
        if start:
            if lines[line_index] != "" and lines[line_index].startswith(" "):
                tmp_values.append(lines[line_index].strip().split(" ")[0])
                if line_index == len(lines) - 1:
                    commands_map[tmp_command] = tmp_values
            else:
                start = False
                commands_map[tmp_command] = tmp_values
                tmp_values = []
                tmp_command = ""
    return commands_map

def retrieve_specific_options(content):
    '''
    根据帮助文档解析那些针对某些参数定义的选项

    Args:
        content (string): 帮助文档
    '''
    options_map = dict()
    lines = content.split("\n")
    start = False
    tmp_option = ""
    tmp_values = []
    for line_index in range(0, len(lines)):
        if lines[line_index].startswith("Specific option"):
            if tmp_option != "":
                options_map[tmp_option] = tmp_values
                tmp_values = []
            start = True
            tmp_option = lines[line_index].split("Specific option for the ")[1].split(" ")[0]
            continue
        if start:
            if lines[line_index] != "" and lines[line_index].startswith(" "):
                tmp_values.append(lines[line_index].strip().split(" ")[0])
                if line_index == len(lines) - 1:
                    options_map[tmp_option] = tmp_values
            else:
                start = False
                options_map[tmp_option] = tmp_values
                tmp_values = []
                tmp_option = ""
    return options_map

def parse_usage_parameters(content, file_name, log_file):
    """
        解析参数命令, 获取 usage 使用规则
        函数入口

        Args:
            content ([string]): [帮助信息]
            file_name ([string]): [命令名称]
            log_file ([string]): [日志打印目录]

        Returns:
            [list]: 参数命令
            [list]: 参数命令备份
    """
    """  解析参数命令  """
    # 记录 usage 具体使用方法，例如：
    # Usage: git-clone-subset [options] <repository> <destination-dir> <pattern>
    # Usage: beakerlib-lsb_release [OPTION]...
    file_list = str(content).split("\n")
    # 获取 usage
    usage_content = get_usage(file_list, file_name, log_file)
    # 细化 usage 使用规则
    usage_list = []
    if len(usage_content) != 0:
        usage_list = elaborate_usage(usage_content, file_name)
    if usage_list.__len__() == 0:
        log.warning("命令 " + file_name + "不存在可用于解析的帮助信息, 帮助信息解析失败", log_file)
        return "", ""

    # 处理全局变量的问题, 获取全局参数，并单独拿出来
    global_para_list = get_global_para(usage_list)
    # 将全局变量处理成二维链表，考虑到多个子命令的情况，如 ['instance', '{account,group,initialise,organizationalunit,posixgroup,user,client_config,role}']
    global_para_list = handle_global_list(global_para_list)

    # 拆分 usage 以保证每个 list 只代表一种类型的命令格式, 例如 criu 的 usage 中包含了 7 个不同类型的命令
    # 'criu','dump|pre-dump','-t','PID','[options]',   'criu','restore','[options]'  等
    usage_multiple_list = split_usage(usage_list, file_name)

    # 拆分包含“|”的那些命令，例如['criu','dump|pre-dump','-t','PID','[options]']
    split_command_has_or(usage_multiple_list)

    # 存在某些软件包的option参数定义包含冗余的内容，需要将其删掉；例如['yapp', '[-OPTIONS [-MORE_OPTIONS]]', '[--]', '[PROGRAM_ARG1]']
    for usage_list_item in usage_multiple_list:
        for sub_item_index in range(0, len(usage_list_item)):
            if usage_list_item[sub_item_index].startswith("[-OPTIONS ["):
                usage_list_item[sub_item_index] = "[options]"

    # 获取并替换 --help 中给出的 option
    flag = False
    for d in usage_list:
        if re.search("<option", d, re.I) is not None or re.search("<-option", d, re.I) is not None or re.search("< option", d, re.I) is not None or re.search("< -option", d, re.I) is not None or re.search("\[option", d, re.I) is not None or re.search("\[-option", d, re.I) is not None or re.search("\[ option", d, re.I) is not None or re.search("\[ -option", d, re.I) is not None:
            flag = True
            break
    if flag:
        # 将全局参数加入
        # 只有当 usage 中存在 option 的情况下，才需要去解析 content 中的 option,并且用解析出来的具体 option 命令参数替换 usage
        res_multiple_list = parse_options_parameters.parse_options_parameters(usage_multiple_list, global_para_list,
                                                                              content, file_name)
        # 对于既包含 -h 又包含其他参数的命令进行处理，拆分成单独的 -h 和其他命令
        split_help_command(res_multiple_list)
    else:
        # 将全局参数加入
        # 拆分命令，将不包含 [options] 的 usage 中的复合命令参数进一步拆分，使之成为独立的形式
        res_multiple_list = split_parameter_command.split_parameter_command(usage_multiple_list, global_para_list,
                                                                            file_name)
        # 对于既包含 -h 又包含其他参数的命令进行处理，拆分成单独的 -h 和其他命令
        split_help_command(res_multiple_list)
        pass

    # 再次处理每一个命令中可能被content中额外定义的内容替换的部分：supported command和specific options
    # 首先提取command；它可以直接替换命令中对应的内容；以supported XXXs are作为关键词
    supported_command_map = retrieve_supported_commands(content)
    # 再提取specific options：当存在对应的参数时，可以追加这些options；以Specific option为关键词
    specific_option_map = retrieve_specific_options(content)

    # 先对所有命令替换可能的command
    for key in supported_command_map.keys():
        command_index = 1
        while command_index <= len(res_multiple_list):
            substitute_ok = False
            command = res_multiple_list[command_index - 1]
            for command_item_index in range(1, len(command)):
                current_item = command[command_item_index]
                if current_item.startswith("-") and current_item.__contains__("="):
                    sub_command_items = current_item.split("=")
                    sub_command_tmp = sub_command_items[1]
                    if key.startswith(sub_command_tmp):
                        substitute_ok = True
                        res_multiple_list.pop(command_index - 1)
                        for value in supported_command_map[key]:
                            new_command = []
                            new_command.extend(command[k] for k in range(command_item_index))
                            new_command.append(sub_command_items[0] + "=" + value)
                            new_command.extend(command[k] for k in range(command_item_index + 1, len(command)))
                            res_multiple_list.insert(len(res_multiple_list), new_command)
                        break
                elif not current_item.__contains__("-"):
                    if key.startswith(current_item):
                        substitute_ok = True
                        res_multiple_list.pop(command_index - 1)
                        for value in supported_command_map[key]:
                            new_command = []
                            new_command.extend(command[k] for k in range(command_item_index))
                            new_command.append(value)
                            new_command.extend(command[k] for k in range(command_item_index + 1, len(command)))
                            res_multiple_list.insert(len(res_multiple_list), new_command)
                        break
            if not substitute_ok:
                command_index = command_index + 1

    # 再对命令中和参数相关的option进行扩展；和上面替换命令不同，此处只需要对原有列表遍历，在满足条件的时候直接添加新的参数即可
    current_command_numbers = len(res_multiple_list)
    for key in specific_option_map.keys():
        command_index = 1
        while command_index <= current_command_numbers:
            command = res_multiple_list[command_index - 1]
            for command_item_index in range(1, len(command)):
                current_item = command[command_item_index]
                if current_item.startswith("-") and current_item.__contains__("="):
                    sub_command_items = current_item.split("=")
                    sub_command_tmp = sub_command_items[1]
                    if key.__contains__(sub_command_tmp):
                        for value in specific_option_map[key]:
                            new_command = []
                            new_command.extend(command)
                            new_command.append(value)
                            res_multiple_list.insert(len(res_multiple_list), new_command)
                        break
            command_index = command_index + 1

    # 处理出现异常的普通参数
    handle_special_para(res_multiple_list)
    # 将命令和变量拆分
    split_command(res_multiple_list)
    # 记录赋值前的命令参数,便于查询参数类型与添加注释信息
    res_multiple_back_list = copy.deepcopy(res_multiple_list)
    # 去掉外层括号
    split_parameter_command.remove_outer_bracket(res_multiple_list)
    # 去空
    res_multiple_list = [x for x in res_multiple_list if x]
    # 根据参数类型，获取并且填入参数值
    get_parameters_type.get_parameters_type(res_multiple_list, copy.deepcopy(res_multiple_list))
    return res_multiple_list, res_multiple_back_list