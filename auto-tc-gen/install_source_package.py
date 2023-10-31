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

import os
import subprocess
import configparser
from logger import log
import compile_rpm_package
from help_parse import parameter_classify
from extract_source_code import construct_test_cases

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 读取配置文件
config = configparser.ConfigParser()
config.read('./config.ini')
# 从配置文件中获取日志打印存放目录和脚本文件存放目录
# 包括工具是否需要全自动、源码包下载目录、日志打印存放目录、脚本文件存放目录
download_dir = config.get('Directories', 'download_dir', fallback=current_dir)
build_dir = config.get('Directories', 'build_dir', fallback=current_dir)
log_dir = config.get('Directories', 'log_dir', fallback=current_dir)

# 将路径转换为绝对路径,便于直接使用
download_dir = os.path.abspath(download_dir) + "/"
build_dir = os.path.abspath(build_dir) + "/"
log_dir = os.path.abspath(log_dir) + "/"

package_name = ""

######################################################
#关于安装源码包、编译和解析，以及yum install的步骤的说明：
# （1）安装完源码包通过编译和解析获得源代码和可执行的文件，安装源码包有三个作用：
#      首先可以获得源码，判断编程语言类型；
#      其次，可以通过解析源代码获得待测命令；
#      最后，在源码解析失败的时候，也可以用直接通过解析到的源码脚本执行-h等命令获得待测命令；
# （2）在源码包安装失败的时候，启动yum install，通过help提示解析命令；
# （3）在源码包成功安装但编译失败的时候，也启动yum install，通过help提示解析命令
#
def install_source_package():
    """
    下载与安装源码包
    """
    # 初始化参数映射
    parameter_classify.initialize_parameters()
    # 从配置文件中读取软件包名称
    packages = config.get("Packages", "packages").split(",")
    # 创建日志打印目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # 下载软件包的 src.rpm 文件
    for package in packages:
        package = package.strip()
        # 创建下载目录
        if not os.path.exists(download_dir + "" + package + "/"):
            os.makedirs(download_dir + "" + package + "/")
        cur_log_dir = log_dir + "" + package + "/"
        log_file = f"{cur_log_dir}{package}.txt"
        if not os.path.exists(cur_log_dir):
            os.makedirs(cur_log_dir)
        print("第一步：下载源码包")
        command = f"yumdownloader --source {package} --destdir {download_dir}{package}/"
        sub_status, sub_res = subprocess.getstatusoutput(command)
        if sub_status != 0:
            print("源码包 " + package + " 下载失败")
            continue
        else:
            print("源码包 " + package + " 下载成功")
        source_dir = download_dir + "" + package + "/"
        sub_status, sub_res = subprocess.getstatusoutput(f"ls {source_dir}")
        source_name = sub_res

        print("第二步：安装源码包")
        if not os.path.exists(build_dir + "" + package + "/"):
            os.makedirs(build_dir + "" + package + "/")
        install_command = f"rpm -ivh --define '_topdir {build_dir}{package}/' {source_dir}{source_name}"
        sub_status, sub_res = subprocess.getstatusoutput(install_command)
        if sub_status != 0:
            print("SRPM包 " + source_name + " 安装失败")
            print("第三步：改用 yum install 的方式安装软件包")
            sub_status, sub_res = subprocess.getstatusoutput("yum list installed | grep" + " " + package)
            if len(str(sub_res)) == 0:
                sub_status, sub_res = subprocess.getstatusoutput("yum install -y" + " " + package)
                if sub_status != 0:
                    print("软件包 " + package + " 安装失败")
                else:
                    print("软件包 " + package + " 安装完成")
            else:
                print("软件包 " + package + " 已存在，无需安装")
            # 这里只能根据help去解析命令并生成脚本
            # 因为没有源码，所以命令名称就是package名称，命令路径为空，脚本的语言类型是不知道的
            construct_test_cases("", package, log_file, package, "UnKnown")
        else:
            print("SRPM包 " + source_name + " 安装完成")
            # 便于后续模块存储时使用
            global package_name
            package_name = package
            compile_rpm_package.compile_rpm_package(build_dir + "" + package +"/", log_file, package)

if __name__ == '__main__':
    """
    工具入口
    """
    # 安装源码包
    install_source_package()