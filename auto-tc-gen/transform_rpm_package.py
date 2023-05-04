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
# @Date      	:   2023-4-28 12:00:00
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   RPM 包解压
#####################################

#coding=UTF-8

import subprocess
import logging
from help_parse import extract_source_code as help_parse_extract_source_code

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_possible_rpm_name(suffix, rpm_possible_name_list, source_list):
    """
    由源码包名称，拼接出 noarch 与 x86_64 两个目录下的可能存在的 rpm 包名称

    Args:
        suffix ([string]): [前缀]
        rpm_possible_name_list ([list]): [可能需要解压的rpm包名称]
        source_list ([list]): [rpm包路径]
    """
    for source in source_list:
        source_name_list = source.split('.')
        source_name = ""
        for i in range(0, len(source_name_list) - 2):
            source_name = source_name + "" + source_name_list[i] + "."
        source_name = source_name + "" + suffix + ".rpm"
        rpm_possible_name_list.append(source_name)

def get_rpm_name(suffix, rpm_possible_name_list, rpm_name_list):
    """
    # 获取需要解压的 rpm 包名称

    Args:
        suffix ([string]): [前缀]
        rpm_possible_name_list ([list]): [可能需要解压的rpm包名称]
        rpm_name_list ([list]): [需要解压的rpm包名称]
    """
    rpm_address = "/root/rpmbuild/RPMS/" + suffix
    status, res = subprocess.getstatusoutput("ls" + " " + rpm_address)
    for name in res.split('\n'):
        if rpm_possible_name_list.__contains__(name):
            rpm_name_list.append(name)

def converted_package(rpm_multiple_list, pre_name_list):
    """
        根据 rpm_multiple_list 中包含的包名与路径，解压rpm包

        Args:
            rpm_multiple_list ([list]): [需要解压的rpm包名称]
            pre_name_list ([list]): [rpm包存放目录前缀]
        """
    for rpm_list in rpm_multiple_list:
        if rpm_list and len(rpm_list) != 0:
            rpm_name = rpm_list[0]
            pre_name = "/root/rpmbuild/CPIO/" + rpm_name + "/"
            pre_name_list.append(pre_name)
            subprocess.getstatusoutput("mkdir -p " + pre_name)
            for i in range(1, len(rpm_list)):
                subprocess.getstatusoutput("rm -rf ./usr/")
                sub_status, sub_res = subprocess.getstatusoutput("rpm2cpio " + rpm_list[i] + " | cpio -div")
                # rpm2cpio后默认在当前目录(也就是python程序存放的目录，测试环境中为/home/tmp/pythonProject),将安装产生的文件剪切到指定位置
                subprocess.getstatusoutput("cp -r ./usr/ " + pre_name)
                subprocess.getstatusoutput("rm -rf ./usr/")
                if sub_status != 0:
                    logging.error("RPM包 " + rpm_list[i] + " 解压失败")
                else:
                    logging.info("RPM包 " + rpm_list[i] + " 解压成功")

def transform_rpm_package(source_list, rpm_multiple_list):
    """
    解压 rpm 包

    Args:
        source_list ([list]): [rpm包路径]
        rpm_multiple_list ([list]): [需要解压的rpm包名称]
    """
    print(" ")
    print("-----------------------------------------")
    print("第三步： 解压rpm包")
    print("-----------------------------------------")
    print(" ")
    print("已检测到的rpm包为：")

    for rpm_list in rpm_multiple_list:
        if rpm_list is not None and len(rpm_list) != 0:
            for i in range(1, len(rpm_list)):
                print(rpm_list[i])

    # 记录所有可能存在的，需要转换的 rpm 包名称
    rpm_possible_name_list = []
    get_possible_rpm_name("noarch", rpm_possible_name_list, source_list)
    get_possible_rpm_name("x86_64", rpm_possible_name_list, source_list)

    # 记录两种需要解压的 rpm 包名称
    rpm_name_noarch_list = []
    rpm_name_x86_list = []
    get_rpm_name("noarch", rpm_possible_name_list, rpm_name_noarch_list)
    get_rpm_name("x86_64", rpm_possible_name_list, rpm_name_x86_list)

    print(" ")
    print("开始解压rpm包")

    # 记录解压后的包路径
    pre_name_list = []
    converted_package(rpm_multiple_list, pre_name_list)

    print(" ")
    print("rpm文件解压完成后存放的位置为： ")
    for rpm in pre_name_list:
        print(rpm)
    help_parse_extract_source_code.extract_source_code(pre_name_list, 1)
