#!/usr/bin/env bash
set -euo pipefail
SERVICE_IP=121.36.84.172
LTP_PREFIX=/opt/ltp
source /etc/openEuler-latest

red()    { echo -e "\e[31m$*\e[0m"; }
green()  { echo -e "\e[32m$*\e[0m"; }
yellow() { echo -e "\e[33m$*\e[0m"; }

get_oe_ver() { grep -oE '[0-9]{2}\.[0-9]{2}' /etc/openEuler-latest | head -1; }

select_ltp_tag() {
    local k=$(uname -r | awk -F. '{printf "%d%02d",$1,$2}')
    case $k in
        4*|509|510) echo 20220121 ;;
        511|6[0-4]) echo 20230626 ;;
        6[5-8])    echo 20231030 ;;
        *)         git ls-remote --tags --sort=-v:refname https://github.com/linux-test-project/ltp.git \
                   | awk -F/ '{print $3}' | grep -E '^[0-9]{8}$' | head -1 ;;
    esac
}

gen_repos() {

    target_ver=${1-${openeulerversion}}
    rm -rf /etc/yum.repos.d/*
    test_update_repo=$(curl http://"${SERVICE_IP}"/repo.openeuler.org/"${openeulerversion}"/"${openeulerversion}"-update.json | grep dir | grep "[0-9]" | grep -v test | grep -v round | awk -F \" '{print $4}' | awk -F "/" '{print $1}' | sort | uniq | tail -n 1)
    test_EPOL_update_repo=$(curl http://"${SERVICE_IP}"/repo.openeuler.org/"${openeulerversion}"/EPOL/"${openeulerversion}"-update.json | grep dir | grep "[0-9]" | grep -v test | awk -F \" '{print $4}' | awk -F "/" '{print $1}' | sort | uniq | tail -n 1 | awk -F "|" '{print $1}')
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

[${target_ver}_EPOL_update]
name=${target_ver}_EPOL_update
baseurl=https://repo.openeuler.org/${target_ver}/EPOL/update/main/$(arch)/
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler" >>/etc/yum.repos.d/"${target_ver}".repo

    printf "
[${target_ver}_%s]
name=${target_ver}_%s
baseurl=http://${SERVICE_IP}/repo.openeuler.org/${target_ver}/%s/$(arch)/
enabled=1
gpgcheck=1
gpgkey=http://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
priority=1
" "$test_update_repo" "$test_update_repo" "$test_update_repo" >>/etc/yum.repos.d/"${target_ver}".repo


    if [ "${test_update_repo}"x == "${test_EPOL_update_repo}"x ]; then
        printf "
[${target_ver}_EPOL_%s]
name=${target_ver}_EPOL_%s
baseurl=http://${SERVICE_IP}/repo.openeuler.org/${target_ver}/EPOL/%s/main/$(arch)/
enabled=1
gpgcheck=1
gpgkey=http://repo.openeuler.org/${target_ver}/OS/$(arch)/RPM-GPG-KEY-openEuler
priority=1
" "$test_EPOL_update_repo" "$test_EPOL_update_repo" "$test_EPOL_update_repo" >>/etc/yum.repos.d/"${target_ver}".repo         
    fi
}

install_deps() {
    green ">>> 安装编译依赖"
    dnf -y install zlib-devel bc gcc-c++ m4 flex bison \
        keyutils-libs-devel lksctp-tools-devel xfsprogs-devel libacl-devel \
        openssl-devel numactl-devel libaio-devel libcap-devel libtirpc-devel \
        hwloc-devel kernel-headers elfutils-libelf-devel patch make automake \
        cmake time psmisc git tar vim
    green ">>> 完成安装编译依赖"

}

update_kernel() {
    green ">>> 开始升级kernel"
    dnf -y upgrade kernel
    green ">>> 完成内核升级"
}


clone_ltp() {
    local tag=$(select_ltp_tag) LTP_PREFIX=$LTP_PREFIX
    green ">>> 准备克隆LTP tag=$tag"
    rm -rf "$LTP_PREFIX"
    local t0=$SECONDS
    while [[ ! -d $LTP_PREFIX ]]; do
        (( SECONDS - t0 > 600 )) && { echo "Clone ltp失败，超时10 min"; exit 1; }
        timeout 120 git clone -b "$tag" --depth 1 https://github.com/linux-test-project/ltp.git "$LTP_PREFIX" && break
        sleep 10
    done
    green ">>> LTP已克隆：$LTP_PREFIX"
}

build_ltp() {
    green ">>> 开始编译LTP"
    [[ -f $LTP_PREFIX/.build-done ]] && { green "已编译，跳过"; return; }
    cd "$LTP_PREFIX"
    make autotools
    ./configure
    make -j"$(nproc)"
    make install
    # kernel 5.10 resolve proc01 testcase fail    
    grep openeulerversion /etc/openEuler-latest |grep -iE "22.03|22.09|23.09" && echo 1024 > /proc/dirty/buffer_size
    # load etmem_swap.ko(swap_pages) and etmem_scan.ko(idle_pages)
    if  ! lsmod |grep etmem ;then
        insmod /usr/lib/modules/$(uname -r)/kernel/fs/proc/etmem_swap.ko*
        insmod /usr/lib/modules/$(uname -r)/kernel/fs/proc/etmem_scan.ko*
    fi
    green ">>> 编译完成，安装目录：$LTP_PREFIX"
}

run_ltp() {
    green ">>> 运行LTP用例：$*"
    cd "$LTP_PREFIX"
    ./runltp "$@" | tee ltp.log
    green ">>> 结果目录：$(ls -d results/*)"
    grep -nr FAIL results/ || true
}


usage() {
    cat <<EOF
用法: $0 <action> [runltp参数...]
Actions:
  release       直接运行ltp测试用例，适用于release测试
  update_pre    配置测试源、升级内核、安装依赖、重启
  update_run    重启后，执行ltp测试
EOF
}

case $1 in
    release)
        install_deps
        clone_ltp
        build_ltp
        shift
        run_ltp $*
        ;;
    update_pre)
        gen_repos
        install_deps
        update_kernel
        reboot
        ;;

    update_run)
        clone_ltp
        build_ltp
        shift
        run_ltp $*
        ;;
    *)
        echo -e "\e[32mhelp info:\e[0m"
        usage;;
esac
