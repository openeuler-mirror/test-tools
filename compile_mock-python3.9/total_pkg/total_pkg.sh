#!/usr/bin/bash

# Copyright (c) [2021] Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# ##################################
# @CaseName  :   test_mockbuild_001.sh
# @Author    :   zengcongwei/zhujinlong
# @Contact   :   735811396@qq.com
# @Date      :   2021/11/11
# @Version   :   V2.0
# @Desc      :   test rpm build with mock
# ##################################

source ../common/common_lib.sh

function parameter_check() {
	if [ ${para_num} -ne 1 ]; then
		echo "Please enter the correct option format!"
		exit 1
		echo "Usage: sh mockbuild.sh [all/pkg_name]"
	fi
}

function config_params() {
	echo "start config_params"
	sys_type=$(arch)
	TEST_PATH=$(pwd)
	rm -f fail_pkg.log
	#cpu core num
	core_num=$(grep </proc/cpuinfo -c processor)
	#package number
	total_pkg=$(wc -l <../common/source_list)
	echo "end config_params"
}

function pre_test() {
	echo "start pre_test"
	INSTALL_MOCK
	if [ -d /tmp/srcrpms ]; then
		rm -rf /tmp/srcrpms/*
	else
		mkdir /tmp/srcrpms
	fi
	echo "end pre_test"
}

function run_test() {
	echo "start run_test"
	start_pkg=1
	if [[ ${para_name}X != "all"X || ${core_num} -lt ${total_pkg} ]]; then
		max_loop=${core_num}
	else
		max_loop=${total_pkg}
	fi
	end_pkg=${max_loop}
	#全量编译
	if [ ${para_name}X == "all"X ]; then
		user_num=1
		mapfile -t pkg_list < <(sed -n "${start_pkg},${end_pkg}p" ../common/source_list)
		for pkg in "${pkg_list[@]}"; do
			cp ../common/openEuler-${sys_type}.cfg /tmp/${pkg}_build-${sys_type}.cfg
			sed -i 's/cfg-name/'${pkg}'_build_env/g' /tmp/${pkg}_build-${sys_type}.cfg
			config_file=/tmp/${pkg}_build-${sys_type}.cfg
			BUILD_PKG "$pkg" "$config_file" "mockbuild_${user_num}"
			((user_num++))
		done

		while true; do
			#正在进行的mock编译进程数
			ret=$(ps -ef | grep "mock -q -r" | grep "su" | wc -l)
			#全部编译完成，退出
			if [ ${end_pkg} -ge ${total_pkg} ] && [ ${ret} -eq 0 ]; then
				break
			fi
			#有编译完成就加入新的包进行编译
			if [ ${end_pkg} -lt ${total_pkg} ] && [ ${ret} -lt ${max_loop} ]; then
				let start_pkg=${end_pkg}+1
				let rest=${max_loop}-${ret}
				let end_pkg=${start_pkg}-1+${rest}
				mapfile -t pkg_list < <(sed -n "${start_pkg},${end_pkg}p" ../common/source_list)

				for pkg in "${pkg_list[@]}"; do
					cp ../common/openEuler-${sys_type}.cfg /tmp/${pkg}_build-${sys_type}.cfg
					sed -i 's/cfg-name/'${pkg}'_build_env/g' /tmp/${pkg}_build-${sys_type}.cfg
					config_file=/tmp/${pkg}_build-${sys_type}.cfg
					BUILD_PKG "$pkg" "$config_file" "mockbuild_${user_num}"
					((user_num++))
				done
			fi
			sleep 10
		done
		fail_num=$(wc -l <"$TEST_PATH"/fail_pkg.log)

	#单个编译
	else
		if ! grep <../common/source_list ^${para_name}; then
			echo "No such package,please confirm!"
		else
			cp ../common/openEuler-${sys_type}.cfg /tmp/${para_name}_build-${sys_type}.cfg
			sed -i 's/cfg-name/'${para_name}'_build_env/g' /tmp/${para_name}_build-${sys_type}.cfg
			config_file=/tmp/${para_name}_build-${sys_type}.cfg
			BUILD_PKG "$para_name" "$config_file" "mockbuild"
			while true; do
				if ! ps -ef | grep "mock -q -r" | grep "su"; then
					break
				fi
				sleep 10
			done
			fail_num=$(wc -l <"$TEST_PATH"/fail_pkg.log)
		fi
	fi
	echo "end run_test"
}

function post_test() {
	echo "start post_test"
	REMOVE_MOCK
	rm -rf /tmp/srcrpms
	echo "end post_test"
}

main() {
	parameter_check
	config_params
	pre_test
	run_test
	post_test
}

para_num=$#
para_name=$1
main "$@"
