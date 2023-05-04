#!/bin/bash
# @Author: zjl_long
# @Date:   2022-01-29 16:21:44
# @Last Modified time: 2023-04-28 14:53:43
#
# Desc: Basic function check, Install and uninstall software packages directly
# msg: No arguments need to be passed.
#

source ./common.sh
rm -rf /etc/yum.repos.d/* /home/pkg_manager_folder

main() {
    test_update_repo=$(curl http://"${service_ip}"/repo.openeuler.org/"${openeulerversion}"/"${openeulerversion}"-update.json | grep dir | grep "[0-9]" | grep -v test | grep -v round | awk -F \" '{print $4}' | awk -F "/" '{print $1}' | sort | uniq | tail -n 1)
    test_EPOL_update_repo=$(curl http://"${service_ip}"/repo.openeuler.org/"${openeulerversion}"/EPOL/"${openeulerversion}"-update.json | grep dir | grep "[0-9]" | grep -v test | awk -F \" '{print $4}' | awk -F "/" '{print $1}' | sort | uniq | tail -n 1 | awk -F "|" '{print $1}')
    configure_target_repo "${openeulerversion}"
    get_related_lists "${openeulerversion}"

    #验证版本后缀
    suffix_name=$(echo "${kernelversion}" | awk -F "." '{print $NF}')
    dnf list --all >all_pkgs_list
    grep "noarch\|aarch64\|x86_64" all_pkgs_list | grep -v "$suffix_name" | grep -v "$openeulerversion" >>error_suffix_name_pkgs_list
    if [ -s error_suffix_name_pkgs_list ]; then
        echo "Check suffix fail" >>check.log
    else
        echo "Check suffix success" >>check.log
        rm -f error_suffix_name_pkgs_list all_pkgs_list
    fi

    #验证获取到的软件包个数与repo中是否一致
    curl http://"${service_ip}"/repo.openeuler.org/"${openeulerversion}"/"${test_update_repo}"/"$(arch)"/Packages/ >repo_packages
    repo_pkgs_num=$(grep -ci ".rpm" repo_packages)
    update_list_pkgs_num=$(wc -l <update_list)
    if [[ ${repo_pkgs_num} -eq ${update_list_pkgs_num} ]]; then
        echo "Check update_list packages number success" >>check.log
    else
        echo "Check update_list packages number fail" >>check.log
    fi
    if [ "${openeulerversion}"x == "openEuler-20.03-LTS-SP1"x ]; then
        if [ -s EPOL_update_list ]; then
            curl http://"${service_ip}"/repo.openeuler.org/"${openeulerversion}"/EPOL/"${test_update_repo}"/"$(arch)"/Packages/ >epol_repo_packages
            EPOL_repo_pkgs_num=$(grep -ci ".rpm" epol_repo_packages)
            EPOL_update_list_pkgs_num=$(wc -l <EPOL_update_list)
            if [[ ${EPOL_repo_pkgs_num} -eq ${EPOL_update_list_pkgs_num} ]]; then
                echo "Check EPOL_update_list packages number success" >>check.log
            else
                echo "Check EPOL_update_list packages number fail" >>check.log
            fi
        else
            echo "EPOL repo is not exit" >>check.log
        fi
    else
        if [ -s EPOL_update_list ]; then
            curl http://"${service_ip}"/repo.openeuler.org/"${openeulerversion}"/EPOL/"${test_update_repo}"/main/"$(arch)"/Packages/ >epol_repo_packages
            EPOL_repo_pkgs_num=$(grep -ci ".rpm" epol_repo_packages)
            EPOL_update_list_pkgs_num=$(wc -l <EPOL_update_list)
            if [[ ${EPOL_repo_pkgs_num} -eq ${EPOL_update_list_pkgs_num} ]]; then
                echo "Check EPOL_update_list packages number success" >>check.log
            else
                echo "Check EPOL_update_list packages number fail" >>check.log
            fi
        else
            echo "EPOL repo is not exit" >>check.log
        fi
    fi

    #安装
    yum install -y $(cat update_list) --skip-broken 2>&1 | tee install_log
    test -s EPOL_update_list && yum install -y "$(cat EPOL_update_list)" --skip-broken 2>&1 | tee EPOL_install_log

}

main
