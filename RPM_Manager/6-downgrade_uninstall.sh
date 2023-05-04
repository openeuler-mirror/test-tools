#!/bin/bash
# @Author: zjl_long
# @Date:   2022-02-09 21:06:00
# @Last Modified time: 2023-04-19 19:35:57
#
# Desc: Downgrade and uninstall software packages
# msg: No arguments need to be passed.
#

source ./common.sh

main() {
    cd /home/pkg_manager_folder || exit 1
    #降级
    while read -r pkg; do
        yum downgrade -y "$pkg" >>downgrade_log 2>&1
    done <update_list
    test -s EPOL_update_list && while read -r pkg; do
        yum downgrade -y "$pkg" >>EPOL_downgrade_log 2>&1
    done <EPOL_update_list

    #卸载
    uninstall_pkg
}

main
