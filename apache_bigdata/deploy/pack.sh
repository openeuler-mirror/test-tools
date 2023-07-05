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
source pack_config
tool_root_dir=$(cd $(dirname "$0")/||exit 1;pwd)

############################ functions #####################################

function config_download_tools() {
	os_iso=${tools_os_iso}
	jdk_package=${tools_jdk_package}
	expect_rpm_package=${tools_expect_rpm_package}
	tcl_rpm_package=${tools_tcl_rpm_package}

	config_path=${tool_root_dir}/tools/conf/config
	sed -i "s/os_iso=.*/os_iso=${os_iso}/g" ${config_path}
	sed -i "s/jdk_package=.*/jdk_package=${jdk_package}/g" ${config_path}
	sed -i "s/expect_rpm_package=.*/expect_rpm_package=${expect_rpm_package}/g" ${config_path}
	sed -i "s/tcl_rpm_package=.*/tcl_rpm_package=${tcl_rpm_package}/g" ${config_path}

	bash ${tool_root_dir}/tools/bin/download.sh
}
function modify_component_config() {
	component=$1
	eval component_version='${'${component}_version'}'
	eval component_package='${'${component}_package'}'
	eval component_platform='${'${component}_platform'}'
	if [[ ${online_component} =~ ${component} ]]; then
		is_online=true
	else
		is_online=false
	fi
	config_path=${tool_root_dir}/${component}/conf/config
	sed -i "s/${component}_version=.*/${component}_version=${component_version}/g" ${config_path}
	sed -i "s/package=.*/package=${component_package}/g" ${config_path}
	sed -i "s/platform=.*/platform=${component_platform}/g" ${config_path}
}
function download_component_package() {
	component=$1
	rm -rf ${tool_root_dir}/${component}/deps*

	eval component_version='${'${component}_version'}'
	eval component_package='${'${component}_package'}'
	eval component_platform='${'${component}_platform'}'
	if [[ ${online_component} =~ ${component} ]]; then
		is_online=true
	else
		is_online=false
	fi
	if [ "${is_online}" == "true" ]; then
		## on_line -> download
		bash ${tool_root_dir}/${component}/bin/download/download.sh
	else
		## off_line -> generate directory
		tar_path=${tool_root_dir}/${component}/deps/${component_platform}/${component_version}
		mkdir -p ${tar_path}
	fi
}
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
	# remove tez from component_chain, when installed cdh hive
	source hive/conf/config
	if [ ${platform} == "CDH" ]; then
		component_chain=${component_chain/,tez/}
	fi
}
function pack_component_chain() {
	comp_chain=${1}
	config_download_tools
	comp_list=($(echo ${comp_chain[*]}| sed 's/,/\n/g'| uniq))
	for comp in ${comp_list[@]}
	do
		echo ------------------------------------/--
		echo [WARNING] START PACK ${comp}
		echo ------------------------------------/--
		cp -r ${comp} ${comp}_bak
		modify_component_config ${comp}
		download_component_package ${comp}
		tar -rvf ${tool_root_dir}/packed.tar.gz ${comp}
		rm -rf ${comp}
		mv ${comp}_bak ${comp}
	done
	tar -rvf ${tool_root_dir}/packed.tar.gz tools
}

############################ execute #####################################

component=${1}
param_str_comp='zookeeper|hadoop|tez|kafka|hive|storm|spark|hbase|flink|elastic|redis'
if [ $# -eq 1 ]; then
    if [[ ${param_str_comp} =~ ${component} ]]; then                                      
	config_component_chain ${component}
	pack_component_chain ${component_chain}                      
	exit 0
    fi                                            
fi   
echo "[Usage] bash ${0##*/} ${param_str_comp}"
