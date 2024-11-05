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
tool_root_dir=$(cd $(dirname "$0")||exit 1;pwd)
timeout=300

component_chain=''
deploy_tag_file='/root/installed_components'

################################## functions ################################################

function config_component_chain() {
	comp=${1}

	if [ ${comp} == 'hadoop' ]; then
		component_chain='zookeeper,hadoop'
	elif [ ${comp} == 'hive' ]; then
		component_chain='zookeeper,hadoop,tez,hive'
	
	elif [ ${comp} == 'spark' ]; then
		component_chain='zookeeper,hadoop,tez,hive,spark'
	elif [ ${comp} == 'hbase' ]; then
		component_chain='zookeeper,hadoop,hbase'
	elif [ ${comp} == 'flink' ]; then
		component_chain='zookeeper,hadoop,flink'
	elif [ ${comp} == 'kafka' ]; then
		component_chain='zookeeper,kafka'
	elif [ ${comp} == 'storm' ]; then
		component_chain='zookeeper,storm'
	else
		component_chain=${comp}
	fi

	# remove tez from component_chain, when install cdh hive
	source hive/conf/config
	if [ ${platform} == "CDH" ]; then
		component_chain=${component_chain/,tez/}
	fi
}

function config_uninstall_chain() {
        comp=${1}
        uninstall_chain=${comp}
}

function deploy_component() {
	comp=${1}

	# alive -> return
	bash ${tool_root_dir}/${comp}/bin/common/check_status.sh check_process
	if [ $? == 0 ]; then
		echo [INFO] ${comp} PROCESS IS ACTIVE
		return 	
	fi
		
	bash ${tool_root_dir}/${comp}/bin/common/check_status.sh check_install
	if [ $? == 0 ]; then
		# exist -> start
		echo [INFO] ${comp} WAS INSTALLED
		echo [INFO] ${comp} IS STARTING...
		timeout -s SIGKILL ${timeout} bash $tool_root_dir/${comp}/bin/*tool*.sh start
	else
		# -> deploy
		echo [INFO] ${comp} IS DEPLOYING...
		source /etc/profile
		bash ${tool_root_dir}/${comp}/bin/*tool*.sh deploy
		sleep 1

		# record deploy history
		time_str=$(date '+%Y/%m/%d %H:%M:%S')
		echo ${comp} ${time_str} >> ${deploy_tag_file}
	fi
}

function deploy_component_chain() {
	comp_chain=${1}
	comp_list=($(echo ${comp_chain[*]}| sed 's/,/\n/g'| uniq))
	for comp in ${comp_list[@]}
	do
		echo ------------------------------------/--
		echo [WARNING] START DEPLOY ${comp}
		echo ------------------------------------/--
		deploy_component ${comp}
	done
}

function check_basic_env() {
#   source ${tool_root_dir}/tools/conf/config
#   echo ${target_path}/${jdk_name}
#   if [ -d "${target_path}/${jdk_name}" ]; then
#      echo "[INFO] deployed...tools"
#   else
#      echo "[INFO] deploying...tools"
#      bash ${tool_root_dir}/tools/run.sh
#   fi
    basic_env=$(cat "/root/basic_env")
    if [ "${basic_env}" = "basic_env is finished" ];then
      echo "[INFO] deployed...tools"
    else
      echo "[INFO] deploying...tools"
      bash ${tool_root_dir}/tools/run.sh
    fi
}

function install_all_component() {
    check_basic_env
    component_chain='zookeeper,hadoop,tez,hive,spark,hbase,flink,kafka,storm,elasticsearch,redis'
    ## remove tez from component_chain, when install cdh hive
    source hive/conf/config
    if [ ${platform} == "CDH" ]; then
    	component_chain=${component_chain/,tez/}
    fi
    deploy_component_chain ${component_chain}
    echo "onekey exec success..."
    exit 0
}

function install_select_component() {
    component_chain=${1}
    check_basic_env
    #component_chain='zookeeper,hadoop,tez,hive,spark,hbase,flink,kafka,storm,elasticsearch,redis'
    ## remove tez from component_chain, when install cdh hive
    source hive/conf/config
    if [ ${platform} == "CDH" ]; then
        component_chain=${component_chain/,tez/}
    fi
    deploy_component_chain ${component_chain}
    echo "onekey exec success..."
    exit 0
}


function uninstall_component() {
	comp=${1}
	bash ${tool_root_dir}/${comp}/bin/*tool*.sh uninstall
	sed -i "/^${comp}.*/d" ${deploy_tag_file}
}

function uninstall_all_component() {
  echo "uninstall_all_component"
  read -r -a component_list<<<$(cat ${deploy_tag_file} | awk '{print $1}' | xargs)
  n=1
  num=${#component_list[*]}
  while [ ${n} -le ${num} ]; do
      comp=${component_list[${num}-${n}]}
      echo ------------------------------------/--
      echo [WARNING] START UNINSTALL ${comp}
      echo ------------------------------------/--
      expect <<EOF
      set timeout 600
      spawn bash ${tool_root_dir}/${comp}/bin/deploy/uninstall.sh
      expect {
              "please input 'yes' to confirm" { send "yes\r";exp_continue }
              "Are You Sure To Uninstall? " { send "Y\r";exp_continue }
              "Type 'yes' to continue." { send "yes\r";exp_continue }
              }
EOF
      sed -i "/^${comp}.*/d" ${deploy_tag_file}
      let "n++"
  done


}

function uninstall_uninstall_chain() {
	comp_chain=${1}
        comp_list=($(echo ${comp_chain[*]}| sed 's/,/\n/g'| uniq))
        for comp in ${comp_list[@]}
        do
              echo ------------------------------------/--
              echo [WARNING] START UNINSTALL ${comp}
              echo ------------------------------------/--
              uninstall_component ${comp}
        done
}

function stop_component() {
	component=${1}
	search_ret=$(cat ${deploy_tag_file} |grep "^${component}.*"|awk '{print $1}')
	echo ${search_ret}
	if [ -z ${search_ret} ]; then
			echo "********** ${component} must installed **********"
			exit 0
	elif [ ${search_ret} = ${component} ]; then
	
		timeout -s SIGKILL $timeout bash ${tool_root_dir}/${component}/bin/switch/stop.sh
		sleep 1
		# bash ${tool_root_dir}/${component}/bin/common/check_status.sh check_alive
		
		if [ $? != 0 ]; then 
			echo ${component} stop failed
			exit 0
		else
			echo ${component} stop successfully
			exit 0 
		fi
	fi
}

function start_component() {
	component=${1}
	search_ret=$(cat ${deploy_tag_file} |grep "^${component}.*"|awk '{print $1}')
	echo ${search_ret}

	if [ -z ${search_ret} ]; then
		echo "********** ${component} must installed **********"
		exit 0
	elif [ ${search_ret} = ${component} ]; then
	
		timeout -s SIGKILL $timeout bash $tool_root_dir/$component/bin/switch/start.sh
		sleep 10
		bash ${tool_root_dir}/${component}/bin/common/check_status.sh check_alive

		if [ $? != 0 ]; then
			echo ${component} start failed
			exit 1
		else
			echo ${component} start successfully
			exit 0
		fi
	fi
}

function start_process() {
    component=$1
    operate=$2
	if [ ${operate} == 'uninstall' ]; then
		config_uninstall_chain ${component}
		uninstall_uninstall_chain ${uninstall_chain}
	elif [ ${operate} == 'stop' ]; then
		stop_component ${component}
	elif [ ${operate} == 'start' ]; then
		start_component ${component}
	elif [ ${operate} == 'deploy' ]; then
		check_basic_env
		config_component_chain ${component}
		deploy_component_chain ${component_chain}
	else
		echo PROCESS : ${operate} is not denied ...
	fi
}

################################## execute ################################################
input_param_1=$1
input_param_2=$2
input_param_3=$3
param_str_comp='zookeeper|hadoop|tez|kafka|hive|storm|spark|hbase|flink|elasticsearch|redis'
param_str_oper='deploy|uninstall|start|stop|restart'


if [ $# -eq 1 ]; then
    if [ "install_all" = $1 ]; then
        install_all_component
    elif [ "uninstall_all" = $1 ]; then
        uninstall_all_component
    else
        echo "[Usage] bash ${0##*/} ${param_str_comp}"
    fi

    echo "onekey exec success..."
    exit 0
fi

if [ $# -eq 2 ]; then
    if [[ ${param_str_comp} =~ ${input_param_1} ]] && [[ ${param_str_oper} =~ ${input_param_2} ]]; then
      start_process ${input_param_1} ${input_param_2}
    elif [[ ${param_str_comp} =~ ${input_param_2} ]] && [[ ${param_str_oper} =~ ${input_param_1} ]]; then
      start_process ${input_param_2} ${input_param_1}
    else
      echo "[Usage] bash ${0##*/} ${param_str_comp} ${param_str_oper}"
    fi
    echo "onekey exec success..."
    exit 0
fi

if [ $# -eq 3 ]; then
    if [ "install_select" = $1 ] && [ "true" = $3 ]; then
        echo -e "\033[1;4;4;32m  ${input_param_2} \033[0m"
        install_select_component ${input_param_2}


        echo "222"
    else 
        echo -e "\033[1;4;4;34m[Usage1] 参数有误 \033[0m"
    fi
    echo "onekey exec success..."
    exit 0
fi

echo "[Usage] bash ${0##*/} uninstall_all|install_all or [Usage] bash ${0##*/} ${param_str_comp} ${param_str_oper}"
