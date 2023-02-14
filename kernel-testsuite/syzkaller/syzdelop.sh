#!/bin/bash
local_ip=$(ip a | grep inet | grep -v inet6 | grep -v 127.0.0.1 | awk '{print $2}' | awk -F "/" '{print $1}')
port=1234
arch=$(uname -m)
ver=$(grep openeulerversion= /etc/openEuler-latest | awk -F "=" '{print $2}')
kernel_path=/usr/src/linux-$(rpm -q kernel-source | sed 's/kernel-source-//')
work_dir=/home/workdir/${port}
vm_path=/home/iso/
vm_name=hda
conf_path=/home/fuzz.cfg
syzkaller_path=/home/syzkaller
iso_path=/home/${ver}-${arch}-dvd.iso
#iso_path=/home/openEuler-22.03-LTS-aarch64-dvd.iso

hostnamectl set-hostname localhost
dnf install -y kernel-source expect

deploy_qemu()
{
    cd /home
    yum install -y ninja-build zlib-devel glib2-devel pixman-devel vim tar make g++
    test -s syzdelop/qemu-5.2.0.tar.xz || wget https://download.qemu.org/qemu-5.2.0.tar.xz
    test -d qemu-5.2.0 && rm -rf qemu-5.2.0
    tar -xf syzdelop/qemu-5.2.0.tar.xz
    cd qemu-5.2.0
    mkdir build && cd build
    if [ $arch == 'x86_64' ];then
	../configure
    else
        ../configure --target-list=arm-softmmu,arm-linux-user,aarch64-softmmu,aarch64-linux-user
    fi
    make -j96
    make install
    cd /home
}

deploy_syzkaller()
{
    cd /home/
    yum install -y git go
    until (test -e "syzkaller")
    do
        git clone https://github.com/google/syzkaller.git
    done
    if [ $arch == 'x86_64' ]; then
        go env -w GOPROXY=https://goproxy.cn,direct
    fi
    cd syzkaller || exit
    if [ $arch == 'aarch64' ]; then
        git reset --hard 20497e8e232a
    fi
    make
    cd -
}

build_kernel_with_KASAN() 
{
    yum install -y flex bison openssl-devel rpm-build make bc rsync elfutils-libelf-devel dwarves
    cd ${kernel_path}
    rm -f .config
    #生成.config
    make openeuler_defconfig
    cp .config .config_bak
    #修改.config
    grep CONFIG_KASAN= .config | grep -v \^#
    if [ $? -eq 0 ];then
    	sed -i -E 's/(CONFIG_KASAN=).*/\1y/g' .config
    else
    	sed -i '/CONFIG_KASAN is/a\CONFIG_KASAN=y' .config
    fi

    grep CONFIG_KASAN_INLINE= .config | grep -v \^#
    if [ $? -eq 0 ];then
    	sed -i -E 's/(CONFIG_KASAN_INLINE=).*/\1y/g' .config
    else
    	sed -i '/CONFIG_KASAN=y/a\CONFIG_KASAN_INLINE=y' .config
    fi
    
    grep CONFIG_KCOV= .config | grep -v \^#
    if [ $? -eq 0 ];then
    	sed -i -E 's/(CONFIG_KCOV=).*/\1y/g' .config
    else
    	sed -i '/CONFIG_KCOV is/a\CONFIG_KCOV=y' .config
    fi

    grep CONFIG_KCOV_ENABLE_COMPARISONS= .config | grep -v \^#
    if [ $? -eq 0 ];then
    	sed -i -E 's/(CONFIG_KCOV_ENABLE_COMPARISONS=).*/\1y/g' .config
    else
    	sed -i '/CONFIG_KCOV=y/a\CONFIG_KCOV_ENABLE_COMPARISONS=y' .config
    fi

    grep CONFIG_KCOV_INSTRUMENT_ALL= .config | grep -v \^#
    if [ $? -eq 0 ];then
        sed -i -E 's/(CONFIG_KCOV_INSTRUMENT_ALL=).*/\1y/g' .config
    else
        sed -i '/CONFIG_KCOV_ENABLE_COMPARISONS=y/a\CONFIG_KCOV_INSTRUMENT_ALL=y' .config
    fi

    grep CONFIG_DEBUG_FS= .config | grep -v \^#
    if [ $? -eq 0 ];then
        sed -i -E 's/(CONFIG_DEBUG_FS=).*/\1y/g' .config
    else
        sed -i '/CONFIG_DEBUG_INFO=y/a\CONFIG_DEBUG_FS=y' .config
    fi

    if [ $arch == 'aarch64' ]; then
        grep CONFIG_ARM64_4K_PAGES= .config | grep -v \^#
        if [ $? -eq 0 ];then
            sed -i -E 's/(CONFIG_ARM64_4K_PAGES=).*/\1y/g' .config
        else
    	    grep CONFIG_ARM64_64K_PAGES= .config | grep -v \^# 
    	    if [ $? -eq 0 ];then
                sed -i "s/CONFIG_ARM64_64K_PAGES=/\#CONFIG_ARM64_64K_PAGES=/g" .config
    	    fi
            sed -i '/CONFIG_ARM64_64K_PAGES=/a\CONFIG_ARM64_4K_PAGES=y' .config
        fi
    fi
    diff -Naru .config_bak .config
    make clean
    grep 20.03 /etc/openEuler-latest
    if [ $? == 0 ]; then 
        if [ $arch == 'x86_64' ]; then
	    echo -e "2\nm\n" | make -j96 binrpm-pkg
        else
	    echo -e "1\n2\ny\nm\n2\nm\n" | make -j96 binrpm-pkg
        fi	    
    else
        if [ $arch == 'x86_64' ]; then
            echo -e "2\ny\nm\n\n" | make -j65 binrpm-pkg
        else
            echo -e "1\n2\n\n\ny\nm\n2\nm\n\n" | make -j98 binrpm-pkg
        fi
    fi
}

build_kernel_with_UBSAN() 
{
    yum install -y flex bison openssl-devel rpm-build make bc rsync elfutils-libelf-devel dwarves
    cd ${kernel_path}
    #生成.config
    rm -f .config
    make openeuler_defconfig
    cp .config .config_bak
    #修改.config
    grep CONFIG_UBSAN= .config | grep -v \^#
    if [ $? -eq 0 ];then
        sed -i -E 's/(CONFIG_UBSAN=).*/\1y/g' .config
    else
        sed -i '/CONFIG_UBSAN is/a\CONFIG_UBSAN=y' .config
    fi

    grep CONFIG_UBSAN_INLINE= .config | grep -v \^#
    if [ $? -eq 0 ];then
        sed -i -E 's/(CONFIG_UBSAN_INLINE=).*/\1y/g' .config
    else
        sed -i '/CONFIG_UBSAN=y/a\CONFIG_UBSAN_INLINE=y' .config
    fi

    grep CONFIG_KCOV= .config | grep -v \^#
    if [ $? -eq 0 ];then
        sed -i -E 's/(CONFIG_KCOV=).*/\1y/g' .config
    else
        sed -i '/CONFIG_KCOV is/a\CONFIG_KCOV=y' .config
    fi

    grep CONFIG_KCOV_ENABLE_COMPARISONS= .config | grep -v \^#
    if [ $? -eq 0 ];then
        sed -i -E 's/(CONFIG_KCOV_ENABLE_COMPARISONS=).*/\1y/g' .config
    else
        sed -i '/CONFIG_KCOV=y/a\CONFIG_KCOV_ENABLE_COMPARISONS=y' .config
    fi

    grep CONFIG_KCOV_INSTRUMENT_ALL= .config | grep -v \^#
    if [ $? -eq 0 ];then
        sed -i -E 's/(CONFIG_KCOV_INSTRUMENT_ALL=).*/\1y/g' .config
    else
        sed -i '/CONFIG_KCOV_ENABLE_COMPARISONS=y/a\CONFIG_KCOV_INSTRUMENT_ALL=y' .config
    fi

    grep CONFIG_DEBUG_FS= .config | grep -v \^#
    if [ $? -eq 0 ];then
        sed -i -E 's/(CONFIG_DEBUG_FS=).*/\1y/g' .config
    else
        sed -i '/CONFIG_DEBUG_INFO=y/a\CONFIG_DEBUG_FS=y' .config
    fi

    if [ $arch == 'aarch64' ]; then
        grep CONFIG_ARM64_4K_PAGES= .config | grep -v \^#
        if [ $? -eq 0 ];then
            sed -i -E 's/(CONFIG_ARM64_4K_PAGES=).*/\1y/g' .config
        else
            grep CONFIG_ARM64_64K_PAGES= .config | grep -v \^# 
            if [ $? -eq 0 ];then
                sed -i "s/CONFIG_ARM64_64K_PAGES=/\#CONFIG_ARM64_64K_PAGES=/g" .config
            fi
            sed -i '/CONFIG_ARM64_64K_PAGES=/a\CONFIG_ARM64_4K_PAGES=y' .config
        fi
    fi
    diff -Naru .config_bak .config
    make clean
    grep 20.03 /etc/openEuler-latest
    if [ $? == 0 ]; then
        if [ $arch == 'x86_64' ]; then
            echo -e "y\ny\nm\n" | make -j96 binrpm-pkg
        else
            echo -e "1\n2\nm\nm\ny\ny\nm\n" | make -j96 binrpm-pkg
        fi
    fi
    grep 21.09 /etc/openEuler-latest
    if [ $? == 0 ]; then
        if [ $arch == 'x86_64' ]; then
            echo -e "2\ny\nm\n\n" | make -j65 binrpm-pkg
        else
            echo -e "1\n2\n\n\ny\nm\n2\nm\n\n" | make -j98 binrpm-pkg
        fi
    fi
    grep "22.09\|22.03" /etc/openEuler-latest
    if [ $? == 0 ]; then
        echo -e "y\ny\ny\ny\nm\n\n" | make -j96 binrpm-pkg
    else
        make -j96 binrpm-pkg
    fi
}

qemu_create_vm()
{
    mkdir -p ${vm_path}
    cd ${vm_path}
    qemu-img create ${vm_name} -f qcow2 60G
    yum groupinstall -y "Virtualization Host"
    systemctl stop firewalld
    if [ $arch == 'x86_64' ];then
        qemu-system-x86_64 -machine accel=kvm -cpu host -m 8092 -smp 4 -serial stdio -hda ${vm_path}${vm_name} -cdrom ${iso_path} -device virtio-gpu-pci -device nec-usb-xhci -device usb-tablet -device usb-kbd -vnc :31 -device virtio-net-pci,netdev=net0 -netdev user,id=net0,restrict=on,hostfwd=tcp:127.0.0.1:$port-:22
    else
        qemu-system-aarch64 -machine virt,accel=kvm,gic-version=3 -cpu host -m 8092 -smp 4 -serial stdio -hda ${vm_path}${vm_name} -cdrom ${iso_path} -bios /usr/share/edk2/aarch64/QEMU_EFI.fd -device virtio-gpu-pci -device nec-usb-xhci -device usb-tablet -device usb-kbd -vnc :31 -device virtio-net-pci,netdev=net0 -netdev user,id=net0,restrict=on,hostfwd=tcp:127.0.0.1:$port-:22
    #剩余进行安装操作
    fi
}

qemu_start_vm()
{
    if [ $arch == 'aarch64' ];then
        qemu-system-aarch64 -machine virt,accel=kvm,gic-version=3 -cpu host -m 8092 -smp 4 -serial stdio -hda ${vm_path}${vm_name} -bios /usr/share/edk2/aarch64/QEMU_EFI.fd -device virtio-gpu-pci -device nec-usb-xhci -device usb-tablet -device usb-kbd -vnc :31 -device virtio-net-pci,netdev=net0 -netdev user,id=net0,restrict=on,hostfwd=tcp:127.0.0.1:$port-:22
    else
        qemu-system-x86_64 -machine accel=kvm -cpu host -m 8092 -smp 4 -serial stdio -hda ${vm_path}${vm_name} -device virtio-gpu-pci -device nec-usb-xhci -device usb-tablet -device usb-kbd -vnc :31 -device virtio-net-pci,netdev=net0 -netdev user,id=net0,restrict=on,hostfwd=tcp:127.0.0.1:$port-:22
    fi
}

sshcmd() {
    expect -c"
        set timeout 300
        spawn ssh -p $port localhost \"$1\"
            expect {
                    \"*)?\" {
                    send \"yes\r\"
                    exp_continue
                }
                \"assword:\" {
                    send \"openEuler12#$\r\"
                    exp_continue
                }
            }
    "
}

scpcmd() {
    expect -c"
        set timeout 300
        spawn scp -P $port -r \"$1\" \"$2\"
            expect {
                    \"*)?\" {
                    send \"yes\r\"
                    exp_continue
                }
                \"assword:\" {
                    send \"openEuler12#$\r\"
                    exp_continue
                }
            }
    "
}

no_passwd()
{
    test -f /root/.ssh/id_rsa || {
    	expect -c"
         	   set timeout 30
               spawn ssh-keygen -t rsa
                   expect {
                       \"*):\" {
                         send \"\r\"
                        exp_continue
                    }
                       \"*is:\" {
                            send \"\r\"
                            exp_continue
                      }
                       \"*again:\" {
                            send \"\r\"
                            exp_continue
                      }
              }	
                "
    }   
        expect -c"
        set timeout 30
        spawn ssh-copy-id -p $port localhost
            expect {
                    \"*)?\" {
                    send \"yes\r\"
                    exp_continue
                }
                \"assword:\" {
                    send \"openEuler12#$\r\"
                    exp_continue
                }
            }
         "
}

modify_eth()
{
    sshcmd "
    cd /etc/sysconfig/network-scripts/;ls | xargs -i mv {} ifcfg-eth0;sed -i 's/NAME=.*/NAME=eth0/' ifcfg-eth0;sed -i 's/DEVICE=.*/DEVICE=eth0/' ifcfg-eth0
    sed -i '/SELINUX=/s/=.*/=disabled/g' /etc/selinux/config
    sed -i '/^AllowTcpForwarding/s/no/yes/g' /etc/ssh/sshd_config
    sed -i '/^AllowAgentForwarding/s/no/yes/g' /etc/ssh/sshd_config"
    if [ $arch == 'aarch64' ]; then
        sshcmd "
        sed -i '/GRUB_CMDLINE_LINUX=/s/off/off net.ifnames=0/' /etc/default/grub
        grub2-mkconfig -o /boot/efi/EFI/openEuler/grub.cfg"
    else
        sshcmd "
        sed -i '/GRUB_CMDLINE_LINUX=/s/512M/512M net.ifnames=0 biosdevname=0/' /etc/default/grub
        grub2-mkconfig -o /etc/grub2.cfg"
    fi
#    sshcmd "reboot"
}

install_rpm()
{
    kernel_rpm=$(ls /root/rpmbuild/RPMS/$(uname -i) | grep kernel-[0-9]|tail -n 1)
    scpcmd /root/rpmbuild/RPMS/$(uname -i)/${kernel_rpm} localhost:/home
    sshcmd "rpm -ivh /home/${kernel_rpm} --force"
    sshcmd "grub2-set-default 0"
}

syzkaller_fuzz()
{
    #kasan.cfg
    #reproduce false 表示错误也不会卡住
    if [ ! -f ${conf_path} ]
    then
        mkdir -p ${work_dir}
        cp kasan.cfg ${conf_path}
        sed -i "s/local_ip/${local_ip}/g" ${conf_path}
        sed -i "s/port/${port}/g" ${conf_path}
        sed -i "s:kernel_path:${kernel_path}:g" ${conf_path}
        sed -i "s:syzkaller_path:${syzkaller_path}:g" ${conf_path}
        sed -i "s:work_dir:${work_dir}:g" ${conf_path} 
        sed -i "s:vm_path:${vm_path}${vm_name}:g" ${conf_path}
        if [ $arch == 'aarch64' ];then
            sed -i "s/targ_arch/arm64/g" ${conf_path}
            sed -i "s/machine_arg/-machine virt,accel=kvm,gic-version=3/g" ${conf_path}
            sed -i "s:bios_arg:-bios /usr/share/edk2/aarch64/QEMU_EFI.fd:g" ${conf_path}
        else
            sed -i "s/targ_arch/amd64/g" ${conf_path}
            sed -i "s/machine_arg/-machine accel=kvm/g" ${conf_path}
            sed -i "s/bios_arg//g" ${conf_path}
        fi
        sed -i "s/qarch/${arch}/g" ${conf_path}
    fi
    cd ${syzkaller_path}/bin/
    ./syz-manager -config ${conf_path} & 2>&1
}

function usage()
{
    echo -e " 1. syzdelop.sh deploy, deploy qemu, syzkaller;\n \
2. syzdelop.sh build [kasan/ubsan/all],  build kasan or ubsan kernel-source, all contains both of them\n \
3. syzdelop.sh createvm,  create vm, during installation process requires manual operation;\n \
4. syzdelop.sh config,  config vm, and install new kernel.before doing this, must start vm.finish this operation ,must manully shutdown vm;\n \
5. syzdelop.sh fuzz,  start syzkaller_fuzz;\n \
6. sysdelop.sh startvm,  start vm;\n \
7. syzdelop.sh uninstall,  uninstall kernel-source and remove it\'s path;\n \
8. syzdelop.sh h, show this help.
"
}

    case $1 in
    deploy)
	which qemu-system-${arch}
        if [ $? -ne 0 ]; then
            deploy_qemu
        fi
        test -d ${syzkaller_path}  || deploy_syzkaller
        ;;
    build)
        case $2 in
        ubsan)
            build_kernel_with_UBSAN;;
        kasan)
            build_kernel_with_KASAN;;
        all)
            build_kernel_with_ALL;;
        esac
        ;;
    createvm)
        qemu_create_vm;;
    config)
        no_passwd
        modify_eth
        install_rpm
        ;;
    fuzz)
        if ! ps -ef | grep syz-manager | grep -qi fuzz.cfg; then
            syzkaller_fuzz
        fi
        ;;
    startvm)
        qemu_start_vm;;
    uninstall)
        [ test ! -d ${kernel_path} ] && exit 1
        dnf remove -y kernel-source
        rm -rf ${kernel_path} 
        rm -rf /usr/local/bin/qemu-*
        rm -rf /usr/local/libexec/qemu-bridge-helper
        rm -rf /usr/local/etc/qemu
        rm -rf /usr/local/share/qemu
        rm -rf /home/syzkaller
        ;;
    h)
        usage
        ;;
    *)
        usage
        exit 1
        ;;
    esac
