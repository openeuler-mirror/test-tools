#!/bin/bash
# @Author: zjl_long
# @Date:   2022-01-25 11:19:31
# @Last Modified time: 2023-04-18 11:10:33
#
# Desc: Uninstall software packages directly
# msg: No arguments need to be passed.
#

source ./common.sh

main() {
    cd /home/pkg_manager_folder || exit 1
    #卸载
    uninstall_pkg
}

main
