#!/bin/bash
# @Author: zjl_long
# @Date:   2022-02-09 21:06:00
# @Last Modified time: 2023-04-28 14:50:54
#
# Desc: Direct upgrade
# msg: Two parameters need to be passed, one for the original version and the other for the target version.
#

source ./common.sh
rm -rf /etc/yum.repos.d/* /home/pkg_manager_folder

#安装
install_pkg() {
    original_ver=$1
    target_ver=$2
    if [ "${original_ver}"x == "${target_ver}"x ]; then
        dnf config-manager --disable "${target_ver}_${test_update_repo}"
        test -s EPOL_update_list && dnf config-manager --disable "${target_ver}_EPOL_${test_EPOL_update_repo}"
    else
        mv /etc/yum.repos.d/"${target_ver}".repo /etc/yum.repos.d/"${target_ver}".repo.bak
    fi
    yum clean all
    while read -r pkg; do
        yum install -y "$pkg" >>install_log
    done <update_list
    test -s EPOL_update_list && while read -r pkg; do
        yum install -y "$pkg" >>EPOL_install_log
    done <EPOL_update_list
}

#升级到测试版本
upgrade_test_pkg() {
    original_ver=$1
    target_ver=$2
    if [ "${original_ver}"x == "${target_ver}"x ]; then
        dnf config-manager --enable "${target_ver}_${test_update_repo}"
        test -s EPOL_update_list && dnf config-manager --enable "${target_ver}_EPOL_${test_EPOL_update_repo}"
    else
        mv /etc/yum.repos.d/"${target_ver}".repo.bak /etc/yum.repos.d/"${target_ver}".repo
    fi
    while read -r pkg; do
        yum upgrade -y "$pkg" >>update_log 2>&1
    done <update_list
    test -s EPOL_update_list && while read -r pkg; do
        yum upgrade -y "$pkg" >>EPOL_update_log 2>&1
    done <EPOL_update_list
}

main() {
    original_ver=$1
    target_ver=$2
    echo "Input original version: ${original_ver}, target version: ${target_ver}"
    test_update_repo=$(curl http://"${service_ip}"/repo.openeuler.org/"${target_ver}"/"${target_ver}"-update.json | grep dir | grep "[0-9]" | grep -v test | grep -v round | awk -F \" '{print $4}' | awk -F "/" '{print $1}' | sort | uniq | tail -n 1)
    test_EPOL_update_repo=$(curl http://"${service_ip}"/repo.openeuler.org/"${target_ver}"/EPOL/"${target_ver}"-update.json | grep dir | grep "[0-9]" | grep -v test | awk -F \" '{print $4}' | awk -F "/" '{print $1}' | sort | uniq | tail -n 1 | awk -F "|" '{print $1}')

    #Configure original repo source
    configure_original_repo "${original_ver}"
    #Configure target repo source
    configure_target_repo "${target_ver}"
    #Get the package lists
    get_related_lists "${target_ver}"

    install_pkg "${original_ver}" "${target_ver}"
    upgrade_test_pkg "${original_ver}" "${target_ver}"
}

main "$@"
