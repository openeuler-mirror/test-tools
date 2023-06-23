# Copyright (c) 2022. Huawei Technologies Co.,Ltd.ALL rights reserved.
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
# @Desc      	:   工具入口
#####################################


import install_source_package
import subprocess
import time


if __name__ == '__main__':
    """
    工具入口
    """
    # 设置系统语言
    LANG_EN = True
    previous_lang = ""

    # sub_status, previous_lang = subprocess.getstatusoutput("cat /etc/locale.conf")
    # print("系统现有语言为：", previous_lang)
    # if not previous_lang.__contains__("en"):
    #     print("首先将语言切换为英文！")
    #
    #     # 确认是否已经安装英文语言包
    #     sub_status, sub_res = subprocess.getstatusoutput("locale -a | grep \'en_US.utf8\'")
    #     if sub_status != 0:
    #         sub_status, sub_res = subprocess.getstatusoutput("yum groupinstall \'fonts\' -y")
    #         if sub_status != 0:
    #             print("安装语言失败，无法切换系统语言；后续将按照原有语言处理！")
    #         else:
    #             set_lang_command = "localectl set-locale LANG=en_US.utf8"
    #             sub_status, sub_res = subprocess.getstatusoutput(set_lang_command)
    #             sub_status, sub_res = subprocess.getstatusoutput("source /etc/locale.conf")
    #             sub_status, sub_res = subprocess.getstatusoutput("cat /etc/locale.conf")
    #             print("系统现有语言为：", sub_res)
    #             LANG_EN = False
    #     else:
    #         set_lang_command = "localectl set-locale LANG=en_US.utf8"
    #         sub_status, sub_res = subprocess.getstatusoutput(set_lang_command)
    #         sub_status, sub_res = subprocess.getstatusoutput("source /etc/locale.conf")
    #         sub_status, sub_res = subprocess.getstatusoutput("cat /etc/locale.conf")
    #         print(sub_res)
    #         print("系统现有语言为：", sub_res)
    #         LANG_EN = False

    install_source_package.install_source_package()

    # if not LANG_EN:
    #     set_lang_command = f"localectl set-locale {previous_lang}"
    #     sub_status, sub_res = subprocess.getstatusoutput(set_lang_command)
    #     sub_status, sub_res = subprocess.getstatusoutput("source /etc/locale.conf")
    #     sub_status, sub_res = subprocess.getstatusoutput("cat /etc/locale.conf")
    #     print(sub_res)
    #     print("系统现有语言为：", sub_res)
