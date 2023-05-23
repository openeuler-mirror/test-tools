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
# @Desc      	:   源码包安装
#####################################

#coding=UTF-8

import logging
import subprocess
import compile_rpm_package
from help_parse import parameter_classify

is_auto = "y"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def install_source_package(address):
    """
    安装源码包

    Args:
        address ([string]): [源码包本地目录]
    """
    print(" ")
    print("-----------------------------------------")
    print("第一步：安装源码包（XXX.src.rpm）")
    print("-----------------------------------------")
    print(" ")
    source_list = []
    status, res = subprocess.getstatusoutput("ls" + " " + address)
    print("已检测到的源码包为： ")
    for src_rpm in res.split('\n'):
        if src_rpm.endswith(".src.rpm"):
            print(src_rpm)
            source_list.append(src_rpm)

    # 使用 dnf install 的方式安装软件包，便于后续使用预设值自动生成测试用例时测试
    print("使用 yum install 的方式安装源码包")
    for rpm in res.split('\n'):
        rpm = rpm.lstrip()
        name_list = rpm.split("-")
        name = name_list[0]
        for i in range(1, len(name_list)):
            if name_list[i].isspace():
                continue
            if 0 <= ord(name_list[i][0]) - ord('0') <= 9:
                break
            name = name + "-" + name_list[i]
        sub_status, sub_res = subprocess.getstatusoutput("yum list installed | grep" + " " + name)
        if len(str(sub_res)) == 0:
            sub_status, sub_res = subprocess.getstatusoutput("yum install -y" + " " + name)
            if sub_status != 0:
                logging.error("软件包 " + name + " 安装失败")
            else :
                logging.info("软件包 " + name + " 安装完成")
        else:
            logging.info("软件包 " + name + " 已存在，无需安装")

    for name in res.split('\n'):
        sub_status, sub_res = subprocess.getstatusoutput("rpm -ivh" + " " + str(address) + "/" + name)
        if sub_status != 0:
            logging.error("SRPM包 " + name + " 安装失败")
        else:
            logging.info("SRPM包 " + name + " 安装完成")

    compile_rpm_package.compile_rpm_package(source_list)

def input_directory():
    """
        获取本地源码包路径
    """
    print("请输入是否需要全自动生成测试用例 [y/n]")
    global is_auto
    is_auto = input()
    print("请输入本地源码包路径, 例如：/root/test (默认为 /root/test)")
    address = input()
    if is_auto == '':
        is_auto = "y"
    if address == '':
        address = "/root/test"
    status, res = subprocess.getstatusoutput("ls" + " " + address)
    address_flag = False
    for name in res.split('\n'):
        if name.endswith(".src.rpm"):
            address_flag = True
            break
    if not address_flag:
        logging.info("输入的地址中不包含源码包")
        return

    # 初始化参数映射
    parameter_classify.initialize_parameters()
    # 安装源码包
    install_source_package(address)

if __name__ == '__main__':
    """
    工具入口
    """
    input_directory()