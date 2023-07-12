# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
# @Author    	:   hourui
# @Contact   	:   softgreet@qq.com
# @Date      	:   2023-10-12 12:00:00
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   python中参数解析
#####################################

#coding=UTF-8

from enum import Enum
import subprocess
import locale
import itertools
import ast

# 比较两个抽象语法树是否相同
def compare_ast(node1, node2):
    if type(node1) is not type(node2):
        return False
    if isinstance(node1, ast.AST):
        if node1._fields != node2._fields:
            return False
        for k in node1._fields:
            if not compare_ast(getattr(node1, k), getattr(node2, k)):
                return False
        return True
    elif isinstance(node1, list):
        if len(node1) != len(node2):
            return False
        return all(itertools.starmap(compare_ast, zip(node1, node2)))
    else:
        return node1 == node2

class FileType(Enum):
    SRCRPM = 'src.rpm file'
    RPM = 'rpm file'
    EXE = 'other script except shell|py|perl'
    PYTHON = 'python script'
    SHELL = 'shell script'
    PERL = 'perl script'
    ELF = 'elf file'
    LINK = 'link file'
    OTHER = 'other file'
    NOTFILE = 'not file'

    def get_linked_file(link: str):
        ret = subprocess.run(args='file -b \'' + link + '\'', stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, shell=True, encoding=locale.getpreferredencoding())
        if ret.returncode == 0:
            output = ret.stdout.strip().lower()
            if output.find('symbolic link') != -1:
                target = output.split(' ')[-1]
                if target[0] != '/':
                    if target.startswith('./'):
                        target = target.lstrip('./')
                    target = link[:link.rfind('/') + 1] + target
                return target
            else:
                return link
        else:
            raise Exception(ret.stdout)

    def filetype(filename: str):
        ret = subprocess.run(args='file -b \'' + filename + '\'', stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, shell=True, encoding=locale.getpreferredencoding())
        if ret.returncode == 0:
            output = ret.stdout.lower()
            if output.find('cannot open') != -1:
                return FileType.NOTFILE
            elif output.find('rpm') != -1:
                if output.find('bin') != -1:
                    return FileType.RPM
                elif output.find('src') != -1:
                    return FileType.SRCRPM
            elif output.find('executable') != -1:
                if output.find('python') != -1:
                    return FileType.PYTHON
                elif output.find('shell') != -1:
                    return FileType.SHELL
                elif output.find('perl') != -1:
                    return FileType.PERL
                elif output.find('elf') != -1:
                    return FileType.ELF
                else:
                    return FileType.EXE
            elif output.find('symbolic link') != -1:
                return FileType.LINK
            else:
                return FileType.OTHER