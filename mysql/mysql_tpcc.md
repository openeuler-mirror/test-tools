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
# mysql tpcc测试 

​				 
## 环境要求
### 1） 硬件要求
要求服务端（Server）、客户端（Client）各一台，硬件具体要求如下表所示。

​	

|      |              Server              |        Client        |
| ---- | :------------------------------: | :------------------: |
| CPU | Kunpeng 920-4826 * 2 | Kunpeng 920-4826 * 2 |
| 主频   |2600MHz                                  | 2600MHz |
| 内存大小 | 12 * 32G Micron 2666 MHz | 8 * 32G Micron 2666 MHz |
| 网络 |         1822 25G                         |    1822 25G                  |
| 系统盘 | 1.1T HDD TOSHIBA | 1.1T HDD TOSHIBA  |
| 数据盘 | 3T HUAWEI SSD NVME |  NA|



### 2） 软件要求



软件要求如下：
		

|   软件名称   |  版本  |
| :----------: | :----: |
|    mysql     | 8.0.20 |
| benchmarksql |  5.0   |

### 3） 集群环境规划



物理组网方式如下图：

 	![img](http://image.huawei.com/tiny-lts/v1/images/ba93c493d0085d35fe3dfc932f34d8b2_868x210.png@900-0-90-f.png)

网络配置如下表：
	

| 集群   | 管理IP        | 业务UP          |
| ------ | ------------- | --------------- |
| Server | 10.174.217.37 | 192.168.1.10/24 |
| Client | 10.174.217.39 | 192.168.11/24    |

### 4） 关键参数



Mysql关键参数配置如下：

| 配置项 | 值   | 描述 |
| -------- | ---- | ---- |
|    Innodb_flush_log_at_trx_commit      |     1 |  提交事务时将redo日志写入磁盘中，0~2，设置值为0时该模式速度最高。    |
|       Sync_binlog   |    0  |   同步binlog   |
|    innodb_io_capacity      |  36368    |   刷新脏数据时，控制MySQL每秒执行的写IO量   |
|        innodb_write_io_threads  |   161   |    后台写IO的线程数  |
|   innodb_read_io_threads       |  27    |   后台读IO的线程数   |

Tpcc关键参数配置如下：

| 配置项    | 值   | 描述                              |
| --------- | ---- | --------------------------------- |
| Terminals | 300  | 压力测试的并发数量。 |
| runMins   | 10   | 压力测试运行时间（单位：分钟）                                  |

 	注：Server（服务）端：1台  client（客户）端：1台  两台环境需选定同等规格网卡进行配置，如server和client均使用1822网卡，server端及client端网卡信息先后设置为192.168.1.10/24、192.168.1.11/24，关闭防火墙（systemctl stop firewalld）后确保两张网卡可直连。 
 	

# 一. Server端服务配置搭建



## 1.部署mysql



### 1.1 配置epel源

在所有集群和客户端节点执行下列操作以配置epel源。
	（1） 将OS对应的everything镜像源文件上传到服务器。
    通过SFTP工具将“openEuler-***-everything-aarch64-dvd.iso”上传到服务器上“/root”目录下.
	（2） 创建一个本地文件夹用于挂载本地镜像。
	（3） 将iso文件挂载到本地文件夹。
	（4） 创建镜像yum源。
	

### 1.2 安装依赖包

		yum install  -y cmake doxygen bison ncurses-devel openssl-devel libtool tar rpcgen libtirpc-devel bison bc unzip git gcc-c++ libaio libaio-devel numactl

### 1.3 安装mysql

#### 		1.3.1 获取mysql-boost-8.0.20.tar.gz

​				获取地址如下：

​						https://downloads.mysql.com/archives/community/

#### 		1.3.2 部署mysql-boost-8.0.20.tar.gz

			tar -xvf mysql-boost-8.0.20.tar.gz
			chmod -R +x mysql-boost-8.0.20
#### 		1.3.3（可选）对mysql包进行特性优化

​				注：此处优化不影响mysql测试功能，但对性能跑分会有明显提升

​				1）获取patch

​						细粒度锁优化特性补丁：

​						https://objects.githubusercontent.com/github-production-release-asset-2e65be/276785729/82c6c000-99f6-11eb-9332-f45eb18910e9?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20220510%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220510T030125Z&X-Amz-Expires=300&X-Amz-Signature=950e19a743d8bf65b9dfa7d3d813263716e874b690eb24e4a39b809169a1f27b&X-Amz-SignedHeaders=host&actor_id=0&key_id=0&repo_id=276785729&response-content-disposition=attachment%3B%20filename%3D0001-SHARDED-LOCK-SYS.patch&response-content-type=application%2Foctet-stream

​						无锁优化特性补丁：

​						https://objects.githubusercontent.com/github-production-release-asset-2e65be/276785729/064f9f00-a28a-11eb-96b9-f9a013783ffe?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20220510%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220510T030504Z&X-Amz-Expires=300&X-Amz-Signature=7624dc3aa40cb4faa50a3ed7642a9af82eb995f47030888065753345279db7ea&X-Amz-SignedHeaders=host&actor_id=0&key_id=0&repo_id=276785729&response-content-disposition=attachment%3B%20filename%3D0002-LOCK-FREE-TRX-SYS.patch&response-content-type=application%2Foctet-stream

​						NUMA调度补丁：

​						https://objects.githubusercontent.com/github-production-release-asset-2e65be/276785729/7f148d80-b19c-11eb-8129-f154224a0ce9?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20220510%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220510T030609Z&X-Amz-Expires=300&X-Amz-Signature=67788e9ce85f6a1d7773693689bc300bb4109f3b7b55cdf3ed0b6d596e0f838d&X-Amz-SignedHeaders=host&actor_id=0&key_id=0&repo_id=276785729&response-content-disposition=attachment%3B%20filename%3D0001-SCHED-AFFINITY.patch&response-content-type=application%2Foctet-stream

​				2）安装优化补丁

​						下载git工具包

```
			yum install git 
```

​						进入mysql主目录

```
			cd mysql-boost-8.0.20
```

​						源码git初始化

```
			git init
			git add -A
```

​						注：若未配置git的提交用户信息，git commit前需要先配置用户邮件及用户名称信息			

```
			git config user.email "123@example.com"		
         	 git config user.name "123"
```

​							再进行git commit提交

```
			git commit -m "init"
```

​							应用补丁

```
			git am --whitespace=nowarn 0001-SHARDED-LOCK-SYS.patch
			git am --whitespace=nowarn 0001-SCHED-AFFINITY.patch
			git am --whitespace=nowarn 0002-LOCK-FREE-TRX-SYS.patch
```

​							注：之后可通过"git status"查看修改情况，如下所示新增了所加patch：

​								

```
			Refresh index: 100% (42716/42716), done.
			On branch master
      	     Changes not staged for commit:
             (use "git add <file>..." to update what will be committed)
             (use "git restore <file>..." to discard changes in working directory)
                modified:   0001-SCHED-AFFINITY.patch
                modified:   0001-SHARDED-LOCK-SYS.patch
                modified:   0002-LOCK-FREE-TRX-SYS.patch
```

#### 1.3.4  安装mysql

​		进入cmake路径下先后进行配置及编译安装，如下：

			cd mysql-boost-8.0.20/cmake
			cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local/mysql-8.0.20  -DWITH_BOOST=../boost -DDOWNLOAD_BOOST=1
			make -j 64
			make install


### 1.4 初始化mysql并创建basedir

​				部署配置文件my.cnf至/etc下并创建basedir。在测试过程中发现不同架构对应最优配置不同，因而arm与x86在配置上做了区分，my.cnf arm环境具体内容如下：





		[mysqld_safe]
	    log-error=/data/mysql/log/mysql.log
	    pid-file=/data/mysql/run/mysqld.pid
	
	    [client]
	    socket=/data/mysql/run/mysql.sock
	    default-character-set=utf8
	
	    [mysqld]
	    server-id=1
	    #log-error=/data/mysql/log/mysql.log
	    #basedir=/usr/local/mysql
	    socket=/data/mysql/run/mysql.sock
	    tmpdir=/data/mysql/tmp
	    datadir=/data/mysql/data
	    default_authentication_plugin=mysql_native_password
	    port=3306
	    user=root
	
	    max_connections=2000
	    back_log=4000
	    performance_schema=OFF
	    max_prepared_stmt_count=128000
	
	    #file
	    innodb_file_per_table
	    innodb_log_file_size=2048M
	    innodb_log_files_in_group=32
	    innodb_open_files=10000
	    table_open_cache_instances=64
	
	    #buffers
	    innodb_buffer_pool_size=230G
	    innodb_buffer_pool_instances=16
	    innodb_log_buffer_size=2048M
	    innodb_undo_log_truncate=OFF
	
	    #tune
	    default_time_zone=+8:00
	    #innodb_numa_interleave=1
	    thread_cache_size=2000
	    sync_binlog=1
	    innodb_flush_log_at_trx_commit=1
	    innodb_use_native_aio=1
	    innodb_spin_wait_delay=180
	    innodb_sync_spin_loops=25
	    innodb_flush_method=O_DIRECT
	    innodb_io_capacity=30000
	    innodb_io_capacity_max=40000
	    innodb_lru_scan_depth=9000
	    innodb_page_cleaners=16
	
	    #perf special
	    innodb_flush_neighbors=0
	    innodb_write_io_threads=1
	    innodb_read_io_threads=1
	    innodb_purge_threads=1
	
	    sql_mode=STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION,NO_AUTO_VALUE_ON_ZERO,STRICT_ALL_TABLES
	
	    log-bin=mysql-bin
	    skip_log_bin
	    ssl=0
	    table_open_cache=30000
	    max_connect_errors=2000
	    innodb_adaptive_hash_index=0
	    mysqlx=0

​		x86 my.cnf具体内容如下:

    [mysqld_safe]
    log-=/data/mysql/log/mysql.log
    pid-file=/data/mysql/run/mysqld.pid
    [client]
    socket=/data/mysql/run/mysql.sock
    default-character-set=utf8
    
    [mysqld]
    server-id=1
    #log-error=/data/mysql/log/mysql.log
    #basedir=/usr/local/mysql
    socket=/data/mysql/run/mysql.sock
    tmpdir=/data/mysql/tmp
    datadir=/data/mysql/data
    default_authentication_plugin=mysql_native_password
    port=3306
    user=root
    #innodb_page_size=4k
    
    max_connections=2000
    back_log=4000
    performance_schema=OFF
    max_prepared_stmt_count=128000
    #transaction_isolation=READ-COMMITTED
    #skip-grant-tables
    
    #file
    innodb_file_per_table
    innodb_log_file_size=1802M
    innodb_log_files_in_group=18
    innodb_open_files=10000
    table_open_cache_instances=64
    
    #buffers
    innodb_buffer_pool_size=230G
    innodb_buffer_pool_instances=23
    innodb_log_buffer_size=159M
    
    #tune
    default_time_zone=+8:00
    #innodb_numa_interleave=1
    thread_cache_size=2000
    sync_binlog=0
    innodb_flush_log_at_trx_commit=1
    innodb_use_native_aio=1
    innodb_spin_wait_delay=12
    innodb_sync_spin_loops=436
    innodb_flush_method=O_DIRECT
    innodb_io_capacity=36368
    innodb_io_capacity_max=40000
    innodb_lru_scan_depth=12
    innodb_page_cleaners=19
    innodb_thread_concurrency=280
    #innodb_spin_wait_pause_multiplier=25
    
    #perf special
    innodb_flush_neighbors=0
    innodb_write_io_threads=161
    innodb_read_io_threads=27
    innodb_purge_threads=32
    
    sql_mode=STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION,NO_AUTO_VALUE_ON_ZERO,STRICT_ALL_TABLES
    
    log-bin=mysql-bin
    skip_log_bin
    ssl=0
    table_open_cache=30000
    max_connect_errors=2000
    innodb_adaptive_hash_index=0
    mysqlx=0
### 1.5 创建basedir并挂载

    	mkdir -p /data
    	mount  /dev/nvme0n1 /data
        mkdir -p /data/mysql
        mkdir -p /data/mysql/data
        mkdir -p /data/mysql/share
        mkdir -p /data/mysql/tmp
        mkdir -p /data/mysql/run
        mkdir -p /data/mysql/log
        groupadd mysql
        useradd -g mysql mysql
        chown -R mysql:mysql /data
        echo "" > /data/mysql/log/mysql.log
        chown -R mysql:mysql /data/mysql/log/mysql.log

### 1.6 数据库初始化及登录配置

​		初始化：

```
	/usr/local/mysql-8.0.20/bin/mysqld  --defaults-file=/etc/my.cnf --user=root --initialize
```

​		启动服务：

```
	/usr/local/mysql-8.0.20/support-files/mysql.server start
```

​		完成初始化后会随机生成一个密码，用其登陆mysql：

```
	/usr/local/mysql-8.0.20/bin/mysql -u root -p
	alter user 'root'@'localhost' identified by '123456';
    flush privileges;
```

​		再次登陆数据库，更新root账号能够访问的域为%，从而可以支持远程访问：

	    use mysql;
	    update user set host='%' where user='root';
	    flush privileges;
	    create database tpcc;
	    quit
​		重启服务使配置生效

```
	/usr/local/mysql-8.0.20/support-files/mysql.server restart
```

### 1.7 启动服务及绑核

​		到此重启可直接在客户端进行数据创建及测试，如不加任何调优手段，建议进行手动绑中断及服务绑核启动（会有明显的性能优化效果），且在arm和x86环境下需做区分，具体如下：

​		绑中断：

​				（1） 修改如下affinity中断脚本部署在环境

		    #!/bin/bash
	        eth1=$1
	        cnt=$2
	        bus=$3
	        ethtool -L $eth1 combined $cnt
	        irq1=`cat /proc/interrupts| grep -E ${bus} | head -n$cnt 		| awk -F ':' '{print $1}'`
	        irq1=`echo $irq1`
	        cpulist=(91 92 93 94 95)
	        c=0
	        for irq in $irq1
	        do
	        echo ${cpulist[c]} "->" $irq
	        echo ${cpulist[c]} > /proc/irq/$irq/smp_affinity_list
	        let "c++"
	        done
​		 以上affinity脚本中cpulist=(91 92 93 94 95)，该行（）中91...95为中断绑核数，即指定中断到91 92 93 94 95这五个核上来处理（96核arm环境可绑定91 92 93 94 95，80核x86环境可绑定76 77 78 79）

​				（2） 绑定中断(enp4s0为测试用网卡名）

```
		./affinity enp4s0 5 enp4s0
```

​					绑核起启服务：

​						处理服务核数绑定处理中断核数外所有，即96核arm环境：	

```
		numactl -C 0-90 -i 0-3  /usr/local/mysql-8.0.20/bin/mysqld --defaults-file=/etc/my.cnf &
```

​					    在80核x86环境上：

```
		numactl -C 0-75 -i 0-1  /usr/local/mysql-8.0.20/bin/mysqld --defaults-file=/etc/my.cnf &
```

注：绑核与绑中断需要根据环境情况来适量分配，可通过测试时观察htop表现情况进行进一步确定，确认每个核无100%使用率的情况，且表现均匀。

### 1.8 关闭测试影响项

​	关闭irqbalance:

```
systemctl stop irqbalance.service
systemctl disable irqbalance.service
```

​	关闭防火墙:

```
systemctl stop iptables
systemctl stop firewalld
```

# 二、 Client端配置及测试



## 	1. 部署benchmarksql工具



### 		1.1 获取地址

​			https://mirrors.huaweicloud.com/kunpeng/archive/kunpeng_solution/database/patch/benchmarksql5.0-for-mysql.zip

### 		1.2 部署工具包到client端环境上解压

```shell
		unzip benchmarksql5.0-for-mysql.zip
```
### 		1.3 安装依赖工具包

			yum install -y java
### 		1.4 赋权限

			chmod 777 *.sh
## 	2.配置参数及创建测试数据

​	

```
	cd /home/benchmarksql-5.0/run
```

​		修改分页表类型：

```
	mv sql.mysql/tableCreates.sql sql.mysql/tableCreates.sql-bak
	mv sql.mysql/tableCreates_partition.sql sql.mysql/tableCreates.sql
```

### 2.1 修改props.conf如下

			db=mysql
	        driver=com.mysql.cj.jdbc.Driver
	        conn=jdbc:mysql://192.168.1.10:3306/tpcc?useSSL=false&useServerPrepStmts=true&useConfigs=maxPerformance&rewriteBatchedStatements=true
	        user=root
	        password=123456
	        profile=/etc/my.cnf
	        data=/data/mysql/data
	        backup=/data/mysql/backup
	
	        warehouses=1000
	        loadWorkers=100
	        terminals=300
	        terminalWarehouseFixed=true
	        runMins=10
	
	        runTxnsPerTerminal=0
	        limitTxnsPerMin=1000000000
	        newOrderWeight=45
	        paymentWeight=43
	        orderStatusWeight=4
	        deliveryWeight=4
	        stockLevelWeight=4  
  注：192.168.1.10:3306这里需要根据实际设置的server端测试网卡ip以及端口来指定

### 2.2 创建测试数据

```
		./runDatabaseBuild.sh props.conf
```

注：完成测试数据创建后，建议对server端/data/mysql/data下数据进行备份,之后如需测试，数据从此拷贝即可

```
		mkdir /home/tpccdata
		cp -r /data/mysql/data/* /home/tpccdata
```

## 	3. mysql测试

​		执行如下命令即可开展测试：

```
	./runBenchmark.sh props.conf
```

​		最终结果呈现形式如下：

​	![img](http://image.huawei.com/tiny-lts/v1/images/cdfadb5d1918de1bbd6b75aac314dc75_937x334.png@900-0-90-f.png)
​	tpm（transactions per minute）每分钟事物处理个数。
​	最终性能跑分即为Measured tpmC(NewOrders)的值，即609590.95
​	
注：tpcc属于CPU密集型测试，测试过程中可通过htop、topc等工具观察性能实时跑分情况，增长基本呈由大到小态势，且瞬时得分可通过Running Average tpmTOTAL值 * 0.45 计算获得



# 三、 Mysql优化项



## 	1. STEAL优化



### 		1.1 修改启动项

		在/etc/grub2-grub2-efi.cfg中BEGIN /etc/grub.d/10_linux模块中系统启动项末尾添加参数sched_steal_node_limit=4，修改如下图所示：

​	![img](http://image.huawei.com/tiny-lts/v1/images/859a04d7c9515b544dc2644c2385c6de_1456x306.png@900-0-90-f.png)

​			修改完成后进行reboot重启生效

### 		1.2 设置STEAL模式

​			重启后进行设置如下：

		echo STEAL > /sys/kernel/debug/sched_features

## 	2. Gazelle优化

​			以下均在Server端完成

### 		2.1 安装工具包

		yum install dpdk libconfig numactl libboundsheck libcap gazelle
### 		2.2 修改配置文件

```
	vi /etc/gazelle/lstack.conf
```

​			use_ltran配置为0

​			根据实际配置NUMA分配均匀

​			num_cpus配置为18,38,58,78

​			与num_cpus一一对应，不要连续的cpu，因为x86会2核超线程，默认无此配置项表示不使用，添加上去即可。

​			num_wakeup配置为14,34,54,74

​			表示每个numa占用的大页内存

​			dpdk_args=["--socket-mem", "2048,0,0,0"，若4个numa使用修改为"2048, 2048, 2048, 2048"，x86环境两个numa可修改为"2048,2048,0,0"

​			devices= "aa:bb:cc:dd:ee:ff"改为实际网卡mac地址

​			以上具体设置图示如下：

![img](http://image.huawei.com/tiny-lts/v1/images/3d26607c42809d1039f3833fbfb36529_1181x225.png@900-0-90-f.png)

### 			2.3 分配内存大页

		echo 8192 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages	
		mkdir -p /mnt/hugepages-2M
		mount -t hugetlbfs nodev /mnt/hugepages-2M #不要重复执行，会一直占有大页内存
### 			2.4 加载模块及设置业务网卡

​				加载模块

```
		modprobe vfio
		enable_unsafe_noiommu_mode=1
		modprobe vfio-pci
```

 				拔业务网卡及绑定vfio-pci协议

			ip link set enp63s0 down
			dpdk-devbind -b vfio-pci enp63s0 
​				注：enp63s0为业务网卡名

### 			2.5 gazelle测试服务启动

​				如下命令启动mysql：

			LD_PRELOAD=/usr/lib64/liblstack.so GAZELLE_BIND_PROCNAME=mysqld /usr/local/mysql-8.0.20/bin/mysqld --defaults-file=/etc/my.cnf --bind-address=192.168.1.10 &

​				注：192.168.1.10为server端业务网卡ip

## 		3. 分配大页优化

### 			3.1 预先分配供mysql使用的大页		

```
		numactl -m 0-3 echo 130000 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
```

​			注：130000 由下述公式取个合理值，视具体情况而定

​	（innodb_buffer_pool_size+innodb_additional_mem_pool_size+innodb_log_buffer_size+tmp_table_size+max_heap_table_size）/2m

### 			3.2 保证连续的内存驻留，以减少延迟并阻止分页和交换

			ulimit -l unlimited
### 			3.3 启用glibc malloc堆大页

			export GLIBC_TUNABLES=glibc.malloc.hugetlb=2
### 			3.4 启用mysql自身大页

​				1） 命令设置如下：

```
		echo `id mysql -g` > /proc/sys/vm/hugetlb_shm_group
```

​				2） 打开/etc/my.cnf，设置large_pages=1，图示如下：

![img](http://image.huawei.com/tiny-lts/v1/images/f35c8f8d5fcc1999f05ff2b8c1ea444d_442x189.png@900-0-90-f.png)

​				3） 重启mysql服务生效

```
		#如为mysql.server启动：
			/usr/local/mysql-8.0.20/support-files/mysql.server restart
		#如为gazelle参数启动：
			ps -ef|grep mysql #查找进程
			kill -9 [PID]
			D_PRELOAD=/usr/lib64/liblstack.so GAZELLE_BIND_PROCNAME=mysqld /usr/local/mysql-8.0.20/bin/mysqld --defaults-file=/etc/my.cnf --bind-address=192.168.1.10 &
```

​				4） 取消系统预分配的大页(跑完后可选择恢复)

```
		numactl -m 0-3 echo 0> /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
```

## 		4.tmpfs优化

​			tmpfs优化添加：

```
	enable_tmpfs=1
	mkdir -p /var/mysql
	mountpoint -q /var/mysql || mount -t tmpfs -o huge=always tmpfs /var/mysql
	cp /usr/local/mysql-8.0.20/bin/mysqld /usr/local/$filename/bin/mysqld.bak
	mv -f /usr/local/mysql-8.0.20/bin/mysqld /var/mysql
	ln -sf /var/mysql/mysqld /usr/local/$filename/bin/mysqld
```

​       tmpfs优化取消：

```
	rm -rf /usr/local/mysql-8.0.20/bin/mysqld
	mv /usr/local/mysql-8.0.20/bin/mysqld.bak /usr/local/mysql-8.0.20/bin/mysqld
```

注：是否生效启用可通过perf命令查看(iTLB-load-misses值会明显变小）:

```
	perf stat -e dTLB-load-misses -e dTLB-store-misses -e iTLB-load-misses -e branch-misses -e cache-misses -e L1-dcache-load-misses -e L1-icache-load-misses -e branch-load-misses -a -- sleep 10
```


​		
