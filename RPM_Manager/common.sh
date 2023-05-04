#!/bin/bash
# @Author: zjl_long
# @Date:   2022-02-09 21:06:00
# @Last Modified time: 2023-04-28 14:54:50
#
# Desc: common_functions
# msg: common_functions of install_uninstall_direct and upgrade_direct and upgrade_indirect,include cfg_repo_source and get_related_lists and uninstall_pkg.
#

source /etc/openEuler-latest
LANG=en_US.UTF-8
service_ip=121.36.84.172

#Configure original repo source
function configure_original_repo() {
    original_ver=$1
    echo "[${original_ver}_OS]
name=${original_ver}_OS
baseurl=https://repo.openeuler.org/${original_ver}/OS/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_everything]
name=${original_ver}_everything
baseurl=https://repo.openeuler.org/${original_ver}/everything/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/everything/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_source]
name=${original_ver}_source
baseurl=https://repo.openeuler.org/${original_ver}/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_update]
name=${original_ver}_update
baseurl=https://repo.openeuler.org/${original_ver}/update/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
" >/etc/yum.repos.d/"${original_ver}".repo 

    if [[ ${original_ver}x == "openEuler-20.03-LTS"x ]] || [[ ${original_ver}x == "openEuler-20.03-LTS-SP1"x ]]; then
        echo "[${original_ver}_EPOL]
name=${original_ver}_EPOL
baseurl=https://repo.openeuler.org/${original_ver}/EPOL/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_EPOL_source]
name=${original_ver}_EPOL_source
baseurl=https://repo.openeuler.org/${original_ver}/EPOL/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_EPOL_update]
name=${original_ver}_EPOL_update
baseurl=https://repo.openeuler.org/${original_ver}/EPOL/update/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_EPOL_update_source]
name=${original_ver}_EPOL_update_source
baseurl=https://repo.openeuler.org/${original_ver}/EPOL/update/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler" >>/etc/yum.repos.d/"${original_ver}".repo
    else
        echo "[${original_ver}_EPOL]
name=${original_ver}_EPOL
baseurl=https://repo.openeuler.org/${original_ver}/EPOL/main/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_EPOL_source]
name=${original_ver}_EPOL_source
baseurl=https://repo.openeuler.org/${original_ver}/EPOL/main/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_EPOL_update]
name=${original_ver}_EPOL_update
baseurl=https://repo.openeuler.org/${original_ver}/EPOL/update/main/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${original_ver}_EPOL_update_source]
name=${original_ver}_EPOL_update_source
baseurl=https://repo.openeuler.org/${original_ver}/EPOL/update/main/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${original_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler" >>/etc/yum.repos.d/"${original_ver}".repo
    fi
}

#Configure target repo source
function configure_target_repo() {
    target_ver=${1-${openeulerversion}}
    echo "[${target_ver}_OS]
name=${target_ver}_OS
baseurl=https://repo.openeuler.org/${target_ver}/OS/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_everything]
name=${target_ver}_everything
baseurl=https://repo.openeuler.org/${target_ver}/everything/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/everything/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_source]
name=${target_ver}_source
baseurl=https://repo.openeuler.org/${target_ver}/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_update]
name=${target_ver}_update
baseurl=https://repo.openeuler.org/${target_ver}/update/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_update_source]
name=${target_ver}_update_source
baseurl=https://repo.openeuler.org/${target_ver}/update/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
" >/etc/yum.repos.d/"${target_ver}".repo

    if [ "${target_ver}"x == "openEuler-20.03-LTS-SP1"x ]; then
        echo "[${target_ver}_EPOL]
name=${target_ver}_EPOL
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_EPOL_source]
name=${target_ver}_EPOL_source
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_EPOL_update]
name=${target_ver}_EPOL_update
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/update/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_EPOL_update_source]
name=${target_ver}_EPOL_update_source
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/update/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler" >>/etc/yum.repos.d/"${target_ver}".repo
    else
        echo "[${target_ver}_EPOL]
name=${target_ver}_EPOL
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/main/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_EPOL_source]
name=${target_ver}_EPOL_source
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/main/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_EPOL_update]
name=${target_ver}_EPOL_update
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/update/main/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler

[${target_ver}_EPOL_update_source]
name=${target_ver}_EPOL_update_source
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/update/main/source/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler" >>/etc/yum.repos.d/"${target_ver}".repo
    fi

    printf "
[${target_ver}_%s]
name=${target_ver}_%s
baseurl=http://${service_ip}/repo.openeuler.org/${target_ver}/%s/$(arch)/
enabled=1
gpgcheck=1
gpgkey=http://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
priority=1
" "$test_update_repo" "$test_update_repo" "$test_update_repo" >>/etc/yum.repos.d/"${target_ver}".repo

    printf "
[${target_ver}_source_%s]
name=${target_ver}_source_%s
baseurl=http://${service_ip}/repo.openeuler.org/${target_ver}/%s/source/
enabled=1
gpgcheck=1
gpgkey=http://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
priority=1
" "$test_update_repo" "$test_update_repo" "$test_update_repo" >>/etc/yum.repos.d/"${target_ver}".repo

    if [ "${target_ver}"x == "openEuler-20.03-LTS-SP1"x ]; then
        if [ "${test_update_repo}"x == "${test_EPOL_update_repo}"x ]; then
            printf "
[${target_ver}_EPOL_%s]
name=${target_ver}_EPOL_%s
baseurl=http://${service_ip}/repo.openeuler.org/${target_ver}/EPOL/%s/$(arch)/
enabled=1
gpgcheck=1
gpgkey=http://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
priority=1
" "$test_EPOL_update_repo" "$test_EPOL_update_repo" "$test_EPOL_update_repo" >>/etc/yum.repos.d/"${target_ver}".repo

            printf "
[${target_ver}_EPOL_source_%s]
name=${target_ver}_EPOL_source_%s
baseurl=http://${service_ip}/repo.openeuler.org/${target_ver}/EPOL/%s/source/
enabled=1
gpgcheck=1
gpgkey=http://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
priority=1
" "$test_EPOL_update_repo" "$test_EPOL_update_repo" "$test_EPOL_update_repo" >>/etc/yum.repos.d/"${target_ver}".repo
        else
            printf "No ${target_ver}_EPOL_%s repo" "$test_update_repo"
        fi
    else
        if [ "${test_update_repo}"x == "${test_EPOL_update_repo}"x ]; then
            printf "
[${target_ver}_EPOL_%s]
name=${target_ver}_EPOL_%s
baseurl=http://${service_ip}/repo.openeuler.org/${target_ver}/EPOL/%s/main/$(arch)/
enabled=1
gpgcheck=1
gpgkey=http://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
priority=1
" "$test_EPOL_update_repo" "$test_EPOL_update_repo" "$test_EPOL_update_repo" >>/etc/yum.repos.d/"${target_ver}".repo

            printf "
[${target_ver}_EPOL_source_%s]
name=${target_ver}_EPOL_source_%s
baseurl=http://${service_ip}/repo.openeuler.org/${target_ver}/EPOL/%s/main/source/
enabled=1
gpgcheck=1
gpgkey=http://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
priority=1
" "$test_EPOL_update_repo" "$test_EPOL_update_repo" "$test_EPOL_update_repo" >>/etc/yum.repos.d/"${target_ver}".repo
        else
            printf "No ${target_ver}_EPOL_%s repo" "$test_update_repo"
        fi
    fi
}

#Get the package lists
function get_related_lists() {
    target_ver=${1-${openeulerversion}}
    test -d /home/pkg_manager_folder || mkdir /home/pkg_manager_folder && cd /home/pkg_manager_folder || exit 1
    dnf list --installed | grep "@anaconda" | grep "arch\|x86_64" | awk '{print $1}' | awk -F. 'OFS="."{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}' >anaconda_list
    dnf list --available --repo="${target_ver}_${test_update_repo}" | grep "arch\|x86_64" | awk '{print $1}' | awk -F. 'OFS="."{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}' >update_dnf_list

    # 获取update二进制包列表
    dnf install -y rpm-build
    exec_path=$(pwd)
    dnf list --repo="${target_ver}_source_${test_update_repo}" --available|awk '{print $1}' |awk -F '.src' '{print $1}'|grep -v "Last\|Available\|${target_ver}" > source_list
    dnf config-manager --disable "${target_ver}_source_${test_update_repo}"
    test -d /home/src || mkdir /home/src && cd /home/src
    yumdownloader --source $(cat ${exec_path}/source_list)
    while read name
    do
        rpm -i ${name}*.src.rpm || echo "Source package ${name} install fail !" >>${exec_path}/check.log
        rpm2cpio ${name}*.src.rpm |cpio -idmv --no-absolute-filenames "*.spec" || echo "${name} spec get fail !" >>${exec_path}/check.log
    done < ${exec_path}/source_list
    cd ${exec_path}
    ls -l /home/src/*spec|awk '{print $9}' > spec.list
    while read spec
    do
            rpm -q --specfile ${spec} --queryformat="%{NAME}\n" >> update_rpm_list || echo " ${spec} get the package name fail !" >>check.log
    done < spec.list
    cat update_dnf_list update_rpm_list |sort|uniq > update_list

    # 获取EPOL二进制包列表
    if [ "${test_update_repo}"x == "${test_EPOL_update_repo}"x ]; then
        dnf list --available --repo="${target_ver}_EPOL_${test_EPOL_update_repo}" | grep "arch\|x86_64" | awk '{print $1}' | awk -F. 'OFS="."{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}' >EPOL_update_dnf_list
        dnf list --repo="${target_ver}_EPOL_source_${test_EPOL_update_repo}" --available|awk '{print $1}' |awk -F '.src' '{print $1}'|grep -v "Last\|Available\|${target_ver}" > epol_source_list
        dnf config-manager --disable "${target_ver}_EPOL_source_${test_update_repo}"
        test -d /home/src_epol || mkdir /home/src_epol && cd /home/src_epol
        yumdownloader --source $(cat ${exec_path}/epol_source_list)
        while read epol_name
        do
            rpm -i ${epol_name}*.src.rpm || echo "Source package ${epol_name} install fail !" >>${exec_path}/check.log
            rpm2cpio ${epol_name}*.src.rpm |cpio -idmv --no-absolute-filenames "*.spec" 
        done < ${exec_path}/epol_source_list
        cd ${exec_path}
        ls -l /home/src_epol/*spec|awk '{print $9}' > epol_spec.list
        while read epol_spec
        do
                rpm -q --specfile ${epol_spec} --queryformat="%{NAME}\n" >> EPOL_update_rpm_list || echo " ${epol_spec} get the package name fail !" >>check.log
        done < epol_spec.list
        cat EPOL_update_dnf_list EPOL_update_rpm_list |sort|uniq > EPOL_update_list
    else
        printf "No ${target_ver}_EPOL_%s pkg-lists" "$test_update_repo"
    fi
}


#uninstall packages
function uninstall_pkg() {
    #yum remove -y $(cat update_list) --skip-broken --nobest |tee remove_log
    #if [ -s remove_log ]; then
    #    echo "update_list uninstall complete"
    #else
    cat >get_removeList.sh <<EOF1
while read -r pkg; do
    cat anaconda_list | grep "^\${pkg}$" || echo "\${pkg}" >> removeList
done < update_list
EOF1

    cat >delete_removeList.sh <<EOF2
while read -r pkg; do
    dnf remove -y --skip-broken --nobest \${pkg}
done < removeList
EOF2
    chmod +x get_removeList.sh delete_removeList.sh
    ./get_removeList.sh
    bash -x delete_removeList.sh | tee remove_log
    #fi
    test -s EPOL_update_list && while read -r pkg; do
        yum remove -y "$pkg" --skip-broken --nobest >>EPOL_remove_log 2>&1
    done <EPOL_update_list
}
