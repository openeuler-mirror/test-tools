#! /usr/bin
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

function modify_config(){
    OPEN_JDK_NAME=$1
    ip=''
    for device in $(ip a | grep BROADCAST | grep -v NO-CARRIER | awk '{print $2}')
    do
        Speed=$(ethtool "${device}" | grep Speed: | awk '{print $2}')
        if [ "${Speed}" = '1000Mb/s' ] && [[ $(ifconfig -a | grep -A 2 "${device}"|grep inet| xargs) != "" ]];then
        read -r -a array <<<$(ifconfig -a | grep -A 2 "${device}"|grep inet| xargs)
        ip=${array[1]}
    echo ${array[1]}
    fi
    done

    pwd="/automated/testcase/parameterGroup/config/local_config.py"
    echo "11"
    echo ${ip}
    echo "22"
    echo ${pwd}
    cpu_type=`cat ${pwd} | grep -A 5 ${ip}| grep "cpu_type"| awk '{print $2}' `
    echo ${cpu_type:1:-3}

    system=`cat /etc/system-release | awk '{print $1}' | tr "[:upper:]" "[:lower:]"`
    echo $system

    platform=`cat ${pwd} | grep -A 5 ${ip} | grep "platform" | awk '{print $2}'`
    echo ${platform:1:-3}

    path="/automated/testcase/parameterGroup/config/${platform:1:-2}/$system/${cpu_type:1:-2}/spark/perform_testcase14/client.config"
    echo $path

    spark_task_path="/automated/testcase/parameterGroup/config/${platform:1:-2}/$system/${cpu_type:1:-2}/spark/perform_testcase14/client.config"
    if [[ $OPEN_JDK_NAME == "jdk8u222-b10" ]];then
        sed -i "/spark.executor.extraJavaOptions=-Xms20g/d" ${path}
    else
        sed -i "/spark.conf]/a\spark.executor.extraJavaOptions=-Xms20g" ${path}
    fi
}

if [[ $# -ne 1 ]]; then
    echo -e "\033[1;4;5;31m[Usage1] bash ${0##*/} 请传入jdk文件参数   \033[0m"
    exit 1

fi

modify_config ${OPEN_JDK_NAME}


