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
tool_root_dir=$(cd "$(dirname "$0")"/../..||exit 1;pwd)
source "${tool_root_dir}"/conf/config
PROCESS_NAME=QuorumPeerMain
INSTALL_DIR=${zookeeper_dir}/${package%.tar*}

read -r -a node_list <<< "${zookeeper_list//,/ }"

function check_process() {
        command="ps -ef |grep -w ${PROCESS_NAME}|grep -v grep|wc -l"

        for agent in "${node_list[@]}"
        do
                result=$(ssh "${agent}" "${command}")

                if [ "${result}" -le 0 ];then                   
                   exit 1
                fi
        done
}

function check_install() {
        command="test -d ${INSTALL_DIR}"

        for agent in "${node_list[@]}"
        do
                if ssh "${agent}" "${command}"; then
                   echo "[INFO] ${agent} ${INSTALL_DIR} exist"
                else
                   exit 1
                fi
        done
}

function check_alive() {

agent=${node_list[0]}
file=/check_alive_zookeeper.sh

# generate remote script file
ssh "${agent}" > /dev/null 2>&1 << eeooff
touch ${file}
echo '#!/bin/bash' > ${file}
echo 'input_file=./inputf' >> ${file}
echo 'output_file=./outputf' >> ${file}
echo '# set a data' >> ${file}
echo 'echo "create /check_alive_key check_alive_value" > \${input_file}' >> ${file}
echo 'bash ${zookeeper_dir}/zookeeper/bin/zkCli.sh < \${input_file} > /dev/null'  >> ${file}
echo '# get the data' >> ${file}
echo 'echo "get /check_alive_key" > \${input_file}' >> ${file}
echo 'var=\$(bash ${zookeeper_dir}/zookeeper/bin/zkCli.sh < \${input_file})' >> ${file}
echo '## collection result and analyze' >> ${file}
echo 'echo \$var > \${output_file}' >> ${file}
echo 'check_cmd=\`grep -R "/check_alive_key check_alive_value" \${output_file}\`' >> ${file}
echo 'if [[ -z \${check_cmd} ]]; then' >> ${file}
echo 'result_value=1' >> ${file}
echo 'else' >> ${file}
echo 'result_value=0' >> ${file}
echo 'fi' >> ${file}
echo '# remove' >> ${file}
echo 'echo "delete /check_alive_key" > \${input_file}' >> ${file}
echo 'bash ${zookeeper_dir}/zookeeper/bin/zkCli.sh < \${input_file} > /dev/null' >> ${file}
echo 'rm -f \${input_file}' >> ${file}
echo 'rm -f \${output_file}' >> ${file}
echo '# return result' >> ${file}
echo 'if [ \${result_value} -eq 0 ]; then' >> ${file}
echo 'exit 0' >> ${file}
echo 'else' >> ${file}
echo 'exit 1' >> ${file}
echo 'fi' >> ${file}
chmod +x ${file}
exit
eeooff

# execute remote script file
result=$(ssh "${agent}" "source /etc/profile; bash ${file}")
if [ $? -eq 0 ]; then
        result_value=0
else
        result_value=1
fi

# clear
ssh "${agent}" "rm -f ${file}"

# return result
if [ ${result_value} -eq 0 ]; then
    echo "zookeeper is alive"
    exit 0
else
    echo "zookeeper is not alive"
    exit 1
fi

}

if [[ $# -ne 1 ]]; then
    echo "Usage: bash ${0##*/} check_alive|check_install|check_process"
    exit 1
fi

case ${1} in
    check_alive)
        check_process
        check_alive
        ;;
    check_install)
        check_install
        ;;
    check_process)
        check_process
        ;;
    *)  echo "[Usage] bash ${0##*/} check_alive|check_install|check_process"
        exit 1
        ;;
esac
