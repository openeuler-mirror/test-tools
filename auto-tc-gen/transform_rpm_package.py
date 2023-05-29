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
import subprocess
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
            log.error("RPM包 " + rpm + " 解压失败", log_file)
            return
        else:
            log.info("RPM包 " + rpm + " 解压成功", log_file)

def transform_rpm_package(rpm_list, build_dir, log_file):
    """
    解压 rpm 包

    Args:
        rpm_list ([list]): [rpm包路径]
        build_dir ([string]): [build目录]
        log_file ([string]): [日志打印目录]
    """
    log.info("第五步：解压rpm包", log_file)
    log.info("已检测到的rpm包为：", log_file)
    for rpm in rpm_list:
        log.info(f"{rpm}", log_file)

    log.info("开始解压rpm包", log_file)

    converted_package(rpm_list, build_dir+"CPIO/", log_file)

    log.info(f"rpm文件解压完成后存放的位置为：{build_dir}CPIO/", log_file)
    extract_source_code.extract_source_code(build_dir+"CPIO/", log_file)
