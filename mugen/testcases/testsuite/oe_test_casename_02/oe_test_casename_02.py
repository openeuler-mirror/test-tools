#!/usr/bin/python3

# Copyright (c) 2020. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
# @Author    	:   lemon.higgins
# @Contact   	:   lemon.higgins@aliyun.com
# @Date      	:   2020-04-09 09:39:43
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   Take the test ls command as an example
#####################################


import subprocess

ret = 0

cmd_status = subprocess.getstatusoutput("ls -CZl --all")[0]
if cmd_status != 0:
    ret += 1

dir_num = subprocess.getoutput(
    "ls / | grep -cE 'proc|usr|roor|var|sys|etc|boot|dev'")
if dir_num != "7":
    ret += 1

exit(ret)
