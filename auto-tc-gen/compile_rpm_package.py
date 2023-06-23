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
# @Desc      	:   软件包编译
#####################################

#coding=UTF-8

import subprocess
import re

from logger import log
import transform_rpm_package
from extract_source_code import construct_test_cases


def get_rpm_name_path(sub_res_list, build_dir):
    """
    获取需要安装的rpm包路径

    Args:
        sub_res_list ([list]): [文件编译中的输出信息]
        build_dir ([string]): [build目录]

    Returns:
        [list]: rpm包路径
    """
    rpm_list = []
    for res in sub_res_list:
        if not (res.startswith("Wrote:") or res.startswith("已写至：")):
            continue
        if res.startswith(f"Wrote: {build_dir}SRPMS/") or res.startswith(f"Wrote: {build_dir}RPMS/"):
            res = res.split("Wrote:")[1].strip()
            rpm_list.append(res)
        if res.startswith(f"已写至：{build_dir}SRPMS/") or res.startswith(f"已写至：{build_dir}RPMS/"):
            res = res.split("已写至：")[1].strip()
            rpm_list.append(res)
    return rpm_list


def automatic_install_dependency(sub_res_list, log_file):
    """
    依赖的自动导入

    Args:
        sub_res_list ([list]): [文件编译中的输出信息]
        log_file ([string]): [日志打印目录]
    """
    dependency_list = []
    for res in sub_res_list:
        if res.__contains__(" is needed by "):
            dependency_list.append(res.split(" is needed by ")[0].strip().split(" ")[0])
        if res.__contains__("需要"):
            dependency_list.append(res.split(" 被 ")[0].strip().split(" ")[0])
        if res.__contains__("缺少"):
            dependency_list.append(res.split("缺少")[0].strip().split(" ")[0])
    for res in dependency_list:
        if res.startswith("perl(") and res.endswith(")"):
            res = res[5:len(res) - 1]
            sub_status, sub_res = subprocess.getstatusoutput("cpan " + res)
        else:
            sub_status, sub_res = subprocess.getstatusoutput("yum install -y " + res)
        if sub_status != 0:
            log.error("依赖 " + res + " 导入失败", log_file)
        else:
            log.info("依赖 " + res + " 导入成功", log_file)

def inspect_install(name, log_file):
    """
    检查与安装环境中需要安装的软件包

    Args:
        name ([string]): [包名]
        log_file ([string]): [日志打印目录]
    """
    sub_status, sub_res = subprocess.getstatusoutput("yum list installed | grep" + " " + name)
    if len(str(sub_res)) == 0:
        sub_status, sub_res = subprocess.getstatusoutput("yum install -y" + " " + name)
        if sub_status != 0:
            log.error("环境中缺少软件包 " + name + " ，自动安装失败", log_file)

def compile_rpm_package(build_dir, log_file, package):
    """
    软件包编译

    Args:
        build_dir ([string]): [build文件目录]
        log_file ([string]): [日志打印目录]
        package ([string]): [包名]
    """
    spec_address = build_dir + "SPECS/"
    print("第三步：编译软件包")
    sub_status, sub_res = subprocess.getstatusoutput(f"ls {spec_address}")
    name = sub_res
    # 检查与安装 rpm-build 、cpan包
    inspect_install("rpm-build", log_file)
    inspect_install("perl-CPAN", log_file)
    compile_command = f"rpmbuild -ba --define='_topdir {build_dir}' {spec_address}{name}"
    sub_status, sub_res = subprocess.getstatusoutput(compile_command)
    sub_res_list = sub_res.split('\n')
    if len(sub_res_list) > 0 and re.search(" is needed by |缺少|需要", sub_res_list[len(sub_res_list)-1]):
        log.debug("------开始自动导入依赖------", log_file)
        # 依赖的自动导入,( is needed by )
        automatic_install_dependency(sub_res_list, log_file)
        sub_status, sub_res = subprocess.getstatusoutput(compile_command)
        sub_res_list = sub_res.split('\n')
        if sub_status != 0:
            log.debug("软件包 " + name + " 自动导入依赖失败", log_file)
        else:
            log.debug("软件包 " + name + " 自动导入依赖成功", log_file)
    # 获取需要安装的rpm包路径
    rpm_list = get_rpm_name_path(sub_res_list, build_dir)
    # 打印编译失败的情况
    if not sub_res_list[-1].__contains__("exit 0"):
        print("软件包 " + name + " 编译失败")
        print("第四步：改用 yum install 的方式安装软件包")
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
        print("软件包 " + name + " 编译成功")
        transform_rpm_package.transform_rpm_package(rpm_list, build_dir, log_file, package)