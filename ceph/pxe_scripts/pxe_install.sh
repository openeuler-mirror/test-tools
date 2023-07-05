#!/bin/bash
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
source ./conf

echo ${system_name}|grep _4k_bcache
if [ $? -eq 0 ];then
 source_uefi=${system_name%_4k_bcache}_${arch_name}_uefi
 source_ks=${system_name}_${arch_name}-ks.templete
else
 source_uefi=${system_name}_${arch_name}_uefi
 source_ks=${system_name}_${arch_name}-ks.templete
fi

# step 1 copy uefi
cd /var/lib/tftpboot
target_uefi=auto_uefi/${bmc_ip}_uefi
# clean uefi
rm -rf ${target_uefi}
cp -r ${source_uefi} ${target_uefi}
sed -i "s#bmc_ip#${bmc_ip}#" ${target_uefi}/grub.cfg

# step 2 copy ks
cd /home/PXE/os_install/ks
target_ks=auto_ks/${bmc_ip}-ks.cfg
# clean ks
rm -rf ${target_ks}
cp -r ${source_ks} ${target_ks}
sed -i "s#disk_uuid#${disk_uuid}#" ${target_ks}


sed -i "s#manage_ip#${manage_ip}#" ${target_ks}
sed -i "s#manage_prefix#${manage_prefix}#" ${target_ks}
sed -i "s#manage_gateway#${manage_gateway}#" ${target_ks}

# step 3 modify dhcpd.conf
while true
do

if [[ -e "/dhcp_conf_lock" ]]
then
echo  wait dhcp lock release
sleep 1
continue
else
touch /dhcp_conf_lock
\cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf-bak

modify_line=$(cat -n /etc/dhcp/dhcpd.conf|grep -A 6 "host ${dhcp_ip}"|grep filename|awk '{print $1}')
sed -i "${modify_line}s#filename.*#filename \"${target_uefi}/${efi_name}\";#" /etc/dhcp/dhcpd.conf

systemctl restart dhcpd
if [[ $? -eq 0 ]]
then
echo 'restart dhcpd successed'
rm -f /dhcp_conf_lock
rm -f /etc/dhcp/dhcpd.conf-bak
break
else
echo 'restart dhcpd failed'
\cp /etc/dhcp/dhcpd.conf-bak /etc/dhcp/dhcpd.conf 
rm -f /dhcp_conf_lock
exit 1
fi
fi
done

# start  pxe install
# set disk boot
ipmitool -I lanplus -H ${bmc_ip} -U ${bmc_user} -P ${bmc_pwd} chassis bootdev disk options=persistent
# set pxe boot
ipmitool -I lanplus -H ${bmc_ip} -U ${bmc_user} -P ${bmc_pwd} chassis bootdev pxe options=efiboot
# power reset
ipmitool -I lanplus -H ${bmc_ip} -U ${bmc_user} -P ${bmc_pwd} chassis power reset


