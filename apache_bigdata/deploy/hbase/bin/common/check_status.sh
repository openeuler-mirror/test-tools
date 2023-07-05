#!/bin/bash
source /etc/profile
tool_root_dir=$(cd "$(dirname "$0")"/../..||exit 1;pwd)
source "${tool_root_dir}/conf/config"
SERVER_PROCESS_NAME=HMaster
AGENT_PROCESS_NAME=HRegionServer
INSTALL_DIR=${hbase_dir}/hbase-${hbase_version}

read -r -a node_list <<< "${regionserver_list//,/ }"

function check_process() {
    command=$(ps -ef | grep -w ${SERVER_PROCESS_NAME} | grep -v grep -c)
    echo "${command} ${SERVER_PROCESS_NAME} alive on server"
	if [ "${command}" -lt 1 ]; then
        echo "${SERVER_PROCESS_NAME} alive less then 1"
		exit 1
	fi
	command="ps -ef | grep -w ${AGENT_PROCESS_NAME} | grep -v grep -c"
        for agent in "${node_list[@]}"
            do
                result=$(ssh "${agent}" "${command}")
                echo "${result} ${AGENT_PROCESS_NAME} alive  on ${agent}"
                if [ "${result}" -lt 1 ];then
                    echo "${AGENT_PROCESS_NAME} alive less then 1"
                    exit 1
                fi
            done
    echo "hbase process check ok"
}

function check_install() {
    if [ -d "${INSTALL_DIR}" ]; then
        echo "hbase install check ok"
        exit 0
    else
        echo "hbase is not install"
        exit 1
    fi
}

function check_alive() {
    input_file=check_alive_hbase_input
    output_file=check_alive_hbase_output

    # generate sql file
    echo 'create "check_alive_test_table", "id", "name"' > ${input_file}
    echo 'list' >> ${input_file}
    echo 'exit' >> ${input_file}

    # execute
    hbase shell ${input_file}>${output_file} 2>/dev/null

    # check ERROR
    check_cmd=$(grep -R ERROR ${output_file})
    if [[ -z ${check_cmd} ]]; then
        result_value=0
    else
        result_value=1
    fi

    # clear file
    echo 'disable "check_alive_test_table"' > ${input_file}
    echo 'drop "check_alive_test_table"' >> ${input_file}
    echo 'exit' >> ${input_file}
    # to avoid execute disable .. or drop .. when no hbase started
    if [ ${result_value} -eq 0 ]; then
        hbase shell ${input_file}>${output_file} 2>/dev/null
    fi
    rm -f ${input_file}
    rm -f ${output_file}

    # return result
    if [ ${result_value} -eq 0 ]; then
        echo "hbase is alive"
        exit 0
    else
        echo "hbase is not alive"
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
