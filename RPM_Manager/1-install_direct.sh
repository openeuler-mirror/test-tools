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
    dnf list --all|grep "${test_update_repo}" >all_pkgs_list
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
    update_list_pkgs_num=$(wc -l <update_dnf_list)
    if [[ ${repo_pkgs_num} -eq ${update_list_pkgs_num} ]]; then
        echo "Check update_list packages number success" >>check.log
    else
        echo "Check update_list packages number fail" >>check.log
    fi
    if [ "${openeulerversion}"x == "openEuler-20.03-LTS-SP1"x ]; then
        if [ -s EPOL_update_list ]; then
            curl http://"${service_ip}"/repo.openeuler.org/"${openeulerversion}"/EPOL/"${test_update_repo}"/"$(arch)"/Packages/ >epol_repo_packages
            EPOL_repo_pkgs_num=$(grep -ci ".rpm" epol_repo_packages)
            EPOL_update_list_pkgs_num=$(wc -l <EPOL_update_dnf_list)
            if [[ ${EPOL_repo_pkgs_num} -eq ${EPOL_update_list_pkgs_num} ]]; then
                echo "Check EPOL_update_list packages number success" >>check.log
            else
                echo "Check EPOL_update_list packages number fail" >>check.log
            fi
        else
            echo "EPOL repo is not exist" >>check.log
        fi
    else
        if [ -s EPOL_update_list ]; then
            curl http://"${service_ip}"/repo.openeuler.org/"${openeulerversion}"/EPOL/"${test_update_repo}"/main/"$(arch)"/Packages/ >epol_repo_packages
            EPOL_repo_pkgs_num=$(grep -ci ".rpm" epol_repo_packages)
            EPOL_update_list_pkgs_num=$(wc -l <EPOL_update_dnf_list)
            if [[ ${EPOL_repo_pkgs_num} -eq ${EPOL_update_list_pkgs_num} ]]; then
                echo "Check EPOL_update_list packages number success" >>check.log
            else
                echo "Check EPOL_update_list packages number fail" >>check.log
            fi
        else
            echo "EPOL repo is not exist" >>check.log
        fi
    fi

    #安装
    while read -r pkg; do
        yum install -y "$pkg" >>install_log 2>&1
    done <update_list
    test -s EPOL_update_list && while read -r pkg; do
        yum install -y "$pkg" >>EPOL_install_log 2>&1
    done <EPOL_update_list

    # ko场景测试
    echo "Starting check ko" >> check.log
    rpm -ql $(cat update_list) | grep "\.ko$" | grep -vE "TUTORIAL|gtkrc|mc.hint|README|tutor|kernel" > ko.list
    test -s EPOL_update_list && rpm -ql $(cat EPOL_update_list) | grep "\.ko$" | grep -vE "TUTORIAL|gtkrc|mc.hint|README|tutor" >> ko.list
    while read ko_file
    do
        mod=$(echo ${ko_file} | awk -F/ '{print $NF}'| awk -F '.ko' '{print $1}')
        modprobe ${mod}
        lsmod | grep -w ${mod}
        if [ $? -eq 0 ] ;then
            echo "${mod} check success !" >>check.log
            modprobe -r ${mod}
            lsmod | grep -w ${mod}  
        else
            echo "${mod} check fail !" >>check.log
            insmod ${ko_file}
            if [ $? -eq 0 ] ;then
                echo "${mod} insmod success !" >>check.log
                rmmod ${ko_file}
            else
               echo "${mod} insmod fail !" >>check.log 
            fi
        fi    
    done < ko.list

}

main
