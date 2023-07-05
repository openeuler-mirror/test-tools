1、脚本目录介绍
============

|---ceph_test # 根目录

​	|---conf # 配置目录

​		|---cluster_info.cfg # ceph集群配置信息

​		|---fio.cfg # fio相关参数

​		|---testcase.cfg # 测试用例配置

​	|---bin # 脚本目录

​		|--bcache_watch.sh # 查看bcache信息的脚本

​		|---clean_bcache_data.sh # bcache盘卸载安装加快脏数据清理

​		|---env_pre.sh # 环境准备脚本

​		|---fio_test.sh # 执行fio测试的脚本

​		|---lib.sh # 封装的函数

​		|---optimize.sh # 进行优化的脚本

​		|---pre_data.sh # 执行预埋数据的脚本

​		|---fio-3.19.tar.gz # fio源码包，用来进行源码安装fio

​	|---pgbalance # pg均衡相关目录

​		|---run.sh # 执行pg均衡的入口脚本

​		|---readme # 步骤说明

​		|---primarypgbalancer-opt-arm-v3 # pg均衡用到的可执行文件

​		|---primarypgbalancer-opt-x86-v3 # pg均衡用到的可执行文件

​	|---all_testcase.sh # 所有用例的执行入口

​	|---all_bcache_testcase.sh # 所有用例执行入口，bcache场景做了优化操作

2、配置说明
========

2.1、cluster\_info.cfg 
-----------------------

| 参数名      | 示例                       | 解释             |
| ----------- | -------------------------- | ---------------- |
| server_list | (ceph1 ceph2  ceph3)       | ceph节点名数组   |
| client_list | (client1 client2  client3) | client节点名数组 |

**测试脚本需要获取ceph节点和client节点名，去连接到各个环境执行不同操作**

2.2、fio.cfg
------------

| 参数名     | 示例    | 解释                    |
| ---------- | ------- | ----------------------- |
| runtime    | 180     | fio运行的时间           |
| ramp_time  | 30      | 爬坡时间                |
| pool_name  | vdbench | 创建的池子名            |
| pg_num     | 1024    | 创建池子时所指定的pg数  |
| pgp_num    | 1024    | 创建池子时所指定的pgp数 |
| image_name | image   | 创建的image名称前缀     |
| image_num  | 30      | 创建的image数量         |
| image_size | 100G    | image的大小             |
| numjobs    | 1       | fio文件中配置的job数    |
| iodeph     | 64      | 队列深度                |

**基线测试时，该文件保持统一无需更改**

2.3、testcase.cfg 
------------------

| 参数名        | 示例   | 解释                         |
| ------------- | ------ | ---------------------------- |
| block_size    | 1024K  | 块大小                       |
| operate       | randrw | 读写类型                     |
| read_ratio    | 70     | 读写混合中读的百分比         |
| is_bcache     | false  | 是否bcache场景               |
| bcache_detach | true   | bcache场景下是否进行卸盘动作 |

3、脚本使用介绍
============

3.1、bcache\_watch.sh
---------------------

执行方式： sh bcache\_watch.sh

脚本功能：查看bcache设备的信息

3.2、clean\_bcache\_data.sh
---------------------------

执行方式： sh clean\_bcache\_data.sh

脚本功能： 将当前环境的bcache设置卸载再挂载，加快脏数据落盘

3.3、env\_pre.sh
----------------

1\) 准备环境

执行方式： sh env\_pre.sh pre

脚本功能： 根据fio.cfg创建pool和image,并执行pg均衡

2)  清理环境

执行方式： sh env\_pre.sh clean

脚本功能： 删除集群的pool

3.4、optimize.sh
----------------

### 3.4.1、所有cpeh节点执行优化

执行方式： sh optimize.sh all

脚本功能： 修改系统磁盘参数，io直通优化

### 3.4.2、查看所有cpeh节点修改的参数

执行方式： sh optimize.sh check

脚本功能： 查看修改系统参数

**3.4.3、恢复所有cpeh节点参数**

执行方式： sh optimize.sh recovery

脚本功能： 将执行sh optimize.sh all后修改修改系统参数还原

### 3.4.4、所有cpeh节点开启io直通

执行方式： sh optimize.sh write\_through

脚本功能： 执行io直通操作

### 3.4.4、所有cpeh节点关闭io直通

执行方式： sh optimize.sh write\_back

脚本功能： 执行io直通操作

3.5、pre\_data.sh
-----------------

执行方式： sh pre\_data.sh run

脚本功能： 通过1M顺序写将所有image写满

3.6、fio\_test.sh
-----------------

执行方式： sh fio\_test.sh run

脚本功能： 根据testcase.cfg的参数配置，执行fio测试

4、执行所有测试用例
================

4.1、不做优化
-------------

bcache场景：sh all\_testcase.sh run bcache

容量型场景：sh all\_testcase.sh run nomal

4.2、io直通优化
---------------

需要做优化的时候使用all\_bcache\_testcase.sh脚本，该脚本多会多执行一组4K随机混合读写（关闭io直通）

bcache场景：sh all\_bcache\_testcase.sh run bcache

容量型场景：sh all\_bcache\_testcase.sh run nomal

5、结果查看
========

cat report/fio.report

![img](http://image.huawei.com/tiny-lts/v1/images/3be5f4d48c3e092154613c96b5dcaab2_961x264.png@900-0-90-f.png)

