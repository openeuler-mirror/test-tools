# Copyright (c) 2023. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   hekeming
# @Contact   :   hk16897@126.com
# @Date      :   2023/07/03
# @License   :   Mulan PSL v2
# @Desc      :   Test SSH link
# ############################################
本文参照https://support.huaweicloud.com/dpmg-kunpengsdss/kunpengcephblockeuler_04_0001.html整理后稍作改动

# 1、基本介绍

Ceph 是一个专注于分布式的、弹性可扩展的、高可靠的、性能优异的存储系统平台，可以支持块设备、文件系统和对象网关三种类型的存储接口。

各个模块说明如下

| 模块名称 | 功能描述                                                     |
| -------- | ------------------------------------------------------------ |
| RADOS    | RADOS（Reliable Autonomic Distributed Object Store，RADOS）是Ceph存储集群的基础。Ceph中的一切都以对象的形式存储，而RADOS就负责存储这些对象，而不考虑它们的数据类型。RADOS层确保数据一致性和可靠性。对于数据一致性，它执行数据复制、故障检测和恢复，还包括数据在集群节点间的recovery。 |
| OSD      | 实际存储数据的进程。通常一个OSD daemon绑定一个物理磁盘。Client write/read数据最终都会走到OSD去执行write/read操作。 |
| MON      | Monitor在Ceph集群中扮演者管理者的角色，维护了整个集群的状态，是Ceph集群中最重要的组件。MON保证集群的相关组件在同一时刻能够达成一致，相当于集群的领导层，负责收集、更新和发布集群信息。为了规避单点故障，在实际的Ceph部署环境中会部署多个MON，同样会引来多个MON之前如何协同工作的问题。 |
| MGR      | MGR目前的主要功能是一个监控系统，包含采集、存储、分析（包含报警）和可视化几部分，用于把集群的一些指标暴露给外界使用。 |
| Librados | 简化访问RADOS的一种方法，目前支持PHP、Ruby、Java、Python、C和C++语言。它提供了Ceph存储集群的一个本地接口RADOS，并且是其他服务（如RBD、RGW）的基础，此外，还为CephFS提供POSIX接口。Librados API支持直接访问RADOS，使开发者能够创建自己的接口来访问Ceph集群存储。 |
| RBD      | Ceph块设备，对外提供块存储。可以像磁盘一样被映射、格式化和挂载到服务器上。 |
| RGW      | Ceph对象网关，提供了一个兼容S3和Swift的RESTful API接口。RGW还支持多租户和OpenStack的Keystone身份验证服务。 |
| MDS      | Ceph元数据服务器，跟踪文件层次结构并存储只供CephFS使用的元数据。Ceph块设备和RADOS网关不需要元数据。MDS不直接给Client提供数据服务。 |
| CephFS   | 提供了一个任意大小且兼容POSlX的分布式文件系统。CephFS依赖Ceph MDS来跟踪文件层次结构，即元数据。 |

# 2、环境要求

## 2.1、硬件要求

| 服务器名称 | TaiShan 200服务器（型号2280）                                |
| ---------- | ------------------------------------------------------------ |
| 处理器     | 鲲鹏920 5220处理器                                           |
| 核数       | 2*32核                                                       |
| 主频       | 2600MHz                                                      |
| 内存大小   | 8*16GB                                                       |
| 内存频率   | 2933MHz                                                      |
| 网卡       | IN200网卡4*25GE                                              |
| 硬盘       | 系统盘：RAID1（2*960GB SATA SSD）数据盘：RAID模式下使能JBOD（11\*4TB SATA HDD） |
| NVMe SSD   | 1*ES3000 V5 3.2TB NVMe SSD                                   |
| RAID卡     | Avago SAS 3508                                               |



## 2.2、软件要求

| 软件名称    | 版本            |
| ----------- | --------------- |
| OS          | openEuler 22.03 |
| Ceph        | 14.2.8          |
| ceph-deploy | 2.0.1           |

## 2.3、集群规划

### 2.3.1、组网图

![](https://support.huaweicloud.com/dpmg-kunpengsdss/zh-cn_image_0000001089002225.png)

### 2.3.2、服务端规划

| 主机名 | 管理IP        | Public Network | Cluster Network |
| ------ | ------------- | -------------- | --------------- |
| ceph1  | 192.168.2.166 | 192.168.3.166  | 192.168.4.166   |
| ceph2  | 192.168.2.167 | 192.168.3.167  | 192.168.4.167   |
| ceph3  | 192.168.2.168 | 192.168.3.168  | 192.168.4.168   |

### 2.3.3、客户端规划

| 主机名  | 管理IP        | Public Network |
| ------- | ------------- | -------------- |
| client1 | 192.168.2.160 | 192.168.3.160  |
| client2 | 192.168.2.161 | 192.168.3.161  |
| client3 | 192.168.2.162 | 192.168.3.162  |

- 管理IP：用于远程SSH机器管理配置使用的IP。
- 内部集群IP（cluster network）：用于集群之间同步数据的IP，选取任意一个25GE网口配置即可。
- 外部访问IP（public network）：存储节点供其他节点访问的IP，选取任意一个25GE网口配置即可。
- 客户端当做压力机，需保证客户端业务口IP与集群的外部访问IP在同一个网段，建议选用25GE网口进行配置。

# 3、配置部署环境

### 3.1、配置源

**在所有节点执行以下操作**

1. 通过SFTP工具将“openEuler-***-everything-aarch64-dvd.iso”上传到服务器上“/root”目录下。

2. 挂载everything镜像

   ```shell
   mkdir -p /iso
   mount /root/openEuler-***-everything-aarch64-dvd.iso /iso
   ```

3. 备份并生成新repo

   ```shell
   mkdir -p /etc/yum.repos.d/bak
   mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/bak/
   cat > new.repo <<EOF
   [Base]
   name=Base
   baseurl=file:///iso
   enabled=1
   gpgcheck=0
   priority=1
   
   [arch_fedora_online]
   name=arch_fedora
   baseurl=https://mirrors.huaweicloud.com/fedora/releases/34/Everything/aarch64/os/
   enabled=1
   gpgcheck=0
   priority=2
   
   [Ceph]
   name=Ceph packages for $basearch
   baseurl=http://mirrors.huaweicloud.com/ceph/rpm-nautilus/el7/$basearch
   enabled=1
   gpgcheck=0
   type=rpm-md
   gpgkey=https://download.ceph.com/keys/release.asc
   priority=1
    
   [Ceph-noarch]
   name=Ceph noarch packages
   #baseurl=http://download.ceph.com/rpm-nautilus/el7/noarch
   baseurl=http://mirrors.huaweicloud.com/ceph/rpm-nautilus/el7/noarch
   enabled=1
   gpgcheck=0
   type=rpm-md
   gpgkey=https://download.ceph.com/keys/release.asc
   priority=1
    
   [ceph-source]
   name=Ceph source packages
   #baseurl=http://download.ceph.com/rpm-nautilus/el7/SRPMS
   baseurl=http://mirrors.huaweicloud.com/ceph/rpm-nautilus/el7/SRPMS
   enabled=1
   gpgcheck=0
   type=rpm-md
   gpgkey=https://download.ceph.com/keys/release.asc
   priority=1
   EOF
   ```

### 3.2、关闭防火墙

**所有节点执行以下命令**

   ```shell
systemctl stop firewalld
systemctl disable firewalld
systemctl status firewalld
   ```



### 3.3、配置主机名、ip地址

根据服务端、客户端规划配置好主机名和ip地址

**ceph1主机名配置方法如下，其余节点类似请配置好所有节点**

```shell
hostnamectl --static set-hostname ceph1
```

ceph1节点配置ip地址方法如下

```shell
[root@ceph1 ~]# nmcli c edit enp5s0

===| nmcli interactive connection editor |===

Editing existing '802-3-ethernet' connection: 'enp5s0'

Type 'help' or '?' for available commands.
Type 'print' to show all the connection properties.
Type 'describe [<setting>.<prop>]' for detailed property description.

You may edit the following settings: connection, 802-3-ethernet (ethernet), 802-1x, dcb, sriov, ethtool, match, ipv4, ipv6, tc, proxy
nmcli> set ipv4.addresses 192.168.3.166/24
Do you also want to set 'ipv4.method' to 'manual'? [yes]: yes
nmcli> save
Connection 'enp5s0' (16c486ae-00cd-4d9e-947e-99f40c5f83aa) successfully updated.
nmcli> activate enp5s0
Monitoring connection activation (press any key to continue)
Connection successfully activated (D-Bus active path: /org/freedesktop/NetworkManager/ActiveConnection/7)
```

**总结**

#### **3.3.1、配置 public ip**

```shell
nmcli c edit enp5s0
set ipv4.addresses 192.168.3.166/24
yes
save
activate enp5s0
```

#### **3.3.2、配置 cluster ip**

```shell
nmcli c edit enp6s0
set ipv4.addresses 192.168.4.166/24
yes
save
activate enp6s0
```

### 3.4 配置/etc/hosts

**ceph1节点修改域名解析文件**

```shell
vi /etc/hosts
```

```shell
192.168.3.166   ceph1
192.168.3.167   ceph2
192.168.3.168   ceph3
192.168.3.160   client1
192.168.3.161   client2
192.168.3.162   client3
```

**同步到其余节点**

```shell
scp /etc/hosts ceph2:/etc
scp /etc/hosts ceph3:/etc
scp /etc/hosts client1:/etc
scp /etc/hosts client2:/etc
scp /etc/hosts client3:/etc
```

### 3.5、配置免密登录

**在ceph1节点生成公钥，并发放到各个主机/客户机节点**

```shell
ssh-keygen -t rsa
for i in {1..3}; do ssh-copy-id ceph$i; done
for i in {1..3}; do ssh-copy-id client$i; done
```

**在client1节点生成公钥，并发放到各个主机/客户机节点**

```shell
ssh-keygen -t rsa
for i in {1..3}; do ssh-copy-id ceph$i; done
for i in {1..3}; do ssh-copy-id client$i; done
```

### 3.6、关闭SELinux

**临时关闭，重启后失效**

```shell
setenforce 0
```

**永久关闭，重启后生效**

```shell
sed -i "s#SELINUX=.*#SELINUX=disabled#" /etc/selinux/config
reboot
```

### 3.7、修改umask

修改 umask为0022

```shell
echo "umask 0022" >> /etc/bashrc
source /etc/bashrc
```

### **3.8、配置时间同步**

**安装chrony**

所有节点执行以下命令

```shell
yum -y install chrony
```

**以ceph1为chrony服务端**

```shell
# 备份配置
mv /etc/chrony.conf /etc/chrony.conf-bak

# 生成配置
cat > /etc/chrony.conf <<EOF
allow 192.168.3.0/24
local stratum 5
server 192.168.3.166 iburst
EOF

# 启动chronyd服务
systemctl start chronyd.service
systemctl enable chronyd.service
# 修改时区
timedatectl set-timezone Asia/Shanghai
chronyc -a makestep
# 开启网络时间同步
timedatectl set-ntp true
# 将时间写入bios
hwclock -w
```

所有除ceph1节点为chrony客户端执行以下命令

```shell
# 备份配置
mv /etc/chrony.conf /etc/chrony.conf-bak

# 生成配置
cat > /etc/chrony.conf <<EOF
server 192.168.3.166 iburst
makestep 1.0 3
EOF

# 启动chronyd服务
systemctl start chronyd.service
systemctl enable chronyd.service
# 修改时区
timedatectl set-timezone Asia/Shanghai
chronyc -a makestep
# 开启网络时间同步
timedatectl set-ntp true
# 将时间写入bios
hwclock -w
```

# 4、安装ceph环境

## 4.1、安装ceph软件

**1) 所有节点执行以下命令安装ceph相关依赖**

```shell
yum install -y openssl-devel
pip install prettytable
pip install werkzeug
pip install pyOpenSSL
```

**2) 所有节点安装ceph软件**

```
yum -y install ceph-14.2.8
```

注意ceph安装失败可以尝试执行yum install -y ceph-14.2.8 --allowerasing

**3) 在ceph1节点额外安装ceph-deploy**

```shell
pip install ceph-deploy
```

**4) ceph-deploy工具适配openEuler系统**

```shell
vi /lib/python2.7/site-packages/ceph_deploy/hosts/__init__.py
```

![](https://support.huaweicloud.com/dpmg-kunpengsdss/zh-cn_image_0266583444.jpg)

增加以下内容

```
'openeuler': fedora,
```

## 4.2、部署MON节点

**以下操作均在在ceph1节点执行**

### **4.2.1、创建集群**

```shell
cd /etc/ceph
ceph-deploy new ceph1 ceph2 ceph3
```

### **4.2.2、修改ceph.conf配置文件**

```
vi /etc/ceph/ceph.conf
```

内容如下

```shell
[global]
fsid = f6b3c38c-7241-44b3-b433-52e276dd53c6
mon_initial_members = ceph1, ceph2, ceph3
mon_host = 192.168.3.166,192.168.3.167,192.168.3.168
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx

public_network = 192.168.3.0/24
cluster_network = 192.168.4.0/24

[mon]
mon_allow_pool_delete = true
```

### **4.2.3、初始化监视器并收集密钥**

```shell
ceph-deploy mon create-initial
```

### 4.2.4、将ceph.client.admin.keyring拷贝到各个节点上

```shell
ceph-deploy --overwrite-conf admin ceph1 ceph2 ceph3 client1 client2 client3
```

### 4.2.5、查看状态

```shell
ceph -s
```

**回显如下**

```shell
cluster:
id:     f6b3c38c-7241-44b3-b433-52e276dd53c6
health: HEALTH_OK

services:
mon: 3 daemons, quorum ceph1,ceph2,ceph3 (age 25h)
```

## 4.3、部署MGR节点

**以下操作均在在ceph1节点执行**

### 4.3.1、创建MGR

```shell
ceph-deploy mgr create ceph1 ceph2 ceph3
```

### 4.3.2、查看状态

```shell
ceph -s
```

**回显如下**

```shell
cluster:
id:     f6b3c38c-7241-44b3-b433-52e276dd53c6
health: HEALTH_OK

services:
mon: 3 daemons, quorum ceph1,ceph2,ceph3 (age 25h)
mgr: ceph1(active, since 2d), standbys: ceph2, ceph3
```

## 4.4、部署OSD

### 4.4.1、清理数据盘

**1) 所有服务节点生成清理磁盘的脚本format_disk.sh**

```shell
cat > format_disk.sh <<EOF
#!/bin/bash
data_disk_list=($(lsblk|grep disk |grep -v nvme|grep -v $(lsblk|grep /boot/efi|awk '{print $1}'|grep -Eo '[a-zA-Z]+')|awk '{print $1}'))
vgs|grep ceph|awk '{print $1}'|xargs -i vgremove -y {}
dmsetup ls|grep ceph|awk '{print $1}'|xargs -i dmsetup remove {}
data_disk_num=11

echo ${#data_disk_list[*]}
# format disk
for ((i=0;i<${#data_disk_list[*]};i++))
do
    if [ ${data_disk_num} -le ${i} ];then
        break
    fi
    mkfs.ext4 -F /dev/${data_disk_list[i]}
done
EOF
```

**2) 执行磁盘格式化**

其中data_disk_num可修改为实际需要使用的磁盘数量

```shell
sh format_disk.sh
```



### 4.4.2、容量型

#### **1) nvme盘分区**

**以下命令在所有ceph节点执行**

**1) 生成mkpart.sh**

```shell
cat > mkpart.sh <<EOF
#!/bin/bash
db_wal_disk=$1
parted_num=$2
db_size=30
wal_size=15
unit=GiB

parted /dev/${db_wal_disk} mklabel gpt
index=1
for j in $(seq 1 ${parted_num})
do
start_index=$(echo ${index} ${db_size}|awk '{print $1 + $2}')
end_index=$(echo ${start_index} ${wal_size}|awk '{print $1 + $2}')
parted /dev/${db_wal_disk} mkpart primary ${index}${unit} ${start_index}${unit}
parted /dev/${db_wal_disk} mkpart primary ${start_index}${unit} ${end_index}${unit}
index=${end_index}
done
EOF
```

**2) 两块nvme盘分给11个osd（6+5）**

```shell
sh  mkpart.sh nvme0n1 6
sh  mkpart.sh nvme1n1 5
```

#### 2) 部署OSD节点

**以下命令在ceph1节点执行**

**1) 生成osd_create.sh脚本**

```shell
cat > osd_create.sh <<EOF
#!/bin/bash
for node in ceph1 ceph2 ceph3
do
data_disk_list=($(ssh ${node} "lsblk|grep disk |grep -v nvme|grep -v \$(lsblk|grep /boot/efi|awk '{print \$1}'|grep -Eo '[a-zA-Z]+')|awk '{print \$1}'"))
disk_index=0

# nmve0n1 6 osd
j=1
k=2
cd /etc/ceph
for m in $(seq 1 6)
do
    ceph-deploy osd create ${node} --data /dev/${data_disk_list[disk_index]} --block-wal /dev/nmve0n1p${k} --block-db /dev/nmve0n1p${j} 
((j=${j}+2))
((k=${k}+2))
((disk_index=${disk_index}+1))
done

# nmve1n1 5 osd
j=1
k=2
for m in $(seq 1 5)
do
    ceph-deploy osd create ${node} --data  /dev/${data_disk_list[disk_index]} --block-wal /dev/nmve1n1p${k} --block-db /dev/nmve1n1p${j} 

((j=${j}+2))
((k=${k}+2))
((disk_index=${disk_index}+1))
done
done
cd -

EOF
```
**2) 执行osd部署脚本**

```shell
sh osd_create.sh
```

**3) 创建成功后，查看是否正常，即33个OSD是否都为up**

```shell
ceph -s
```

### 4.4.3、bcache型

**<font color=red>注意需要内核支持bcache功能且PAGESIZE为4K，若不支持则需要编译一个支持bcache功能的内核并切换到对应内核</font>**

#### 1) 安装bcache

##### **编译支持bcache功能的内核**

参考文档：https://support.huaweicloud.com/fg-kunpengsdss/kunpengswc_20_0006.html

###### **1、安装依赖**

```shell
yum install -y ncurses-devel bc openssl-devel rpm-build bison flex rsync dwarves elfutils-libelf-devel
```

**dwarves、elfutils-libelf-devel软件包为5.X内核版本额外需要安装的依赖包**

###### **2、下载并编译内核源码**

****

```
wget  https://repo.openeuler.org/openEuler-20.03-LTS-SP3/source/Packages/kernel-4.19.90-2012.8.0.0131.oe1.src.rpm
rpm -ivh kernel-4.19.90-2012.8.0.0131.oe1.src.rpm
cd /root/rpmbuild && rpmbuild -bp kernel.spec
```

###### **3、拷贝当前系统.config并修改参数**

```
cd /root/rpmbuild/BUILD/kernel
cp /boot/config-$(uname -r) .config
make menuconfig
```

**进入图形化界面选择Device Drivers**

![](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001117164496.png)

**按Enter键进入下一级菜单，选择Multiple device driver support (RAID and LVM )**

![点击放大](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001117324398.png)

**按Enter键进入下一级菜单，选中Block device as cache，键盘输入M选中该配置。**

![点击放大](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001163564273.png)

**按两次exit返回至第一层。**

![点击放大](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001163524243.png)



**修改内核PAGESIZE大小为4K**

**选择Kernel Features**

![img](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001117164498.png)

**按Enter键进入下一级菜单，选择Page size（64KB）**

![点击放大](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001117324400.png)

**按Enter键进入选择，按Space键选择4KB**

![点击放大](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001163564275.png)

**按两次exit保存并退出**

![点击放大](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001163524245.png)

![点击放大](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001117164502.png)

**查看.config确认配置**

**a、确认Bcache模块打开**



![](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001163564281.png)

**b、确认PAGESIZE为4k**

![](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001163524257.png)

###### 4、编译bcache内核 

```shell
make binrpm-pkg
```

###### 5、安装bcache内核

**将内核包拷贝到所有ceph节点**

```
cd /root/rpmbuild/RPMS
rpm -ivh kernel*.rpm
```

**注意如果安装有问题，添加`--force`选项**

**安装完后执行重启切换内核**

```shell
reboot
```



##### **安装make-bcache工具**

**所有ceph节点安装make-bcache工具**

参考文档：https://support.huaweicloud.com/fg-kunpengsdss/kunpengswc_20_0009.html

###### **1、下载并解压源码**

```shell
cd /home/
wget https://github.com/g2p/bcache-tools/archive/refs/tags/v1.0.8.tar.gz --no-check-certificate
tar -zxvf v1.0.8.tar.gz
```

###### **2、安装依赖**

```shell
yum install libblkid-devel -y
```

###### **3、编译安装**

```shell
make
make install
```

###### **4、执行make-bcache命令**

![img](https://support.huaweicloud.com/fg-kunpengsdss/zh-cn_image_0000001113388170.png)



#### **2) nvme盘分区**

**以下命令在所有ceph节点执行**

**1) 生成mkpart.sh**

```shell
cat > mkpart.sh <<EOF
#!/bin/bash
db_wal_disk=$1
parted_num=$2
db_size=30
wal_size=15
bcache_size=200
unit=GiB

parted /dev/${db_wal_disk} mklabel gpt
index=1
for j in $(seq 1 ${parted_num})
do
start_index=$(echo ${index} ${db_size}|awk '{print $1 + $2}')
end_index=$(echo ${start_index} ${wal_size}|awk '{print $1 + $2}')
parted /dev/${db_wal_disk} mkpart primary ${index}${unit} ${start_index}${unit}
parted /dev/${db_wal_disk} mkpart primary ${start_index}${unit} ${end_index}${unit}
index=${end_index}
done

for j in $(seq 1 ${parted_num})
do
end_index=$(echo ${start_index} ${bcache_size}|awk '{print $1 + $2}')
parted /dev/${db_wal_disk} mkpart primary ${index}${unit} ${end_index}${unit}
index=${end_index}
done
EOF
```

**2) 两块nvme盘分给11个osd（6+5）**

```
sh  mkpart.sh nvme0n1 6
sh  mkpart.sh nvme1n1 5
```

#### 3) 创建Bcache设备

**以下命令在所有ceph节点执行**

**1) 生成make_bcache.sh**

```shell
cat > make_bcache.sh <<EOF
#!/bin/bash
data_disk_list=($(lsblk|grep disk |grep -v nvme|grep -v $(lsblk|grep /boot/efi|awk '{print $1}'|grep -Eo '[a-zA-Z]+')|awk '{print $1}'))
data_index=0
# nmve0n1 6 bcache
nvme_index=13
for m in $(seq 1 6)
do
	make-bcache -B /dev/${data_disk_list[data_index]} -C /dev/nvme0n1p${nvme_index}
((data_index=${disk_index}+1))
((nvme_index=${nvme_index}+1))
done

# nmve1n1 5 bcache
nvme_index=11
for m in $(seq 1 5)
do
	make-bcache -B /dev/${data_disk_list[data_index]} -C /dev/nvme0n1p${nvme_index}
((data_index=${disk_index}+1))
((nvme_index=${nvme_index}+1))
done
EOF
```

**2) 执行make_bcache.sh脚本,创建bcache**

```shell
sh make_bcache.sh
```

#### 4) 部署OSD节点

**以下命令在ceph1节点执行**

**1) 生成osd_bcache_create.sh脚本**

```shell
cat > osd_bcache_create.sh <<EOF
#!/bin/sh
for node in ceph1 ceph2 ceph3
do
bcache_list=($(ssh ${node} "lsblk|grep -C 1 sd|grep -Eo bcache[0-9]+|sort -u"))
bcache_index=0

# nmve0n1 6 osd
j=1
k=2
cd /etc/ceph
for m in $(seq 1 6)
do
    ceph-deploy osd create ${node} --data /dev/${bcache_list[bcache_index]} --block-wal /dev/nmve0n1p${k} --block-db /dev/nmve0n1p${j} 
((j=${j}+2))
((k=${k}+2))
((disk_index=${disk_index}+1))
done

# nmve1n1 5 osd
j=1
k=2
for m in $(seq 1 5)
do
    ceph-deploy osd create ${node} --data  /dev/${bcache_list[bcache_index]} --block-wal /dev/nmve1n1p${k} --block-db /dev/nmve1n1p${j} 

((j=${j}+2))
((k=${k}+2))
((disk_index=${disk_index}+1))
done
done
cd -	
EOF
```

**2) 执行创建osd脚本**

```shell
sh osd_bcache_create.sh
```

**3) 创建成功后，查看是否正常，即33个OSD是否都为up**

```shell
ceph -s
```

# 5、安装问题记录

## no module named werkzeug.serving

解决办法： pip install werkzeug 所有节点后重启服务

## Module 'restful' has failed dependency: No module named OpenSSL

install pyOpenSSL

## nothing provides libcrypto.so.10

强制安装openssl-libs-1.0.2k软件包

可以通过https://rpmfind.net/linux/rpm2html/search.php地址搜索获取对应系统的rpm包或者在centos7.6镜像源里找到对应的rpm包进行安装

## openEuler 22.03安装问题记录

需要额外安装libffi-3.1-28-fc34 和redhat-rpm-config-182-1-fc34这两个rpm包，才能正常安装ceph

可以通过https://rpmfind.net/linux/rpm2html/search.php地址搜索获取对应系统的rpm包

还需要额外给python2安装pip

```shell
cd /home
wget https://github.com/pypa/pip/archive/refs/tags/9.0.1.tar.gz
tar -xzf 9.0.1.tar.gz
cd pip-9.0.1
python2 setup.py install
```



