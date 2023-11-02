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
# @Desc      	:   分离参数命令
#####################################

#coding=UTF-8

import re, copy

from help_parse import parse_options_parameters


def split_command(usage_list):
    """
        拆分 usage 中的参数命令

        Args:
            usage_list ([list]): [usage信息]

        Returns:
            [list]: 参数命令
            [string]: 位置参数
    """
    # 合并命令参数和普通参数
    # global_para 记录整体的参数变量
    global_para = merge_command_parameter(usage_list)
    # 获取必选和可选命令参数位置
    required_parameters = []
    required_parameters_index = []
    optional_parameters = []
    optional_parameters_index = []
    res_multiple_list = get_parameters_index(usage_list, required_parameters, required_parameters_index,
                                             optional_parameters, optional_parameters_index)
    return res_multiple_list, global_para

def get_parameters_index(usage_list, required_parameters, required_parameters_index, optional_parameters, optional_parameters_index):
    """
        处理必选和可选参数位置

        Args:
            usage_list ([list]): [usage信息]
            required_parameters ([list]): [必选参数]
            required_parameters_index ([list]): [必选参数位置]
            optional_parameters ([list]): [可选参数]
            optional_parameters_index ([list]): [可选参数位置]

        Returns:
            [list]: 参数命令
    """
    res_multiple_list = []
    for i in range(0, len(usage_list)):
        # 可选参数
        if usage_list[i].startswith("["):
            optional_parameters.append(usage_list[i])
            optional_parameters_index.append(i)
        else:
            # 必选参数
            required_parameters.append(usage_list[i])
            required_parameters_index.append(i)
    s = []
    s_index = []
    for i in range(0, len(required_parameters_index)):
        s.append(required_parameters[i])
        s_index.append(required_parameters_index[i])
    # 插入所有可选参数都不选的情况
    res_multiple_list.append(s.copy())
    for i in range(0, len(optional_parameters_index)):
        # 找到可选参数应该插入的位置
        index = 0
        for j in range(0, len(s_index)):
            if optional_parameters_index[i] > s_index[j]:
                index = j
            else:
                break
        s.insert(index + 1, optional_parameters[i])
        res_multiple_list.append(s.copy())
        s.pop(index + 1)
    return res_multiple_list

def merge_command_parameter(usage_list):
    """
        合并命令参数和普通参数， 提取全局变量（位置参数）

        Args:
            usage_list ([list]): [usage信息]

        Returns:
            [string]: 位置参数
    """
    i = 0
    while i < len(usage_list):
        if not usage_list[i].startswith("[-") and not usage_list[i].startswith("(-") and not usage_list[i].startswith(
                "-"):
            i = i + 1
            continue
        i = i + 1
        j = i
        while j < len(usage_list):
            if usage_list[j].startswith("[-") or usage_list[j].startswith("(-") or usage_list[j].startswith("-"):
                i = j
                break
            else:
                usage_list[i - 1] = usage_list[i - 1] + " " + str(usage_list[j])
                usage_list.pop(j)
    # 提取出全局参数
    s = str(usage_list[len(usage_list) - 1]).strip()
    flag = re.match(r"^(\[-.*])|^(\(-.*\))|^(\{-.*})|^(-\w* )", s)
    global_para = ""
    if flag is None:
        pass
    else:
        end = flag.end()
        if end >= len(s):
            pass
        else:
            global_para = s[end:].strip()
            s = s[0:end].strip()
            usage_list[len(usage_list) - 1] = s
    return global_para

def handle_similar_command(res_multiple_list):
    """
        拆分参数命令，对可能出现的以|连接的相同类型的参数进行处理

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    # 以"[]", "()", "{}" 为拆分条件， 将命令拆分
    split_one_command(res_multiple_list)
    # 去掉每个参数命令最外层的括号
    remove_outer_bracket(res_multiple_list)
    remove_outer_bracket(res_multiple_list)
    # 将 -hV, -Vh, -Vhn等命令拆分,将-wWIDTH, -hHEIGHT, -pPAPER 等命令和参数拆分
    handle_special_command(res_multiple_list)
    i = 0
    while i < len(res_multiple_list):
        j = 1
        while j < len(res_multiple_list[i]):
            s = res_multiple_list[i][j]
            # 不需要分割的情况
            if not str(s).__contains__("|"):
                j = j + 1
                continue
            if re.match(r"^(\(-\D*.*\))$|^(\[-\D*.*])$|^(\{-\D*.*})$|^(<-\D*.*>)$|^(-\D*.*)", str(s)) is None:
                j = j + 1
                continue
            s_list = str(s).split("|")
            # 分割完成后，命令需要变量的情况
            if need_para(s):
                # 分隔符 | 被用于分隔变量的情况, 直接取第一个参数
                if re.match(r"^(\(-\D*.*\))$|^(\[-\D*.*])$|^(\{-\D*.*})$|^(<-\D*.*>)$|^(-\D*.*)", s_list[1]) is None:
                    res_multiple_list[i][j] = s_list[0]
                # 分割前后的命令参数都自带变量的情况
                elif s_list[0].strip().__contains__(" ") or s_list[0].strip().__contains__("="):
                    for m in range(0, len(s_list)):
                        res_multiple_list[i].pop(j)
                        res_multiple_list[i].insert(j, s_list[m].strip())
                        res_multiple_list.insert(i + 1, res_multiple_list[i].copy())
                    res_multiple_list.pop(i)
                    pass
                # | 用于分隔命令，参数在后面的情况
                else:
                    temp_list = []
                    for m in range(0, len(s_list)):
                        if re.match(r"^(\(-\D*.*\))$|^(\[-\D*.*])$|^(\{-\D*.*})$|^(<-\D*.*>)$|^(-\D*.*)",
                                    s_list[m]) is not None:
                            temp_list.append(s_list[m])
                    para = ""
                    if temp_list[len(temp_list) - 1].strip().__contains__(" "):
                        para = temp_list[len(temp_list) - 1].strip().split(" ")[1]
                        temp_list[len(temp_list) - 1] = temp_list[len(temp_list) - 1].strip().split(" ")[0]
                    elif temp_list[len(temp_list) - 1].strip().__contains__("="):
                        para = temp_list[len(temp_list) - 1].strip().split("=")[1]
                        temp_list[len(temp_list) - 1] = temp_list[len(temp_list) - 1].strip().split("=")[0]
                    else:
                        break
                    for m in range(0, len(temp_list)):
                        temp_list[m] = temp_list[m] + " " + para
                    for m in range(0, len(temp_list)):
                        res_multiple_list[i].pop(j)
                        res_multiple_list[i].insert(j, temp_list[m].strip())
                        res_multiple_list.insert(i + 1, res_multiple_list[i].copy())
                    res_multiple_list.pop(i)
                    pass
            else:
                # 分割完成后，命令参数不需要变量的情况
                temp_list = []
                for m in range(0, len(s_list)):
                    if s_list[m].strip().startswith("-"):
                        temp = s_list[m]
                    else:
                        temp = "-" + s_list[m].strip()
                    temp_list.append(temp)
                temp_list.reverse()
                for m in range(0, len(temp_list)):
                    res_multiple_list[i][j] = temp_list[m].strip()
                    res_multiple_list.insert(i + 1, res_multiple_list[i].copy())
                res_multiple_list.pop(i)
            j = j + 1
        i = i + 1

def need_para(s):
    """
        判断命令参数是否需要变量

        Args:
            s ([string]): [参数命令]

        Returns:
            [bool]: 是否需要变量
    """
    s_list = str(s).strip().split("|")
    for i in range(0, len(s_list)):
        if s_list[i].strip().__contains__(" ") or s_list[i].strip().__contains__("="):
            return True
    return False

def split_one_command(res_multiple_list):
    """
        # 以"[]", "()", "{}" 为拆分条件， 将命令拆分

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    for i in range(0, len(res_multiple_list)):
        j = 1
        while j < len(res_multiple_list[i]):
            res_multiple_list[i][j] = parse_options_parameters.handle_common_parameters(res_multiple_list[i][j])
            s = str(res_multiple_list[i][j])
            s_list = []
            num1 = 0
            num2 = 0
            num3 = 0
            start = 0
            if re.match(r"(\()|(\))|(\[)|(])|({)|(})", s) is None:
                j = j + 1
                continue
            for m in range(0, len(s)):
                end = m + 1
                if s[m].__eq__("("):
                    num1 = num1 + 1
                elif s[m].__eq__(")"):
                    num1 = num1 - 1
                elif s[m].__eq__("["):
                    num2 = num2 + 1
                elif s[m].__eq__("]"):
                    num2 = num2 - 1
                elif s[m].__eq__("{"):
                    num3 = num3 + 1
                elif s[m].__eq__("}"):
                    num3 = num3 - 1
                elif m != len(s) - 1:
                    continue
                if end != start + 1 and not s[start:end].isspace() and num1 == 0 and num2 == 0 and num3 == 0:
                    s_list.append(s[start:end])
                    start = end
            if len(s_list) > 1:
                res_multiple_list[i].pop(j)
                for m in range(0, len(s_list)):
                    res_multiple_list[i].insert(j, s_list[len(s_list) - m - 1].strip())
            j = j + 1

def handle_special_command(res_multiple_list):
    """
        将 -hV, -Vh, -Vhn 等命令拆分, 将-wWIDTH, -hHEIGHT, -pPAPER 等命令和参数拆分

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    # 将 -hV, -Vh, -Vhn, -qQvV, -efcibaltnxrgjuyp, -hlV 等命令拆分成多个命令
    i = 0
    while i < len(res_multiple_list):
        for j in range(1, len(res_multiple_list[i])):
            s = str(res_multiple_list[i][j])
            if s.__eq__("-hV") or s.__eq__("-Vh") or s.__eq__("-Vhn") or s.__eq__("-afhnpqvVy") or s.__eq__("-hnqvVy") \
                    or s.__eq__("-hlV") or s.__eq__("-qQvV") or s.__eq__("-efcibaltnxrgjuyp"):
                s = "-" + ''.join(reversed(s[1:]))
                for l in range(1, len(s)):
                    temp_s = "-" + str(s[l])
                    temp_list = res_multiple_list[i]
                    temp_list[j] = temp_s
                    res_multiple_list.insert(i + 1, temp_list.copy())
                res_multiple_list.pop(i)
                break
        i = i + 1
    # 将 -wWIDTH, -hHEIGHT, -pPAPER 等命令和参数拆分成 一个命令+一个参数的格式
    for i in range(0, len(res_multiple_list)):
        for j in range(1, len(res_multiple_list[i])):
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).strip()
            if len(res_multiple_list[i][j]) > 2 and res_multiple_list[i][j].startswith("-") and not \
            res_multiple_list[i][j].startswith("--") and not res_multiple_list[i][j].__contains__(" "):
                # 特殊情况: -merge不处理
                if res_multiple_list[i][j].__eq__("-merge"):
                    continue
                command = res_multiple_list[i][j][0:2]
                para = res_multiple_list[i][j][2:]
                res_multiple_list[i][j] = (command + " " + para).strip()

def remove_outer_bracket(res_multiple_list):
    """
        去掉每个参数命令最外层括号 () <> [] {}

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    for i in range(0, len(res_multiple_list)):
        for j in range(1, len(res_multiple_list[i])):
            # 去掉最外层的括号
            res_multiple_list[i][j] = str(res_multiple_list[i][j]).strip()
            s = res_multiple_list[i][j]
            # ^(\(.*\))$|^(\[.*\])$|^(\{.*\})$|^(\".*\")$
            if re.match(r"^(\(.*\))$|^(\[.*])$|^(\{.*})$|^(<.*>)$", s, re.I) is not None:
                if parse_options_parameters.is_brackets_match([0, 0, 0, 0], s[1:len(s) - 1]):
                    s = s[1:len(s) - 1]
                    res_multiple_list[i][j] = s

def remove_multiple_brackets(usage_multiple_list):
    """
        去掉多重相同括号的情况，便于后续处理

        Args:
            usage_multiple_list ([list]): [usage信息]
    """
    for i in range(0, len(usage_multiple_list)):
        for j in range(1, len(usage_multiple_list[i])):
            # 将 -{ 转换成 {- , -[ 转换成 [- 便于处理括号问题
            usage_multiple_list[i][j] = usage_multiple_list[i][j].replace("-[", "[-")
            usage_multiple_list[i][j] = usage_multiple_list[i][j].replace("-[", "[-")
            usage_multiple_list[i][j] = usage_multiple_list[i][j].replace("-{", "{-")
            usage_multiple_list[i][j] = usage_multiple_list[i][j].replace("-{", "{-")
            usage_multiple_list[i][j] = usage_multiple_list[i][j].replace("-]", "] ")
            usage_multiple_list[i][j] = usage_multiple_list[i][j].replace("-}", "} ")
            s = str(usage_multiple_list[i][j]).strip()
            while s.startswith("[[") and s.endswith("]"):
                s = s[1:len(s) - 1].strip()

def split_parameter_command(usage_multiple_list, global_para_list, file_name):
    """
        拆分，将不包含 [options] 的 usage 中的复合命令参数进一步拆分，使之成为独立的形式
        函数入口

        Args:
            usage_multiple_list ([list]): [usage信息]
            global_para_list ([string]): [位置参数]
            file_name ([string]): [命令名称]

        Returns:
            [list]: 参数命令
    """
    res_multiple_list = []
    # 去掉多重相同括号的情况，便于后续处理
    remove_multiple_brackets(usage_multiple_list)
    # 拆分和格式化 usage ，确保 usage_list 中多个不同类型的参数命令不叠加在一起
    for i in range(0, len(usage_multiple_list)):
        temp_multiple_list, global_para = split_command(usage_multiple_list[i])
        for d in temp_multiple_list:
            res_multiple_list.append(d.copy())
    # 拆分参数命令，对可能出现的以|连接的相同类型的参数进行处理
    handle_similar_command(res_multiple_list)
    if global_para_list is None or len(global_para_list) == 0:
        pass
    else:
        # 将全局变量加入每个语句最后
        res = []
        for global_list in global_para_list:
            res_multiple_back_list = copy.deepcopy(res_multiple_list)
            for i in range(0, len(res_multiple_back_list)):
                for d in global_list:
                    res_multiple_back_list[i].append(d)
                res.append(res_multiple_back_list[i].copy())
        res_multiple_list = copy.deepcopy(res)
    remove_multiple_brackets(usage_multiple_list)
    return res_multiple_list
