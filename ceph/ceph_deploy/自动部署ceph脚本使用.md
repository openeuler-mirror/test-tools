1、脚本目录介绍
============

|---ceph_dploy # 根目录

​	|---conf # 配置目录

​		|---cluster_conf.yaml # ceph集群配置信息

​		|---conf.yaml # pip代理和系统代理配置

​		|---repo_file # repo源配置文件

​	    	|---ceph.repo # ceph源

​			|---arch_fedora.repo # fedora额外源

​			|---openeuler_20.03_LTS-SP3_aarch64.repo # 对应系统源

​			...... # 后续支持系统的源均放置在这个目录

​	|---system_compatible # 系统兼容性目录

​		|---openeuler_20.03_LTS-SP3 # 对应系统目录兼容性适配目录

​			|---adapter.sh # 必须有该脚本，该脚本的作用是适配系统保证ceph软件可以安装到该系统，以及支持bcahce-tools工具安装，后续兼容系统时需保持主体框架一致

​			..... # 省略，adapter.sh脚本需要用到的一些文件和rpm包，

   	|---centos_7.6.1810

​			......

​	|---ceph_env.py # 实现ceph安装卸载的主体脚本

​	|---install.py # 执行ceph安装的入口

​	|---uninstall.py # 执行ceph卸载的入口

2、配置说明
========

2.1、conf.yaml内容说明
----------------------

1、proxy节点

系统代理的配置，配置该参数，则脚本在执行yum install ，pip
install命令时，向环境设置的代理参数

2、pip节点

pip源地址配置，该节点下的参数可以控制脚本在执行pip
install时所指定的源地址

2.2、cluster\_conf.yaml参数说明
-------------------------------

### **2.2.1、ceph_common节点配置参数解释**

| 参数名              | 示例                                    | 解释                                                         |
| ------------------- | --------------------------------------- | ------------------------------------------------------------ |
| public_net          | 192.168.144.0                           | public网段                                                   |
| public_gateway      | 192.168.144.1                           | public网段的网关                                             |
| public_mask         | 255.255.255.0                           | public子网掩码                                               |
| cluster_net         | 192.168.2.0                             | cluster网段                                                  |
| cluster_gateway     | 192.168.2.1                             | cluster网段的网关                                            |
| cluster_mask        | 255.255.255.0                           | cluster子网掩码                                              |
| username            | root                                    | ssh用户名，建议填写root,不填默认root                         |
| password            | \*\*\*\****                             | username用户对应的密码                                       |
| port                | 22                                      | ssh端口，    不填默认22                                      |
| ntp_server          | 172.168.144.9                           | chrony时间服务器地址                                         |
| osd_per_node_num    | 11                                      | 每个节点osd数量                                              |
| osd_per_dev         | 1                                       | 每块机械盘对应的osd数目                                      |
| db_size             | 30                                      | 创建osd指定的db分区大小，单位是mkpart_unit对应的值           |
| wal_size            | 15                                      | 创建osd指定的wal分区大小，单位是mkpart_unit对应的值          |
| mkpart_unit         | GiB                                     | nvme盘分区时指定的单位                                       |
| rgw_per_node        | 6                                       | 每个节点rgw数量                                              |
| firewall_open       | N                                       | 防火墙是否打开，Y或yes不进行操作，否则都将关闭防火墙         |
| ceph_version        | 14.2.8                                  | ceph安装时指定的版本                                         |
| nvme_disk           | nvme0n1 nvme1n1                         | 用到的nvme盘，格式可以以空格，逗号作为分隔符，或者[nvme1,nvme2]表示 |
| data_disk           | sda sdb sdd                             | 用到的nvme盘，格式可以以空格，逗号作为分隔符，或者[sda,sdb]表示，**可以不填，脚本会去检测非系统的sd盘** |
| local_rpm           | N                                       | 是否使用本地rpm包安装ceph, Y或yes使用本地rpm                 |
| local_rpm_path      | /home/ceph/local_rpm/ceph-14.2.8.tar.gz | 当前环境的ceph编译好的rpm包路径，压缩包必须为tar gz格式打成以tar.gz结尾的包，且解压后的目录与包名一致 |
| replace_system_repo | Y                                       | 是否替换系统的repo文件， Y或yes为是                          |
| is_bacache          | N                                       | 是否为bcache安装， Y或yes为是                                |
| bcache_size         | 200                                     | nvme盘上需要分多大空间给bcache使用                           |

### 2.2.2、servers节点配置参数解释

| 二级参数        | 三级参数        | 示例                 | 解释                                                         |
| --------------- | --------------- | -------------------- | ------------------------------------------------------------ |
| ceph1（主机名） | manager_ip      | 172.168.144.10       | 管理口ip，用来连接os系统进行操作的ip                         |
|                 | public_netcard  | [enp133s0, enp134s0] | public网段需要使用的网卡名，可以通过空格、逗号做分隔符或者[net1,net2]，单独网口名配置ip，多个网口则组bond（bond模式为6） |
|                 | public_ip       | 192.168.144.10       | 该节点在public网段下的ip                                     |
|                 | cluster_netcard | [enp135s0, enp136s0] | cluster网段需要使用的网卡名，可以通过空格、逗号做分隔符或者[net1,net2]，单独网口名配置ip，多个网口则组bond（bond模式为6） |
|                 | cluster_ip      | 192.168.2.10         | 该节点在cluster网段下的ip                                    |
|                 | mgr             | Y                    | 该节点是否安装mgr, Y或yes为是                                |
|                 | mon             | Y                    | 该节点是否安装mon, Y或yes为是                                |
|                 | osd             | Y                    | 该节点是否安装osd, Y或yes为是                                |
|                 | mds             | N                    | 该节点是否安装mds, Y或yes为是                                |
|                 | rgw             | N                    | 该节点是否安装rgw, Y或yes为是                                |
|                 | username        | root                 | ssh用户名，建议填写root,不填默认root                         |
|                 | password        | ********             | username用户对应的密码                                       |
|                 | port            | 22                   | ssh端口，    不填默认22                                      |
|                 | osd_num         | 11                   | 该节点下的osd数量，该参数用来限制osd数目，与ceph_common节点下osd_per_node_num作用一样，当前参数优先级高 |
|                 | nvme_disk       | nvme0n1 nvme1n1      | 用到的nvme盘，格式可以以空格，逗号作为分隔符，或者[nvme1,nvme2]表示 |
|                 | data_disk       | sda sdb sdd          | 用到的nvme盘，格式可以以空格，逗号作为分隔符，或者[sda,sdb]表示，可以不填，脚本会去检测非系统的sd盘 |

**注意：ceph_common节点下与servers下的三级同名参数均配置时, 三级同名参数优先级高**

### 2.2.3、clients节点配置参数解释

| 二级参数          | 三级参数                 | 示例                            | 解释                                                         |
| ----------------- | ------------------------ | ------------------------------- | ------------------------------------------------------------ |
| client1（主机名） | manager_ip    manager_ip | public_netcard    172.168.144.7 | 管理口ip，用来连接os系统进行操作的ip                         |
|                   | public_netcard           | [enp133s0, enp134s0]            | public网段需要使用的网卡名，可以通过空格、逗号做分隔符或者[net1,net2]，单独网口名配置ip，多个网口则组bond（bond模式为6） |
|                   | public_ip                | 192.168.144.7                   | 该节点在public网段下的ip                                     |
|                   | username                 | root                            | ssh用户名，建议填写root,不填默认root                         |
|                   | password                 | \*\*\*\***                      | username用户对应的密码                                       |
|                   | port                     | 22                              | ssh端口，不填默认22                                          |

**注意：ceph\_common节点下与clients下的三级同名参数均配置时，三级同名参数优先级高，如果不存在客户端, 当前clients可以不配置**

3、执行脚本 
=========

1)  、**检查参数，并到环境上核对所填写参数无误后执行下一步操作**

2)  、执行python3 install.py脚本

3)  、若无异常，等待20分钟左右即可完成ceph环境安装，在终端可以观察到成功日志打印

![img](http://image.huawei.com/tiny-lts/v1/images/7355024aac7382f909393b3ade64f1ea_664x249.png@900-0-90-f.png)

4、日志查看
========

日志目录在脚本根目录的logs下有对应节点的日志信息，可自行查看

5、系统兼容性适配
==============

兼容性适配主要解决的是ceph包依赖问题，故该部分功能不同系统差异较大，从脚本逻辑中拆出来，解决方案是通过一个adapter.sh脚本处理兼容性问题，并支持bcache-tools安装，这样适配新的操作系统只需修改该脚本逻辑即可

**1、该脚本需要支持三个调用方法**

1\) 适配系统的调用

sh adapter.sh run

2)  检测是否适配完成，成功的情况必须输出 adapter success

sh adapter.sh check

3)  安装bcache-tools工具

sh adapter.sh bcache

该脚本必须放置在system\_compatible/{systemname}\_{version}目录下

**2、目录命名规则：**

查看系统版本命令：cat /etc/system-release

​	a）openEuler系统需要加LTS版本示例：

​		查到信息：openEuler release 20.03 (LTS-SP3)，

​		示例：openeuler\_20.03\_LTS\_SP3

​		规则：openeuler\_{version}\_{lts\_version}

​	b）非openeuler系统

​		查到信息：CentOS Linux release 7.6.1810 (Core)

​		示例：centos\_8.2.2004

​		规则：{system\_name}\_{version}
