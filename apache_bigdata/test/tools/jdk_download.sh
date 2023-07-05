#! /usr/bin/bash
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
OPEN_JDK_NAME=$1

if [[ $# -ne 1 ]]; then
    echo -e "\033[1;4;5;31m[Usage1] bash ${0##*/} 清传入jdk文件参数\033[0m"
    exit 1

fi

if [ ! -e /usr/local/jdk8u282-b08_bak ];then
    cd /usr/local
    mv jdk8u282-b08 jdk8u282-b08_bak
fi

if [ ! -e /usr/local/$OPEN_JDK_NAME ] && [ ${OPEN_JDK_NAME} != jdk8u282-b08 ];then
    echo -e "\033[1;4;5;32m  jdk_file is not exists!!, start to download\033[0m"
    wget -P /root  http://90.90.61.222/Bigdata/Tools/toolsFactory/ambariDeploy/${OPEN_JDK_NAME}.tar.gz
    tar -zxf /root/${OPEN_JDK_NAME}.tar.gz
    chown -R root:root $OPEN_JDK_NAME
    chmod -R 755 $OPEN_JDK_NAME
    mv $OPEN_JDK_NAME /usr/local/
fi

echo [INFO] jdk is success download
    cd /usr/local
    if [ ${OPEN_JDK_NAME} != jdk8u282-b08 ];then
        ln -snf ${OPEN_JDK_NAME} jdk8u282-b08
    else
        ln -snf jdk8u282-b08_bak jdk8u282-b08
    fi


sed -i "/JAVA_HOME/d" /etc/profile
cat /etc/profile | grep "export JAVA_HOME=/usr/local/$OPEN_JDK_NAME"
if [ $? != 0 ];then
        echo "export JAVA_HOME=/usr/local/$OPEN_JDK_NAME" >> /etc/profile
        echo -e "\033[1;4;5;32m  export insert to profile finished\033[0m"
fi

cat /etc/profile | grep 'export PATH=$JAVA_HOME/bin:$PATH'
if [ $? != 0 ];then
        echo -e "\033[1;4;5;32m export insert to path finished\033[0m"
        echo 'export PATH=$JAVA_HOME/bin:$PATH'>> /etc/profile
fi

