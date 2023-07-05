#!/usr/bin/bash
# Copyright (c) 2023. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   hekeming
# @Contact   :   hk16897@126.com
# @Date      :   2023/07/03
# @License   :   Mulan PSL v2
# @Desc      :   Test SSH link
# ############################################
# release=$(cat /etc/system-release|sed -r 's/.* ([0-9]+)\..*/\1/')
echo -e "\033[42;30m ====================Firewall is closing==================== \033[0m"
#case $release in
#    7)
systemctl disable firewalld.service
systemctl stop firewalld.service
echo "Firewall has closed"
#    ;;
#    1)
#    systemctl disable firewalld.service
#    systemctl stop firewalld.service
#    echo "Firewall has closed"
#    ;;
#    6)
#    service stop iptables
#    chkconfig iptables off
#    echo "Firewall has closed"
#    ;;
#    *)
#    echo "Failed to close firewall"
#    ;;
#esac
