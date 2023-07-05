ntp_server=$1
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
if [ ! "${ntp_server}" ];then
    echo need ntp_server!!!
    exit 1
fi
public_net=$(echo ${ntp_server%.*}).0/24
yum -y install chrony
[[ $? -ne 0 ]] && echo "install chrony failed" && exit 1
if [[ -f /etc/chrony.conf ]];then
mv /etc/chrony.conf /etc/chrony.conf-bak
ip a show |grep ${ntp_server}
if [ $? -eq 0 ];then
cat > /etc/chrony.conf <<EOF
allow ${public_net}
local stratum 5
server ${ntp_server} iburst
makestep 1.0 3
EOF
else
cat > /etc/chrony.conf <<EOF
server ${ntp_server} iburst
makestep 1.0 3
EOF
fi
systemctl start chronyd.service
systemctl enable chronyd.service
timedatectl set-timezone Asia/Shanghai
chronyc -a makestep
timedatectl set-ntp true
systemctl restart chronyd.service
hwclock -w
fi
