#!/bin/bash
# @Author: zjl_long
# @Date:   2022-02-09 21:06:00
# @Last Modified time: 2023-04-28 14:52:22
#
# Desc: Indirect upgrade
# msg: Two parameters need to be passed, one for the original version and the other for the target version.
#

source ./common.sh
rm -rf /etc/yum.repos.d/* /home/pkg_manager_folder

#获取update_list中间版本
get_mid_pkg() {
    while read -r pkg_name; do
        if [[ $(yum provides "$pkg_name" --repo="${original_ver}_update" | grep "x86\|arch" | awk '{print $1}' | wc -l) -eq 0 ]]; then
            echo "$pkg_name" >>no_mid-ver_update_list
            echo "There is no mid-version of the $pkg_name."
        else
            yum provides "$pkg_name" --repo="${original_ver}_update" | grep "x86\|arch" | awk '{print $1}' >/tmp/"${pkg_name}"_list
            num_pkg_name=$(grep -c "$pkg_name" /tmp/"${pkg_name}"_list)
            if rpm -qa "$pkg_name" | grep "$pkg_name"; then
                # 中间版本
                if [ "$num_pkg_name" -le 2 ]; then
                    echo "$pkg_name" >>no_mid-ver_update_list
                    echo "There is no mid-version of the $pkg_name."
                else
                    mid_pkg_name=$(grep -v "$(rpm -qa "$pkg_name" | awk -F '-' '{printf $3"-"$4}')" /tmp/"${pkg_name}"_list | sed '$d' | shuf -n 1)
                    yum upgrade -y "$mid_pkg_name" >>pre_update_log
                fi
            else
                # 首次安装的软件包
                mid_pkg_name=$(sed '$d' /tmp/"${pkg_name}"_list | shuf -n 1)
                yum upgrade -y "$mid_pkg_name" >>pre_update_log
            fi
        fi
    done <update_list
}

#获取EPOL_update_list中间版本
get_EPOL_mid_pkg() {
    while read -r EPOL_pkg_name; do
        if [[ $(yum provides "$EPOL_pkg_name" --repo="${original_ver}_EPOL_update" | grep "x86\|arch" | awk '{print $1}' | wc -l) -eq 0 ]]; then
            echo "$EPOL_pkg_name" >>no_mid-ver_EPOL_update_list
            echo "There is no mid-version of the $EPOL_pkg_name."
        else
            yum provides "$EPOL_pkg_name" --repo="${original_ver}_EPOL_update" | grep "x86\|arch" | awk '{print $1}' >/tmp/"${EPOL_pkg_name}"_list
            num_EPOL_pkg_name=$(grep -c "$EPOL_pkg_name" /tmp/"${EPOL_pkg_name}"_list)
            if rpm -qa "$EPOL_pkg_name" | grep "$EPOL_pkg_name"; then
                # 中间版本
                if [ "$num_EPOL_pkg_name" -le 2 ]; then
                    echo "$EPOL_pkg_name" >>no_mid-ver_EPOL_update_list
                    echo "There is no mid-version of the $EPOL_pkg_name."
                else
                    mid_EPOL_pkg_name=$(grep -v "$(rpm -qa "$EPOL_pkg_name" | awk -F '-' '{printf $3"-"$4}')" /tmp/"${EPOL_pkg_name}"_list | sed '$d' | shuf -n 1)
                    yum upgrade -y "$mid_EPOL_pkg_name" >>pre_EPOL_update_log
                fi
            else
                # 首次安装的软件包
                mid_EPOL_pkg_name=$(sed '$d' /tmp/"${EPOL_pkg_name}"_list | shuf -n 1)
                yum upgrade -y "$mid_EPOL_pkg_name" >>pre_EPOL_update_log
            fi
        fi
    done <EPOL_update_list
}

#安装
install_pkg() {
    original_ver=$1
    target_ver=$2
    if [ "${original_ver}"x == "${target_ver}"x ]; then
        dnf config-manager --disable "${target_ver}_update" "${target_ver}_EPOL_update" "${target_ver}_${test_update_repo}"
        test -s EPOL_update_list && dnf config-manager --disable "${target_ver}_EPOL_${test_EPOL_update_repo}"
    else
        dnf config-manager --disable "${original_ver}_update" "${original_ver}_EPOL_update"
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

#升级到update的中间版本
upgrade_mid_pkg() {
    original_ver=$1
    dnf config-manager --enable "${original_ver}_update" "${original_ver}_EPOL_update"
    get_mid_pkg
    if [ -s EPOL_update_list ]; then
        get_EPOL_mid_pkg
    fi
}

#升级到测试版本
upgrade_test_pkg() {
    original_ver=$1
    target_ver=$2
    if [ "${original_ver}"x == "${target_ver}"x ]; then
        dnf config-manager --enable "${target_ver}_${test_update_repo}"
    else
        mv /etc/yum.repos.d/"${target_ver}".repo.bak /etc/yum.repos.d/"${target_ver}".repo
    fi
    test -s EPOL_update_list && dnf config-manager --enable "${target_ver}_EPOL_${test_EPOL_update_repo}"
    yum upgrade -y $(cat update_list) --skip-broken 2>&1 | tee update_log
    test -s EPOL_update_list && yum upgrade -y "$(cat EPOL_update_list)" --skip-broken 2>&1 | tee EPOL_update_log
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
    upgrade_mid_pkg "${original_ver}"
    upgrade_test_pkg "${original_ver}" "${target_ver}"
}

main "$@"
