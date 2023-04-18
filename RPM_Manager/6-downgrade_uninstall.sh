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
    yum downgrade -y $(cat update_list) --skip-broken 2>&1 | tee downgrade_log
    test -s EPOL_update_list && yum downgrade -y "$(cat EPOL_update_list)" --skip-broken 2>&1 | tee EPOL_downgrade_log

    #卸载
    uninstall_pkg
}

main
