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

import os
import re
import subprocess
import queue
from logger import log
import extract_source_code


def converted_package(rpm_list, build_dir, log_file):
    """
    根据 rpm_list 中包含的rpm包路径，解压rpm包

    Args:
        rpm_list ([list]): [需要解压的rpm包名称]
        build_dir ([string]): [build目录]
        log_file ([string]): [日志打印目录]
    """
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    for rpm in rpm_list:
        converted_command = f"rpm2cpio {rpm} | cpio -div -D {build_dir}"
        sub_status, sub_res = subprocess.getstatusoutput(converted_command)
        if sub_status != 0:
            log.debug("RPM包 " + rpm + " 解压失败", log_file)
            return
        else:
            log.debug("RPM包 " + rpm + " 解压成功", log_file)

def package_in_queue(package_name, rpm_names):
    """
    判断package_name在不在rpm_names里面

    Args:
        package_name (string): [缺失的包名称]
        rpm_names ([string]): [当前编译成功的rpm包名称]
    """
    for rpm_name in rpm_names:
        rpm_name_pre = re.split(r"-[0-9]+", rpm_name)[0]
        package_name_pre = re.split(r"-[0-9]+", package_name)[0]
        if rpm_name_pre == package_name_pre:
            return True
    return False

def rpm_install(rpm_list, log_file):
    """
    根据rpm包的路径列表，安装所有rpm；要先安装依赖
    Args:
        rpm_list ([list]): [需要安装的rpm包名称]
        log_file ([string]): [日志打印目录]
    """
    rpm_path_queue = queue.Queue()
    rpm_names = []
    # 将文件添加到队列中
    for rpm in rpm_list:
        rpm_path_queue.put(rpm)
        rpm_names.append(rpm.split('/')[-1])

    # 记录失败的文件，用于通过判断同一个包两次失败之间是否有成功安装
    # 如果有成功的，不会存在同一个包第二次失败的时候已经出现在该列表中
    # 如果没有成功的，则会出现第二次失败时已经记录在该列表中了，即无法正确安装更多包，可以停止了
    fail_list = []

    while not rpm_path_queue.empty():
        rpm_path = rpm_path_queue.get()
        install_command = f"rpm -ivh {rpm_path}"
        sub_status, sub_res = subprocess.getstatusoutput(install_command)
        if sub_status != 0:
            # 失败可能是缺少依赖，也可能是已经安装；
            # 如果已经安装则忽略
            if sub_res.__contains__(" already ") or sub_res.__contains__("已经"):
                fail_list.clear()
                continue
            # 如果是缺依赖，先安装不属于我们编译好的那些依赖；然后依然加入到队列中，等待下一次安装
            if re.search(" is needed by |缺少|需要", sub_res):
                sub_res_list = sub_res.split('\n')
                for sub_res_item in sub_res_list:
                    if re.search(" is needed by |缺少|需要", sub_res_item):
                        # 获取缺失的依赖包的名字
                        package_name = sub_res_item.split(" is needed by ")[0].strip().split(" ")[0]
                        # 判断依赖包是否在我们的rpm包里面：如果有rpm包以缺失依赖包名字开头，则存在；否则不存在
                        # 不存在，则立刻yum install package_name
                        if not package_in_queue(package_name, rpm_names):
                            if package_name.startswith("perl(") and package_name.endswith(")"):
                                package_name = package_name[5:len(package_name) - 1]
                                new_sub_status, sub_res = subprocess.getstatusoutput("cpan " + package_name)
                            else:
                                new_sub_status, sub_res = subprocess.getstatusoutput("yum install -y " + package_name)
                            if new_sub_status != 0:
                                log.error("依赖 " + package_name + " 安装失败", log_file)
                            else:
                                log.info("依赖 " + package_name + " 安装成功", log_file)
            rpm_path_queue.put(rpm_path)
            if rpm_path in fail_list:
                break
            fail_list.append(rpm_path)
        else:
            fail_list.clear()

    if len(fail_list) == 0:
        print("所有rpm包安装成功")
        return 0
    elif len(rpm_list) > len(fail_list) > 0:
        print("部分rpm包安装成功；失败的是：")
        for failed_rpm_path in fail_list:
            print(failed_rpm_path)
        return 0
    else:
        print("所有rpm包都安装失败")
        return 1

def transform_rpm_package(rpm_list, build_dir, log_file, package):
    """
    解压 rpm 包

    Args:
        rpm_list ([list]): [rpm包路径]
        build_dir ([string]): [build目录]
        log_file ([string]): [日志打印目录]
        package ([string]): [包名]
    """
    print("第四步：解压rpm包")
    log.debug("已检测到的rpm包为: ", log_file)
    for rpm in rpm_list:
        log.debug(f"{rpm}", log_file)

    log.debug("开始解压rpm包", log_file)

    converted_package(rpm_list, build_dir+"CPIO/", log_file)

    print(f"rpm文件解压完成后存放的位置为：{build_dir}CPIO/")

    print("第五步：安装rpm包")
    rpm_install(rpm_list, log_file)

    extract_source_code.extract_source_code(build_dir+"CPIO/", log_file, package)
