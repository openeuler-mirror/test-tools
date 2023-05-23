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
import logging
import transform_rpm_package


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_rpm_name_path(sub_res_list):
    """
    获取包名与需要安装的rpm包路径

    Args:
        sub_res_list ([list]): [文件编译中的输出信息]

    Returns:
        [string]: rpm包名
        [list]: rpm包路径
    """
    rpm_name = ""
    rpm_list = []
    for res in sub_res_list:
        if not res.startswith("Wrote:"):
            continue
        if res.startswith("Wrote: /root/rpmbuild/SRPMS/"):
            rpm_name = res.split("Wrote: /root/rpmbuild/SRPMS/")[1]
            rpm_name_list = rpm_name.split(".")
            rpm_name = rpm_name_list[0]
            for i in range(1, len(rpm_name_list) - 2):
                rpm_name = rpm_name + "." + rpm_name_list[i]
        if res.startswith("Wrote: /root/rpmbuild/RPMS/"):
            res = res.split("Wrote:")[1].strip()
            rpm_list.append(res)
    return rpm_name, rpm_list


def automatic_install_dependency(sub_res_list):
    """
    依赖的自动导入

    Args:
        sub_res_list ([list]): [文件编译中的输出信息]
    """
    dependency_list = []
    for res in sub_res_list:
        if res.__contains__(" is needed by "):
            dependency_list.append(res.split(" is needed by ")[0].strip().split(" ")[0])
    for res in dependency_list:
        if res.startswith("perl(") and res.endswith(")"):
            res = res[5:len(res) - 1]
            sub_status, sub_res = subprocess.getstatusoutput("cpan " + res)
        else:
            sub_status, sub_res = subprocess.getstatusoutput("yum install -y " + res)
        if sub_status != 0:
            logging.error("依赖 " + res + " 导入失败")
        else:
            logging.info("依赖 " + res + " 导入成功")

def inspect_install(name):
    """
        检查与安装环境中需要安装的软件包

        Args:
            name ([string]): [包名]
        """
    sub_status, sub_res = subprocess.getstatusoutput("yum list installed | grep" + " " + name)
    if len(str(sub_res)) == 0:
        sub_status, sub_res = subprocess.getstatusoutput("yum install -y" + " " + name)
        if sub_status != 0:
            logging.error("环境中缺少软件包 " + name + " ，自动安装失败")

def compile_rpm_package(source_list):
    """
    软件包编译

    Args:
        source_list ([list]): [SPEC文件列表]
    """

    print(" ")
    print("-----------------------------------------")
    print("第二步：编译rpm包")
    print("-----------------------------------------")
    print(" ")
    print("已检测到的spec文件为：")
    spec_address = "/root/rpmbuild/SPECS"
    status, res = subprocess.getstatusoutput("ls " + spec_address)
    for spec in res.split('\n'):
        print(spec)
    print(" ")
    print("开始编译rpm包")
    # 记录需要安装的rpm包路径
    rpm_multiple_list = []
    # 检查与安装 rpm-build 、cpan包
    inspect_install("rpm-build")
    inspect_install("perl-CPAN")
    for name in res.split('\n'):
        sub_status, sub_res = subprocess.getstatusoutput("rpmbuild -ba" + " " + spec_address + "/" + name)
        sub_res_list = sub_res.split('\n')
        if len(sub_res_list) > 0 and sub_res_list[len(sub_res_list) - 1].__contains__(" is needed by "):
            print("------开始自动导入依赖------")
            # 依赖的自动导入,( is needed by )
            automatic_install_dependency(sub_res_list)
            sub_status, sub_res = subprocess.getstatusoutput("rpmbuild -ba" + " " + spec_address + "/" + name)
            sub_res_list = sub_res.split('\n')
            if sub_status != 0:
                logging.error("软件包 " + name + " 自动导入依赖失败")
            else:
                logging.info("软件包 " + name + " 自动导入依赖成功")
        # 获取包名与需要安装的rpm包路径
        rpm_name, rpm_list = get_rpm_name_path(sub_res_list)
        if rpm_name != "" and len(rpm_list) != 0:
            # 将包名插入第一个位置，与rpm需要安装的包路径放在一起
            rpm_list.insert(0, rpm_name)
            rpm_multiple_list.append(rpm_list)
        # 打印编译失败的情况
        if not sub_res_list[len(sub_res_list)-1].__contains__("exit 0"):
            logging.error("软件包 " + name + " 编译失败")
        else:
            logging.info("软件包 " + name + " 编译成功")
    transform_rpm_package.transform_rpm_package(source_list, rpm_multiple_list)
