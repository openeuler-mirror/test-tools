
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
# chrony时间同步服务

```shell
mv /etc/chrony.conf /etc/chrony.conf-bak
```

/etc/chrony.conf写入以下内容

```shell
allow 172.168.0.0/16
local stratum 5
server 172.168.122.81 iburst
makestep 1.0 3
```

重启chrony服务

```shell
systemctl restart chronyd
```

# 配置NFS

```shell
chkconfig nfs on
chkconfig rpcbind on
```

修改/etc/exports的内容如下

```shell
/home/PXE/pxe_install_share *(ro)
```

重启

```shell
systemctl restart nfs
```

查看是否生效

```shell
[root@localhost ks]# showmount -e localhost

Export list for localhost:

/home/PXE/pxe_install_share *
```

# 安装cobblerd

参考文档：https://cnblogs.com/yanjieli/p/11016825.html

## 1、yum安装相关软件

```shell
yum -y install cobbler cobbler-web tftp-server dhcp httpd xinetd pykickstart fence-agents
```

## 2、启动cobbler、httpd

systemctl start httpd cobblerd

systemctl enable httpd cobblerd

## 3、服务配置

修改cobbler配置

```shell
sed -ri '/allow_dynamic_settings:/c\allow_dynamic_settings: 1' /etc/cobbler/settings

systemctl restart cobblerd

cobbler setting edit --name=server --value=192.168.30.81

cobbler setting edit --name=next_server --value=192.168.30.81
```

修改tftp配置

```shell
sed -ri '/disable/c\disable = no' /etc/xinetd.d/tftp

systemctl enable xinetd

systemctl restart xinetd
```

执行get-loaders、设置同步服务

 ```shell
cobbler get-loaders

systemctl start rsyncd

systemctl enable rsyncd
 ```

## 4、设置默认初始密码

```
openssl passwd -1 -salt `openssl rand -hex 4` 'admin'

cobbler setting edit --name=default_password_crypted --value='$1$675f1d08$oJoAMVxdbdKHjQXbGqNTX0'

cobbler setting edit --name=manage_dhcp --value=1
```

## 5、修改dhcp.templete

```shell
...

subnet 192.168.1.0 netmask 255.255.255.0 {

   option routers       192.168.30.5;

   option domain-name-servers 192.168.30.1;

   option subnet-mask     255.255.255.0;

   range dynamic-bootp    192.168.30.100 192.168.30.254;

   default-lease-time     21600;

   max-lease-time       43200;

   next-server        $next_server;

...
```



# 导入失败适配

## 1、openEuler适配

下载最新的distro_signature.json,并加入以下内容，fedora30下加入以下内容

 "openEuler": {

​       "signatures": [

​     "Packages"

​    ],

​    "version_file": "(openEuler|euleros)-release-(.*)\\.rpm",

​    "version_file_regex": null,

​    "kernel_arch": "kernel-(.*)\\.rpm",

​    "kernel_arch_regex": null,

​    "supported_arches": [

​     "aarch64",

​     "x86_64"

​    ],

​    "supported_repo_breeds": [

​     "rsync",

​     "rhn",

​     "yum"

​    ],

​    "kernel_file": "vmlinuz(.*)",

​    "initrd_file": "initrd(.*)\\.img",

​    "isolinux_ok": false,

​    "default_autoinstall": "sample.ks",

​    "kernel_options": "repo=$tree",

​    "kernel_options_post": "",

​    "boot_files": [],

​    "boot_loaders": {

​     "aarch64": [

​      "grub"

​     ]

​    }

   },

 

## 2、anlios适配

   "Anolis": {

​       "signatures": [

​     "BaseOS/Packages"

​    ],

​    "version_file": "anolis-release-(.*)\\.rpm",

​    "version_file_regex": null,

​    "kernel_arch": "kernel-(.*)\\.rpm",

​    "kernel_arch_regex": null,

​    "supported_arches": [

​     "aarch64",

​     "x86_64"

​    ],

​    "supported_repo_breeds": [

​     "rsync",

​     "rhn",

​     "yum"

​    ],

​    "kernel_file": "vmlinuz(.*)",

​    "initrd_file": "initrd(.*)\\.img",

​    "isolinux_ok": false,

​    "default_autoinstall": "sample.ks",

​    "kernel_options": "repo=$tree",

​    "kernel_options_post": "",

​    "boot_files": [],

​    "boot_loaders": {

​     "aarch64": [

​      "grub"

​     ]

​    }

},

将完整的distro_signatures.json放置在服务器到该处

/var/www/cobbler/pub/distro_signatures.json

并将setting的 signature_url改为

http://172.168.122.81/cobbler/pub/distro_signatures.json

执行

```shell
cobbler signature update
```





# x86环境适配

1、拷贝os的grubx64.efi到/var/lib/cobbler/loaders/grub下

2、修改/etc/cobbler/dhcp.templete

 ```shell
     # UEFI-64-1

	 else if option system-arch = 00:07 {
	 
       filename "grub/grubx64.efi";

    }

     # UEFI-64-2

     else if option system-arch = 00:08 {

      filename "grub/grubx64.efi";

     }

     # UEFI-64-3

     else if option system-arch = 00:09 {

      filename "grub/grubx64.efi";

     }
 ```



3、设置prefix

 修改/var/lib/cobbler/grub_config/grub/grub.cfg

```shell
prefix="(tftp, 192.168.30.81)/grub"
if [ "$grub_cpu" == "i386" ]; then
 set arch='x86_64'
elif [ "$grub_cpu" == "x86_64" ]; then
 set arch='x86_64'
elif [ "$grub_cpu" == "powerpc" ]; then
 set arch='ppc64le'
elif [ "$grub_cpu" == "arm64" ]; then
 set arch='aarch64'
......
```



# grub文件适配新选项

repo、ks、kssendmac修改适配为inst.repo、inst.ks、inst.ks.sendmac

/usr/lib/python3.7/site-packages/cobbler/tftpgen.py修改为以下内容

cd /usr/lib/python3.7/site-packages/cobbler

修改签名

```shell
sed -i "s#repo=$tree#inst.repo=$tree#g" /var/www/cobbler/pub/distro_signatures.json
```

更新签名

```shell
cobbler signature update
```



 
