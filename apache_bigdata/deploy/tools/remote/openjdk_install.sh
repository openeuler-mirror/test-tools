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
OPENJDK_TAR_PATH=$1
OPENJDK_NAME=$2
TARGET_PATH=$3

if [ ! -e "${OPENJDK_TAR_PATH}"  ];then
    echo "Please give me openjdk"
    exit 1
fi

echo -e "\033[42;30m ====================Install ${OPENJDK_NAME}==================== \033[0m"

if ! tar -zxf "${OPENJDK_TAR_PATH}" -C "${TARGET_PATH}";then
    echo "Failed to tar -zxf ${OPENJDK_TAR_PATH}"
    exit 1
fi

#chown -R root:root ${TARGET_PATH}/${OPENJDK_NAME}
#chmod -R 755 ${TARGET_PATH}/${OPENJDK_NAME}

#mv $OPENJDK_NAME /usr/local/
if ! cat < "/etc/profile" | grep "^export JAVA_HOME=${TARGET_PATH}/$OPENJDK_NAME";then
    echo "export JAVA_HOME=${TARGET_PATH}/$OPENJDK_NAME" >> /etc/profile
fi

if ! cat < "/etc/profile" | grep "^export PATH=\${JAVA_HOME}/bin:\$PATH"; then
    echo "export PATH=\${JAVA_HOME}/bin:\$PATH">> /etc/profile
fi
echo "Install opejdk Successful"
