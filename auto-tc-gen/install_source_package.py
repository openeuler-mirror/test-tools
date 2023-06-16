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
scr_dir = config.get('Directories', 'scr_dir', fallback=current_dir)

# 将路径转换为绝对路径,便于直接使用
download_dir = os.path.abspath(download_dir) + "/"
build_dir = os.path.abspath(build_dir) + "/"
log_dir = os.path.abspath(log_dir) + "/"
scr_dir = os.path.abspath(scr_dir) + "/"

package_name = ""

def install_source_package():
    """
    下载与安装源码包
    """
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
        if not os.path.exists(cur_log_dir):
            os.makedirs(cur_log_dir)
        log.info("第一步：下载源码包", f"{cur_log_dir}{package}.txt")
        command = f"yumdownloader --source {package} --destdir {download_dir}{package}/"
        sub_status, sub_res = subprocess.getstatusoutput(command)
        if sub_status != 0:
            log.error("源码包 " + package + " 下载失败", cur_log_dir + "" + package + ".txt")
            continue
        else:
            log.info("源码包 " + package + " 下载成功", cur_log_dir + "" + package + ".txt")
        source_dir = download_dir + "" + package + "/"
        sub_status, sub_res = subprocess.getstatusoutput(f"ls {source_dir}")
        source_name = sub_res
        log_file = f"{cur_log_dir}{package}.txt"
        log.info("第二步：安装源码包", log_file)
        if not os.path.exists(build_dir + "" + package + "/"):
            os.makedirs(build_dir + "" + package + "/")
        install_command = f"rpm -ivh --define '_topdir {build_dir}{package}/' {source_dir}{source_name}"
        sub_status, sub_res = subprocess.getstatusoutput(install_command)
        if sub_status != 0:
            log.error("SRPM包 " + source_name + " 安装失败", log_file)
            continue
        else:
            log.info("SRPM包 " + source_name + " 安装完成", log_file)
        log.info("第三步：使用 yum install 的方式安装软件包", log_file)
        sub_status, sub_res = subprocess.getstatusoutput("yum list installed | grep" + " " + package)
        if len(str(sub_res)) == 0:
            sub_status, sub_res = subprocess.getstatusoutput("yum install -y" + " " + package)
            if sub_status != 0:
                log.error("软件包 " + package + " 安装失败", log_file)
            else:
                log.info("软件包 " + package + " 安装完成", log_file)
        else:
            log.info("软件包 " + package + " 已存在，无需安装", log_file)
        # 便于后续模块存储时使用
        global package_name
        package_name = package
        compile_rpm_package.compile_rpm_package(build_dir + "" + package +"/", log_file)

if __name__ == '__main__':
    """
    工具入口
    """
    # 初始化参数映射
    parameter_classify.initialize_parameters()
    # 安装源码包
    install_source_package()