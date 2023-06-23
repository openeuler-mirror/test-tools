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
# @Desc      	:   解析option
#####################################

#coding=UTF-8

import copy
import re, subprocess
from help_parse import split_parameter_command


def get_options(content, file_name):
    """
        获取处理后的 options

        Args:

            content ([string]): [命令帮助信息]
            file_name ([string]): [命令名称]

        Returns:
            [list]: -开头的短参数命令
            [list]: --开头的长参数命令
            [list]: 所有参数命令
    """
    # 特殊情况处理，-h 返回了 usage，但不包含option， -- help 不返回 usage 但返回了 option, 例如 fig2dev
    flag = is_own_option(content)
    # 当content中不包含usage关键词时，多做一次判断
    if not flag:
        content = get_sub_res(file_name, content)
    # 提取 options
    # 扫描每一行，若当前行去掉前置空格后，有 - 前置 ，则拿出来作为备选命令参数
    # 针对可能存在的专门指定了 -- 和 - 两类参数使用的位置不同，使用两个元组分别存储 -options 和 --options, 例如 'git-rebase-theirs','[options]','[--]','FILE'
    # 对于有-和--两种两种表达方式的命令参数，看做 -option, 不存放在 --options, 例如 -h, --help
    # 若当前命令不区分 - 和 --, 则两个 options 合并存储
    options_one_prefix = []
    options_two_prefix = []
    options = []
    for line in content.split("\n"):
        # 若当前行以 "- "开头，说明本行是解释说明类型的语句
        if line.strip().startswith("- "):
            continue
        # 前置空格超过 10 , 不考虑为命令参数，防止将解释说明中的-误判为命令参数
        if line.__len__() - line.lstrip().__len__() >= 10:
            continue
        elif line.strip().startswith("---"):
            continue
        elif line.startswith("Supported") or line.startswith("Specific"):
            break
        elif line.strip().startswith("-") or line.strip().startswith("--"):
            # 对携带命令参数的一行内容进行处理，取出命令参数和普通参数
            line_res = handle_line_option(line)
            res_list = handle_one_option(line_res)
            options.extend(res_list)
            for res in res_list:
                if res.startswith("--"):
                    options_two_prefix.append(res)
                    continue
                if res.startswith("-"):
                    options_one_prefix.append(res)
    return options_one_prefix, options_two_prefix, options

def get_sub_res(file_name, content):
    """
        通过 -h, --h, --help 三种方式获取content

        Args:
            file_name ([string]): [命令名称]
            content ([string]): [命令帮助信息]

        Returns:
            [string]: 命令帮助信息
    """
    sub_res = ""
    try:
        # 排除掉执行 getstatusoutput 超时的命令
        sub_res = subprocess.run(file_name + " -h", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 timeout=2)
        sub_status1, sub_res1 = subprocess.getstatusoutput(file_name + " -h")
        sub_status2, sub_res2 = subprocess.getstatusoutput(file_name + " --h")
        sub_status3, sub_res3 = subprocess.getstatusoutput(file_name + " --help")
        if is_own_option(sub_res1):
            return sub_res1
        if is_own_option(sub_res2):
            return sub_res2
        if is_own_option(sub_res3):
            return sub_res3
    except UnicodeDecodeError:
        res = re.sub("b'", "", str(sub_res.stdout), 1, re.I).strip()
        res = res[0:len(res) - 1]
        res = res.replace("\\n", "\n")
        content = res.split("\n")
        return content
    except subprocess.TimeoutExpired:
        return content

def is_own_option(content):
    """
        判断元组中是否存在 option

        Args:
            content ([string]): [命令帮助信息]

        Returns:
            [string]: 标志位，表真假
    """
    flag = False
    for line in content.split("\n"):
        if re.search("option", line, re.I) is not None:
            flag = True
            break
    return flag

def handle_line_option(line):
    """
        对携带命令参数的一行内容进行处理, 取出命令参数和普通参数

        Args:
            line ([string]): [帮助信息的一行内容]

        Returns:
            [string]: 处理后的帮助信息
    """
    # 1. 以两个空格或 tab 分割，去掉参数后面的解释语句
    line = line.strip().split("\t")[0]
    res = line.strip().split("  ")[0]
    # 2. 将 "[,"  替换成 "["  , 参数中出现 "[," 的多与 ... 配合，表示参数可多叠加，去掉","后不影响判断，便于后续拆分，例如 --ignore=<file[,file...]>
    res = re.sub("\[,", "[", res, 10, re.I).strip()
    # 3. 以一个空格划分
    res_list = res.strip().split(" ")
    if len(res_list) == 1:
        return res_list[0]

    res = ""
    for res_item in res_list:
        if res_item.startswith("-") or res_item.startswith("--"):
            res = res + res_item + " "
        else:
            break
    # # 4. 若既有 - 又有 -- ，则可以使用更为简单的 - 作为命令参数， 例如 -h, --help
    # if res_list[0].startswith("--"):
    #     s = res_list[0][1:3]
    #     index = get_one_command_index(res_list, s)
    #     if index != -1:
    #         for i in range(0, index):
    #             res_list.pop(0)
    # if len(res_list) == 1:
    #     return res_list[0]
    # res = res_list[0] + " " + res_list[1]
    # 为了防止在 [] <> 等内部存在空格导致分隔错误，扫描res_list,保证 [] <> () {} 匹配, 用 num[] 表示每个括号左右差值, flag 记录是否完全匹配
    # num = [0, 0, 0, 0]
    # flag = True
    # for i in range(0, 2):
    #     flag = is_brackets_match(num, res_list[i])
    # if flag:
    #     res = res_list[0] + " " + res_list[1]
    # else:
    #     for i in range(2, len(res_list)):
    #         flag = is_brackets_match(num, res_list[i])
    #         res = res + " " + res_list[i]
    #         if flag:
    #             break
    return res

def get_one_command_index(res_list, s):
    """
        获取 -command 位置

        Args:
            res_list ([string]): [参数命令]
            s ([string]): [command字符串]

        Returns:
            [int]: 位置
    """
    for i in range(1, res_list.__len__()):
        if re.search(s, res_list[i], re.I) is not None:
            return i
    return -1

def is_brackets_match(num, s):
    """
        统计成对出现的括号是否匹配

        Args:
            num ([list]): [括号数量计数列表]
            s ([string]): [command字符串]

        Returns:
            [bool]: 表示是否匹配
    """
    # 统计成对出现的括号是否匹配
    nums = get_brackets("[", "]", s)
    num[0] = num[0] + nums
    nums = get_brackets("<", ">", s)
    num[1] = num[1] + nums
    nums = get_brackets("(", ")", s)
    num[2] = num[2] + nums
    nums = get_brackets("{", "}", s)
    num[3] = num[3] + nums
    if num[0] < 0 or num[1] < 0 or num[2] < 0 or num[3] < 0:
        return False
    if num[0] == 0 and num[1] == 0 and num[2] == 0 and num[3] == 0:
        return True
    return False

def get_brackets(left, right, s):
    """
        统计括号不匹配时出现的次数差值

        Args:
            left ([int]): [左侧位置]
            right ([int]): [右侧位置]
            s ([string]): [command字符串]

        Returns:
            [int]: 次数差值
    """
    nums = 0
    for i in range(0, len(s)):
        if s[i].__eq__(left):
            nums = nums + 1
        if s[i].__eq__(right):
            nums = nums - 1
        if nums < 0:
            return -999
    return nums

def handle_one_option(line):
    """
        对通过行处理流程的 option 进一步细化处理

        Args:
            line ([string]): [帮助信息的某一行]

        Returns:
            [string]: 处理后结果
    """
    # 去掉前后置空格，逗号
    line = line.strip()
    if line.endswith(",") or line.endswith("."):
        line = line[0:len(line) - 1]
    # 去掉感叹号
    line = re.sub("!", "", line).strip()
    # 替换为简单逻辑，如果包括大括号，就按照大括号切分，返回多个参数的列表；如果没有大括号，按照等号划分得到参数取值，再按照逗号或|划分得到参数
    if re.search("{", line, re.I) is None:
        res_list = []
        if line.__contains__("="):
            line_list = line.split("=")
            common_parameter = line_list[1]
            if line_list[0].__contains__("|"):
                para_list = line_list[0].split("|")
            else:
                para_list = line_list[0].split(",")
            for para in para_list:
                res_list.append(para + "=" + common_parameter)
            return res_list
        else:
            if line.__contains__("|"):
                para_list = line.split("|")
            else:
                para_list = line.split(",")
            for para in para_list:
                res_list.append(para)
            return res_list
    else:
        res_list = []
        line_list = line.split("{")
        if len(line_list) > 1 and line_list[0] != "":
            para_list = line_list[1].split(",")
            for para in para_list:
                res_list.append(line_list[0] + " " + para)
            return res_list
        else:
            para_list = line_list[1].split(",")
            for para in para_list:
                res_list.append(para)
            return res_list
    # # 1. 以 "," 作为拆分条件，  "=" 表示有后续的普通参数
    # # 若以 "," 作为拆分条件拆分后，若不存在 "=", 取第一部分，否则，需要同时取后续的普通参数
    # # 存在 {} 的语句需要特殊考虑，它使用了 "," 间隔不同参数，例如 -B {html,info,latex,lyx,rtf,txt,check}
    # if re.search("{", line, re.I) is None:
        # line_list = line.split(",")
        # common_parameters = get_common_parameters(line_list)
        # line = line_list[0].strip()
        # if not line.__contains__(common_parameters):
        #     line = (line + " " + common_parameters).strip()
    # # 2. 对所有此时依然存在两种命令方式的命令参数，选取前面的一个， 例如 -h --help
    # line_list = line.split(" ")
    # index = len(line_list)
    # for i in range(1, len(line_list)):
    #     if line_list[i].strip().startswith("-"):
    #         index = i
    #         break
    # line = ""
    # for i in range(0, index):
    #     line = line + " " + line_list[i]
    # line = line.strip()
    # # 3. 元组中第一个元素若含有 "=" 且 不一 "=" 结尾，说明已拥有了参数命令和普通参数，直接使用即可
    # if line_list[0].__contains__("=") and not line_list[0].endswith("="):
    #     line = line_list[0]
    # # 4. 以 "|" 作为分隔条件，若分隔后以 "-"、"--" 开头的命令超过2个，选择后面的命令参数即可（考虑到普通参数会放在最后）
    # line_list = line.split("|")
    # line = choose_command(line_list, line)
    # line = handle_common_parameters(line)
    # return line

def get_common_parameters(line_list):
    """
        获取 "=" 后的普通参数

        Args:
            line_list ([list]): [处理后帮助信息的某一行]

        Returns:
            [string]: 普通参数
    """
    for line in line_list:
        if line.__contains__("="):
            return line.split("=")[1]
    return ""

def choose_command(line_list, res):
    """
        判断 line_list 中元素是否拥有多个连续的命令参数,将拥有多个连续相同命令的情况处理成一个

        Args:
            line_list ([list]): [处理后帮助信息的某一行]
            res ([list]): [处理前结果]

        Returns:
            [list]: [处理后结果]
    """
    # 1. 处理掉不应该使用 | 划分的情况，通过括号匹配判断 | 是否是最外层可分割的类型
    i = 0
    num = [0, 0, 0, 0]
    while i < len(line_list):
        flag = is_brackets_match(num, line_list[i])
        if flag:
            i = i + 1
        else:
            if i + 1 >= len(line_list):
                break
            line_list[i] = line_list[i] + "|" + line_list[i + 1]
            line_list.pop(i + 1)
            num = [0, 0, 0, 0]
    # 2. 所有部分都是参数命令"-","--"时，若有 "=" 优先选择带有 "=" 的部分，若有 " " 优先选择带有 " " 的部分，否则优先选择 "-"
    flag = True
    for line in line_list:
        if not line.strip().startswith("-"):
            flag = False
    if flag:
        for i in range(0, len(line_list)):
            if line_list[i].strip().__contains__("="):
                return line_list[i].strip()
        for i in range(0, len(line_list)):
            if line_list[i].strip().__contains__(" "):
                return line_list[i].strip()
        for i in range(0, len(line_list)):
            if line_list[i].strip().startswith("-") and not line_list[i].strip().startswith("--"):
                return line_list[i].strip()
        return line_list[0]
    # 3. 将 | 作为分隔不同普通参数的情况
    if line_list[0].__contains__("="):
        return res
    return res

def list_to_str(res_list, s):
    """
        将 list 转成 str 以 " " 作为分隔方式

        Args:
            res_list ([list]): [处理后的参数命令]
            s ([string]): [需要添加的分隔符]

        Returns:
            [list]: [处理后结果]
    """
    if res_list.__len__() == 0:
        return ""
    res = res_list[0]
    for i in range(0, len(res_list)):
        res = res + s + res_list[i]
    return res[0:len(str(res))]

def handle_common_parameters(res):
    """
        处理普通参数格式

        Args:
            res ([string]): [处理后的某一行参数命令]

        Returns:
            [string]: [处理后结果]
    """
    # 1. 将 "[=" 转换成 ”=[“，的格式，便于进一步处理，例如 --in-place[=SUFFIX]
    res = res.replace("[=", "=[")
    # 2. 以 "|" 作为分隔条件，若 "|" 前不存在 "=" 或 " "， 则表示该 "|" 是用于分隔普通参数， 若存在 "=" " ", 则表示该 "|" 是用于分隔命令参数
    res_list = res.split("|")
    # 只考虑最外层的 "|" ，因为只有这种情况下可能出现命令参数的分隔
    flag = is_brackets_match([0, 0, 0, 0], res_list[0])
    if flag and res.__contains__("|"):
        flag = is_command(res_list[0])
        if flag:
            if res_list[1].startswith("-"):
                res = res_list[1]
            else:
                res = "-" + res_list[1]
    return res

def is_command(res):
    """
        判断 "|" 的作用是否是分隔命令,使用"="," "判断

        Args:
            res ([string]): [处理后的某一行参数命令]

        Returns:
            [bool]: [表真假]
    """
    if res.__contains__("=") or res.__contains__(" "):
        return False
    return True

def replace_options(usage_multiple_list, options_one_prefix, options_two_prefix, options):
    """
        将 options 替换为具体的命令参数

        Args:
            usage_multiple_list ([list]): [处理后的参数命令]
            options_one_prefix ([list]): [-开头的短参数命令]
            options_two_prefix ([list]): [--开头的长参数命令]
            options ([list]): [所有参数命令]
        Returns:
            [list]: [完成替换的参数命令]
    """
    res_list = []
    usage_list = []
    for i in range(0, len(usage_multiple_list)):
        usage_list = usage_multiple_list[i]
        index = -1
        for j in range(0, len(usage_list)):
            if str(usage_list[j]).__eq__("[options]") or str(usage_list[j]).__eq__("<options>"):
                index = j
                break
        if index == -1:
            # 对于部分不包含 option 的命令，直接添加原命令
            res_list.append(usage_list.copy())
            continue
        # 区分是否必须带有 options
        flag = False
        if str(usage_list).__contains__("[options]"):
            flag = True
        usage_list.pop(index)
        # 考虑特殊情况处理，若包含[--],说明usage中区分"-"和"--"
        if str(usage_list).__contains__("[--]"):
            index2 = -1
            for j in range(0, len(usage_list)):
                if str(usage_list[j]).__eq__("[--]"):
                    index2 = j
                    usage_list.pop(index2)
                    break
            # index 位置的 options 已移除，index 位置后面元素会左移一位
            if index2 >= index:
                index2 = index2 + 1
            for option in options_one_prefix:
                usage_list.insert(index, option)
                res_list.append(usage_list.copy())
                for e in options_two_prefix:
                    usage_list.insert(index2, e)
                    res_list.append(usage_list.copy())
                    usage_list.pop(index2)
                usage_list.pop(index)
        else:
            for option in options:
                usage_list.insert(index, option)
                res_list.append(usage_list.copy())
                usage_list.pop(index)
        if flag:
            res_list.append(usage_list.copy())
    return res_list

def handle_other_command(usage_multiple_list):
    """
        对已替换完的usage语句中的其他位置进行检测，处理可能出现的参数不独立的情况（合并）

        Args:
            usage_multiple_list ([list]): [处理后的参数命令]
    """
    for i in range(0, len(usage_multiple_list)):
        format_command(usage_multiple_list[i])
    for i in range(0, len(usage_multiple_list)):
        # 可能出现的其他命令参数进行处理
        j = 0
        while j < len(usage_multiple_list[i]):
            if str(usage_multiple_list[i][j]).__contains__("[-"):
                start = re.search("\[-", str(usage_multiple_list[i][j]), re.I).start()
                end = get_range(usage_multiple_list[i][j], start, "[", "]")
            elif str(usage_multiple_list[i][j]).__contains__("<-"):
                start = re.search("<-", str(usage_multiple_list[i][j]), re.I).start()
                end = get_range(usage_multiple_list[i][j], start, "<", ">")
            else:
                j = j + 1
                continue
            temp = str(usage_multiple_list[i][j])
            temp = temp[0:start] + "" + temp[start + 1:end] + "" + temp[end + 1:len(temp)]
            usage_multiple_list[i][j] = temp

def get_range(s, start, str1, str2):
    """
        获取 s 中 与 字符 str1 配对的 str2 的位置

        Args:
            s ([string]): [需要处理的字符串]
            start ([int]): [开始位置]
            str1 ([string]): [字符1]
            str2 ([string]): [字符2]
        Returns:
            [int]: [位置]
    """
    num = 1
    for i in range(start + 1, len(s)):
        if s[i] == str1:
            num = num + 1
        if s[i] == str2:
            num = num - 1
        if num == 0:
            return i
    return 1

def format_command(usage_list):
    """
        # 处理 usage 中每个参数和命令，确保元组中每个位置的元素之间相互独立(前面只判断了括号未判断双引号数量是否匹配，这里额外判定一下)

        Args:
            usage_list ([list]): [参数命令]
    """
    num = 0
    i = 1
    while i < len(usage_list):
        num = num + str(usage_list[i]).count("\"")
        if num % 2 == 0:
            i = i + 1
            num = 0
        else:
            if i + 1 >= len(usage_list):
                break
            usage_list[i] = usage_list[i] + " " + usage_list[i + 1]
            usage_list.pop(i + 1)

def remove_duplicate_parameter(res_multiple_list):
    """
        移除可重复参数

        Args:
            res_multiple_list ([list]): [参数命令]
    """
    for i in range(0, len(res_multiple_list)):
        for j in range(0, len(res_multiple_list[i])):
            res_multiple_list[i][j] = res_multiple_list[i][j].replace("...", "")
            res_multiple_list[i][j] = res_multiple_list[i][j].replace("[]", "")

def parse_options_parameters(usage_multiple_list, global_para_list, content, file_name):
    """
        解析参数命令, 获取 options
        函数入口

        Args:
            usage_multiple_list ([list]): [处理前的参数命令]
            global_para_list ([list]): [位置参数]
            content ([string]): [帮助信息]
            file_name ([string]): [命令名]
        Returns:
            usage_multiple_list ([list]): [处理后的参数命令]
    """
    # 获取处理后的 option
    options_one_prefix, options_two_prefix, options = get_options(content, file_name)
    # 对 usage 中的 options 进行替换
    res_multiple_list = replace_options(usage_multiple_list, options_one_prefix, options_two_prefix, options)
    # 对已替换完的usage语句中的其他位置进行检测，处理可能出现的其他的参数命令与参数不独立的情况
    handle_other_command(res_multiple_list)
    remove_duplicate_parameter(res_multiple_list)
    if global_para_list is None or len(global_para_list) == 0:
        pass
    else:
        # 将全局变量加入每个语句最后
        res = []
        for global_list in global_para_list:
            res_multiple_back_list = copy.deepcopy(res_multiple_list)
            for i in range(0, len(res_multiple_back_list)):
                for res_list in global_list:
                    res_multiple_back_list[i].append(res_list)
                res.append(res_multiple_back_list[i])
        res_multiple_list = copy.deepcopy(res)
    # 去掉每个参数命令最外层括号
    split_parameter_command.remove_outer_bracket(res_multiple_list)

    return res_multiple_list
