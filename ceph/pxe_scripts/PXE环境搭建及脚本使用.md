1、PXE环境搭建
===========

1.1、PXE简介
------------

预启动执行环境(Pre-boot Execution Environment，PXE)是由Intel设计的协议，它可以使计算机通过网络启动。工作在Client/Server模式，允许客户机通过网络从远程服务器下载引导镜像，并加载安装文件或者整个操作系统。

### 1.1.1、PXE安装的优点

规模化：同时装配多台服务器

自动化：安装系统、配置各种服务

远程实现：不需要光盘、U盘等安装介质

### 1.1.2、PXE原理介绍

1、客户端设置PXE启动，重启客户端

2、客户端以PXE方式启动，向当前网络内请求IP地址，DHCP服务收到请求回复（ip
地址， next-server, filename）

2、客户端根据消息，去next-server下获取filename下的启动文件

3、加载启动文件

4、执行指定的ks文件完成系统安装

1.2、软件安装
-------------

```shell
yum install dhcp -y
yum install tftp xinetd tftp-server -y
yum install nfs-utils rpcbind -y
```



1.3、服务配置
-------------

### 1.3.1、dhcpd.conf

```shell
vi /etc/dhcp/dhcpd.conf
```

示例内容

```
next-server 192.168.144.9;

subnet 192.168.144.0 netmask 255.255.255.0 {
not authoritative;
}

group {
host 192.168.144.7 {
option host-name localhost;
option routers 192.168.144.9;
hardware ethernet 44:a1:91:9f:9a:9a;
fixed-address 192.168.144.7;
next-server 192.168.144.9;
filename "auto_uefi/9.3.14.7_uefi/grubaa64.efi";
}
}
```

解释： next-server 指向tftp服务的地址

​			 filename指的是tftp的路径下的引导文件

### 1.3.2、tftp

```shell
vi /etc/xinetd.d/tftp
```

示例内容

```
service tftp
{	
        socket_type             = dgram
        protocol                = udp
        wait                    = yes
        user                    = root
        server                  = /usr/sbin/in.tftpd
        server_args             = -s /var/lib/tftpboot -u nobody -v
        disable                 = no
        per_source              = 11
        cps                     = 100 2
        flags                   = IPv4
}
```



解释：/var/lib/tftpboot目录是用来存放启动文件的目录

### 1.3.3、exports

```shell
vi /etc/exports
```

示例内容

```
/home/PXE/os_install/ *(root_squash,crossmnt)
/home/PXE/pxe_install_share *(ro)
```

解释：/home/PXE/os\_install/目录内存放镜像源、ks文件等，可以自行调整

 		   /home/PXE/pxe\_install\_share目录是用来存放一些公共脚本

### 1.4、启动服务

**1) 关闭防火墙**

```shell
systemctl stop firewalld.service
systemctl disable firewalld.service
```

**2) 启动dhcp、tftp、nfs服务并设置开机启动**

```shell
systemctl enable dhcpd
systemctl start dhcpd
systemctl enable tftp
systemctl start tftp
systemctl enable nfs
systemctl start nfs
```



1.5、os适配
-----------

### 1.5.1、centos7.6 适配记录

1、下载iso镜像至 /home/PXE/iso目录

2、增加开机挂载

```shell
mkdir -p /home/PXE/os_install/CentOS_7.6_aarch64
echo "/home/PXE/iso/CentOS-7-aarch64-Everything-1810.iso      /home/PXE/os_install/CentOS_7.6_aarch64 iso9660 defaults,ro,loop 0 0" >> /etc/fstab

mount -a
```

3、拷贝启动文件

```shell
mkdir -p /var/lib/tftpboot/CentOS_7.6_aarch64_uefi
cd /var/lib/tftpboot/CentOS_7.6_aarch64_uefi
cp /home/PXE/os_install/CentOS_7.6_aarch64/EFI/BOOT/grubaa64.efi .
cp /home/PXE/os_install/CentOS_7.6_aarch64/images/pxeboot/* .
cat > grub.cfg <<EOF
set timeout=10
menuentry 'install CentOS_7.6_aarch64' {
  linux CentOS_7.6_aarch64_uefi/vmlinuz ip=dhcp inst.ks=nfs:192.168.144.9:/home/PXE/os_install/ks/auto_ks/bmc_ip-ks.cfg
  initrd CentOS_7.6_aarch64_uefi/initrd.img
}
EOF
```

4、手动装centos7.6系统获取/root/anaconda-ks.cfg文件，放置在/home/PXE/os\_install/ks目录下并命名为CentOS\_7.6\_aarch64-ks.templete

5、修改CentOS\_7.6\_aarch64-ks.templete

内容如下

```shell
#version=DEVEL
ignoredisk --only-use=disk/by-id/scsi-disk_uuid
#autopart --type=lvm
# clean system disk
clearpart --all --initlabel --drives=disk/by-id/scsi-disk_uuid
# Use graphical install
graphical
# Use NFS installation media
nfs --server=192.168.144.9 --dir=/home/PXE/os_install/CentOS_7.6_aarch64/

# System authorization information
auth --enableshadow --passalgo=sha512
# Run the Setup Agent on first boot
firstboot --enable
# Keyboard layouts
keyboard --vckeymap=us --xlayouts='us'
# System language
lang en_US.UTF-8


# close firewall
firewall --disabled
# close selinux
selinux --disabled
# set installation logging level
logging --level=info


# Network information
network  --bootproto=dhcp --device=enp125s0f0 --ipv6=auto --activate
network  --bootproto=dhcp --device=enp125s0f1 --ipv6=auto
network  --bootproto=dhcp --device=enp125s0f2 --ipv6=auto
network  --bootproto=dhcp --device=enp125s0f3 --ipv6=auto
network  --bootproto=dhcp --device=enp135s0 --ipv6=auto --activate
network  --bootproto=dhcp --device=enp136s0 --ipv6=auto --activate
network  --bootproto=dhcp --device=enp137s0 --ipv6=auto --activate
network  --bootproto=dhcp --device=enp138s0 --ipv6=auto --activate
network  --hostname=localhost.localdomain


# Root password
rootpw --iscrypted $6$cTT3263g6.q9734R$Eupp2mU9A4qvQuSibd9YaoqIOCUMToJUsMUqe6iQS2pvw8grFyPSecTRCqDVky/PugwZI463Tuyl9D2bqGyUt0

# DO not configure the Xwindow System
skipx

# System services
services --enable="chronyd"
# System timezone
timezone Asia/Shanghai --isUtc --nontp
# System bootloader configuration
#bootloader --append=" crashkernel=auto" --location=mbr --boot-drive=disk/by-id/scsi-disk_uuid
# Disk partitioning information
part /boot --fstype="xfs" --ondisk=disk/by-id/scsi-disk_uuid --size=1024
part pv.715 --fstype="lvmpv" --ondisk=disk/by-id/scsi-disk_uuid --size=1 --grow
part /boot/efi --fstype="efi" --ondisk=disk/by-id/scsi-disk_uuid --size=1024 --fsoptions="umask=0077,shortname=winnt"
volgroup centos --pesize=4096 pv.715
logvol swap  --fstype="swap" --size=4096 --name=swap --vgname=centos
logvol /  --fstype="xfs" --grow --size=1 --name=root --vgname=centos

# reboot
reboot

%packages
@^minimal
@core
kexec-tools

nfs-utils
ipmitool
expect
net-tools
chrony
%end

%addon com_redhat_kdump --enable --reserve-mb='auto'

%end

%anaconda
pwpolicy root --minlen=6 --minquality=1 --notstrict --nochanges --notempty
pwpolicy user --minlen=6 --minquality=1 --notstrict --nochanges --emptyok
pwpolicy luks --minlen=6 --minquality=1 --notstrict --nochanges --notempty
%end


%pre --interpreter=/usr/bin/bash --log=/root/ks_pre_install.log --erroronfail
echo "**************************************************************************"
%end


#-----------------------
%post --interpreter=/usr/bin/bash --log=/root/ks_post_install.log --erroronfail
# nfs mount 
mkdir -p /pxe_install_share
cat >> /etc/fstab <<EOF

172.168.144.9:/home/PXE/pxe_install_share /pxe_install_share nfs defaults 0 0

EOF
mount -a

# upgrade 1822
cd /pxe_install_share/1822/version-3.9.0.8
sh upgrade_1822.sh centos7.6
cd -

# config chrony
mv /etc/chrony.conf /etc/chrony.conf-bak
echo "server 172.168.144.9 iburst" >> /etc/chrony.conf
echo "makestep 1.0 3" >> /etc/chrony.conf

systemctl start chronyd.service
systemctl enable chronyd.service
timedatectl set-timezone Asia/Shanghai
chronyc -a makestep
timedatectl set-ntp true

systemctl restart chronyd.service
hwclock -w

# config network
ip a|grep enp125s0f0|grep 'state UP'
if [[ $? -eq 0 ]]
then
cd /etc/sysconfig/network-scripts
cp ifcfg-enp125s0f0 bak-ifcfg-enp125s0f0
sed -i 's#dhcp#static#' ifcfg-enp125s0f0
sed -i 's#ONBOOT=.*#ONBOOT=yes#' ifcfg-enp125s0f0
cat >> ifcfg-enp125s0f0 <<EOF
IPADDR=manage_ip
PREFIX=manage_prefix
GATEWAY=manage_gateway
EOF
fi
%end

```

### 1.5.2、CentOS8.2 适配记录

1、下载iso镜像至 /home/PXE/iso目录

2、增加开机挂载

```shell
mkdir -p /home/PXE/os_install/CentOS_8.2_aarch64
echo "/home/PXE/iso/CentOS-8.2.2004-aarch64-dvd1.iso      /home/PXE/os_install/CentOS_8.2_aarch64 iso9660 defaults,ro,loop 0 0" >> /etc/fstab
mount -a
```

3、拷贝启动文件

```shell
mkdir -p /var/lib/tftpboot/CentOS_8.2_aarch64_uefi
cd /var/lib/tftpboot/CentOS_8.2_aarch64_uefi
cp /home/PXE/os_install/CentOS_8.2_aarch64/EFI/BOOT/grubaa64.efi .
cp /home/PXE/os_install/CentOS_8.2_aarch64/images/pxeboot/* .
cat > grub.cfg <<EOF
set timeout=10
menuentry 'install CentOS_8.2_aarch64' {
  linux CentOS_8.2_aarch64_uefi/vmlinuz ip=dhcp inst.ks=nfs:192.168.144.9:/home/PXE/os_install/ks/auto_ks/bmc_ip-ks.cfg
  initrd CentOS_8.2_aarch64_uefi/initrd.img
}	
EOF
```

4、手动装centos8.2系统获取/root/anaconda-ks.cfg文件，放置在/home/PXE/os\_install/ks目录下并命名为CentOS\_8.2\_aarch64-ks.templete

5、修改CentOS\_8.2\_aarch64-ks.templete

内容如下

```shell
#version=RHEL8

ignoredisk --only-use=disk/by-id/scsi-disk_uuid
#autopart --type=lvm
# clean system disk
clearpart --all --initlabel --drives=disk/by-id/scsi-disk_uuid
# Use graphical install
graphical
# Use NFS installation media
nfs --server=192.168.144.9 --dir=/home/PXE/os_install/CentOS_8.2_aarch64/


# Keyboard layouts
keyboard --vckeymap=us --xlayouts='us'
# System language
lang en_US.UTF-8

# close firewall
firewall --disabled
# close selinux
selinux --disabled
# set installation logging level
logging --level=info


# Network information
network  --bootproto=dhcp --device=enp125s0f0 --ipv6=auto --activate
network  --bootproto=dhcp --device=enp125s0f1 --ipv6=auto
network  --bootproto=dhcp --device=enp125s0f2 --ipv6=auto
network  --bootproto=dhcp --device=enp125s0f3 --ipv6=auto
network  --bootproto=dhcp --device=enp135s0 --ipv6=auto --activate
network  --bootproto=dhcp --device=enp136s0 --ipv6=auto --activate
network  --bootproto=dhcp --device=enp137s0 --ipv6=auto --activate
network  --bootproto=dhcp --device=enp138s0 --ipv6=auto --activate

network  --hostname=localhost.localdomain


# Root password
rootpw --iscrypted $6$3vi6ilzJ.2pqxsiJ$iFpHgUVDnMGQy/1U1JT71.sZR9ncm/YDAO3sMEZAVL8CEvVeGpK9ge6nVYbOSmlQQLKLmcddjb/icTIv.91LD.
# Run the Setup Agent on first boot
firstboot --enable
# Do not configure the X Window System
skipx
# System services
services --disabled="chronyd"
# System timezone
timezone Asia/Shanghai --isUtc --nontp
# Disk partitioning information
part /boot --fstype="xfs" --ondisk=disk/by-id/scsi-disk_uuid --size=1024
part pv.715 --fstype="lvmpv" --ondisk=disk/by-id/scsi-disk_uuid --size=1 --grow
part /boot/efi --fstype="efi" --ondisk=disk/by-id/scsi-disk_uuid --size=1024 --fsoptions="umask=0077,shortname=winnt"
volgroup centos --pesize=4096 pv.715
logvol swap  --fstype="swap" --size=4096 --name=swap --vgname=centos
logvol /  --fstype="xfs" --grow --size=1 --name=root --vgname=centos


# reboot
reboot

%packages
@^minimal-environment
kexec-tools

nfs-utils
ipmitool
expect
net-tools
chrony
%end

%addon com_redhat_kdump --enable --reserve-mb='auto'

%end

%anaconda
pwpolicy root --minlen=6 --minquality=1 --notstrict --nochanges --notempty
pwpolicy user --minlen=6 --minquality=1 --notstrict --nochanges --emptyok
pwpolicy luks --minlen=6 --minquality=1 --notstrict --nochanges --notempty
%end



%pre --interpreter=/usr/bin/bash --log=/root/ks_pre_install.log --erroronfail
echo "**************************************************************************"
%end


#-----------------------
%post --interpreter=/usr/bin/bash --log=/root/ks_post_install.log --erroronfail
# nfs mount
mkdir -p /pxe_install_share

cat >> /etc/fstab <<EOF

172.168.144.9:/home/PXE/pxe_install_share /pxe_install_share nfs defaults 0 0

EOF

mount -a
# upgrade 1822
cd /pxe_install_share/1822/version-3.9.0.8
sh upgrade_1822.sh centos8.2
cd -


# config chrony
mv /etc/chrony.conf /etc/chrony.conf-bak
echo "server 172.168.144.9 iburst" >> /etc/chrony.conf
echo "makestep 1.0 3" >> /etc/chrony.conf

systemctl start chronyd.service
systemctl enable chronyd.service
timedatectl set-timezone Asia/Shanghai
chronyc -a makestep
timedatectl set-ntp true

systemctl restart chronyd.service
hwclock -w

# config network
ip a|grep enp125s0f0|grep 'state UP'
if [[ $? -eq 0 ]]
then
cd /etc/sysconfig/network-scripts
cp ifcfg-enp125s0f0 bak-ifcfg-enp125s0f0
sed -i 's#dhcp#static#' ifcfg-enp125s0f0
sed -i 's#ONBOOT=.*#ONBOOT=yes#' ifcfg-enp125s0f0
cat >> ifcfg-enp125s0f0 <<EOF
IPADDR=manage_ip
PREFIX=manage_prefix
GATEWAY=manage_gateway
EOF
fi
%end
```

1.6、ks文件介绍
---------------

### 1.6.1、%pre预安装部分

```shell
%pre
command1
command2
...
%end
```

该部分是在解析完ks文件后，开始安装前，该系统需要运行的命令，不常用

### 1.6.2、%post 安装后部分

```shell
%post
command1
command2
...
%end

```

该部分是在安装系统完成后，第一次重启前，该系统需要运行的命令（比较常用）

可以进行网络配置、网卡驱动升级以及一些需要在安装完系统后需要执行一次的操作

### 1.6.3、%packages 需要预安装软件

```shell
%packages
@^minimal-environment
kexec-tools

nfs-utils
ipmitool
expect
net-tools
chrony
%end
```

**想了解更多参数请查阅以下链接**

https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/installation_guide/chap-kickstart-installations

# 2、PXE脚本介绍及使用

**使用前提：**

​	**1、pxe服务的网络需要与物理机pxe网口所在网络一致**

​	**2、需要将物理机的pxe网口的mac地址查到，并添加到dhcp服务配置里**

​	**3、需要查到系统磁盘的uuid**

2.1、脚本目录介绍
-----------------

|---pxe\_scripts \# 脚本根目录

​	|---conf \# pxe\_install.sh需要的环境参数

​	|---pxe\_install.sh \# 执行pxe安装的核心脚本

​	|---server\_info.yaml \# 所有需要进行pxe安装的环境参数

​	|---all\_os\_install.py \# 解析server\_info.yaml，并调起pxe\_install.sh

​	|---check\_wait\_os\_ok.py \# 检查等待os安装的脚本

​	|---support\_os.list \# 记录已支持的os

### 2.1.1、pxe\_install.sh 脚本逻辑介绍

1、加载conf参数

2、拷贝uefi摸版，生成当前环境的uefi文件

3、修改grub.cfg下的inst.ks指向，为当前环境所需的ks文件

4、拷贝ks摸版，生成当前环境所需的ks文件

5、检查并修改dncp配置，将filename的值修改为当前环境所需uefi路径，并重启dhcp服务

6、使用ipmitool命令设置当前环境的启动项为硬盘启动(永久有效)

7、使用ipmitool命令设置当前环境的启动项为pxe(单次有效)

8、使用ipmitool命令将当前物理环境重启，即可开始pxe安装

### 2.1.2、all\_os\_install.py脚本逻辑介绍

1、解析server\_info.yaml

2、遍历所有环境信息依次执行以下操作

​	1)、遍历所有参数，并将内容同步至conf文件

​	2)、调起pxe\_install.sh脚本执行当前节点

3、执行check\_wait\_os\_ok.py脚本等待环境安装完成

2.2、参数配置
-------------

### 2.2.1、conf文件配置说明

1）该文件控制pxe\_install.sh执行时所加载的参数

2）需要安装单台服务器可以直接修改该文件，后执行sh pxe\_install.sh脚本

| 参数名         | 示例               | 解释                                                     |
| -------------- | ------------------ | -------------------------------------------------------- |
| bmc_ip         | 9.3.14.10          | bmc ip                                                   |
| bmc_user       | root               | bmc登录的用户名                                          |
| bmc_pwd        | \*\*\****          | bmc登录的密码                                            |
| manage_ip      | 172.168.144.10     | 管理口的ip                                               |
| manage_perfix  | 16                 | 管理口的掩码前缀                                         |
| manage_gateway | 172.168.131.1      | 管理口的网关                                             |
| dhcp_ip        | 192.168.144.12     | 该ip是pxe安装通信网口的ip，与dhcp配置里的mac地址是对应的 |
| system_name    | openEuler22.03_LTS | 安装的系统名称                                           |
| arch_name      | aarch64            | 系统架构                                                 |
| efi_name       | grubaa64.efi       | efi文件名                                                |
| disk_uuid      | 350000399c8106f55  | 该环境系统盘uuid                                         |

**注意：通常只需要修改system_name即可，已支持的名称可以查看当前目录下的support\_os.list文件，后续pxe有支持需要及时更新该文件**

### 2.2.1、server\_info.yaml文件配置说明

1）该文件的作用是供all\_os\_install.py解析然后执行pxe安装，可以同时安装多台物理机（本质上还是串行执行sh pxe\_install.sh）

2）参数含义同conf文件，不再赘述，只是多了一层bmc\_ip做整个配置的key值

2.3、执行pxe安装脚本
--------------------

### 2.3.1、执行单台物理机安装

1、检查好conf配置无误

2、执行sh pxe\_install.sh

### 2.3.2、 执行多台物理机安装

1、检查好server\_info.yaml配置无误

2、执行python3 pxe\_install.sh即可
