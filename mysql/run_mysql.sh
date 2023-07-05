#!/bin/bash
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
systemctl stop irqbalance.service
systemctl disable irqbalance.service
systemctl stop iptables
systemctl stop firewalld
echo "测试场景(-a [action]) : "
echo "install(只安装)"
echo "all (即steal+hugepage+gazelle)"
echo "base （无优化，默认mysql+patch）"

echo "如跑all场景命令如下: sh -x run_mysql.sh -a all -b 5 -f mysql-8.0.20-all -t 192.168.1.10 -n enp4s0"
echo "无优化场景：sh -x run_mysql.sh -a base -b 5 -f mysql-8.0.20-No -t 192.168.1.10 -n enp4s0"
echo "二次跑全优化场景: sh -x run_mysql.sh -a rerun_all -b 5 -f mysql-8.0.20-all -t 192.168.1.10 -n enp4s0"
echo "二次跑无优化场景: sh -x run_mysql.sh -a rerun_base -b 5 -f mysql-8.0.20-No -t 192.168.1.10 -n enp4s0"
echo "仅完成环境部署场景：sh -x run_mysql.sh -a install -b 5 -f mysql-8.0.20-No -t 192.168.1.10 -n enp4s0"

#read -p "1.确认当前环境yum源已配置好"
#read -p "2.确认当前steal启动项已配好（sched_steal_node_limit=4）"


arch=$(uname -m)
Publicip=10.174.216.100
get_ip=$(ifconfig|grep 192.168.1| awk '{print $2}')
# --------------- default argments -------------------------
filename=mysql-8.0.20-613
datapath=/home/tpccdata
testip=192.168.1.10
mac()
{
	if [ $arch = "aarch64" ];then echo "44:a1:91:70:4a:44"; else echo "ac:b3:b5:2c:ed:7a"; fi
}
mac
mac=$(mac)
bindCore()
{
	
	if [ $arch = "aarch64" ];then echo "0-90"; else echo "0-75"; fi
}
bindCore
bindCore=$(bindCore)
interruptbind()
{
	if [ $arch = "aarch64" ];then echo "91 92 93 94 95"; else echo "76 77 78 79"; fi
}
interruptbind=$(interruptbind)
num=$(interruptbind|wc -w)
echo $num
cores=`lscpu | grep "CPU(s)" | head -n 1 | awk -F ' ' '{print $2}'`
networkname()
{
	if [ $arch = "aarch64" ];then echo "enp4s0"; else echo "enp4s0"; fi
}
networkname=$(networkname)
networkname
clientip()
{
	if [ $arch = "aarch64" ];then echo "10.174.217.39"; else echo "10.174.217.43"; fi
}
clientip=$(clientip)
clientip
# --------------- default argments (end) -------------------
affinity()
{
	eth1=$1
	cnt=$2
	bus=$3
	ethtool -L $eth1 combined $cnt
	irq1=`cat /proc/interrupts| grep -E ${bus} | head -n$cnt | awk -F ':' '{print $1}'`
	irq1=`echo $irq1`
	cpulist=(91 92 93 94 95)
	c=0
	for irq in $irq1
	do
		echo ${cpulist[c]} "->" $irq
		echo ${cpulist[c]} > /proc/irq/$irq/smp_affinity_list
		let "c++"
	done
}

help(){
	echo "Usage:"
	echo "run_mysql.sh [-a action] [-b bindnum] [-t testip] [-f filename] [-i interruptbind] [-m mac] [-n networkname] [-c clientip] [-d datapath]"
	echo "Description :"
	echo "action: "
	echo "bindnum:"
	echo "testip: default 192.168.1.10"
	echo "filename: default mysql-8.0.20"
	echo "interruptbind:"
	echo "mac:test mac address"
	echo "networkname,the name of server test networkname"
	echo "clientip,the client of ip"
	echo "path,the path of mysql testdata"
	exit 1 # 这个留在具体调用的地方写，正常返回0，异常返回1
}

# 使用action：分别对应环境安装、停止mysql、数据生成、数据导入、运行测试
# 堆大页和gazella通过选项控制使能，默认均使能
# 测试网卡名
# 需支持长选项
# 支持开启全优化:基线与全优化      -op gazella  heap_huge all xx xx base
while getopts 'a:t:f:i:n:p:h:b:c' OPT;do
	case $OPT in
	a) action="$OPTARG";;
	b) bindnum="$OPTARG";;
	t) testip="$OPTARG";;
	f) filename="$OPTARG";;
	i) interruptbind="$OPTARG";;
	m) mac="$OPTARG";;
	n) networkname="$OPTARG";;
	c) clientip="$OPTARG";;
	p) datapath="$OPTARG";;
	h) help;;
	?) help;;
	esac
done

echo $filename
echo $interruptbind
echo $bindnum
echo $mac
echo $testip
echo $networkname
echo $clientip
echo $datapath

affinity_nic()
{
	NIC=$1
	CPU=$2
	NUM=$3

	ethtool -l $NIC
	ethtool -L $NIC combined $NUM

	for irq in $(grep $NIC /proc/interrupts | head -n$NUM | awk '{print $1}' | sed -e 's/://g')
	do
        	echo $CPU > /proc/irq/$irq/smp_affinity_list
        	echo "echo $CPU > /proc/irq/$irq/smp_affinity_list"
        	((CPU += 1))
	done
	
}
echo $bindnum
cores=`lscpu | grep "CPU(s)" | head -n 1 | awk -F ' ' '{print $2}'`
echo $cores
cores=$(($cores-1-$bindnum))
echo $cores

num=$(interruptbind|wc -w)
#clientip=10.174.217.39
num=$(interruptbind |wc -w)
interruptbind=$( interruptbind | awk '{print $1}' ) 
echo interruptbind

Nopasswd(){
/usr/bin/expect <<EOF
        set timeout 30
        spawn ssh-copy-id   root@${Publicip}
        expect {
                "*yes/no" { send "yes\r";exp_continue }
                "*password:" { send "Huawei12#$\r" }
        }
        expect eof
        set timeout 30
        spawn ssh-copy-id   root@${clientip}
        expect {
                "*yes/no" { send "yes\r";exp_continue }
                "*password:" { send "Huawei12#$\r" }
        }
        expect eof

EOF
}

res1=$(ssh root@${clientip} -o PreferredAuthentications=publickey -o StrictHostKeyChecking=no "date" | wc -l)
res2=$(ssh root@${Publicip} -o PreferredAuthentications=publickey -o StrictHostKeyChecking=no "date" | wc -l)
if [ $res1 -eq 1 || $res2 -eq 1 ]; then
	echo "已配置免密"
else
	Nopasswd
fi
stop_mysql()
{
	#/usr/local/${filename}/bin/mysqladmin -uroot -p123456 -S/data/mysql/run/mysql.sock shutdown
	ps -ef |grep mysql |grep -v grep |grep -v run_mysql.sh|awk '{print $2}' |xargs kill -9
}


stop_mysql
if grep -q large_pages=1 /etc/my.cnf; then sed -i '/large_pages=1/d' /etc/my.cnf ;fi
install_mysql()
{
	yum install -y expect
	if [ ! -e "/home/mysql_deploy.tar.gz" ]; then
		scp -r root@${Publicip}:/deploy/mysql_deploy.tar.gz .
	else
                echo "The mysql test Dependency package is exists"
        fi
	yum install -y cmake doxygen bison ncurses-devel openssl-devel libtool tar rpcgen libtirpc-devel bison bc unzip git gcc-c++ libaio make
	if [ ! -e "/usr/local/${filename}" ]; then
		if [ ! -e "/home/mysql-8.0.20" ];then
			tar -xvf mysql_deploy.tar.gz
			tar -xvf mysql-8.0.20-patched_${arch}.tar.gz
			cp -r my.cnf${arch} /etc/my.cnf
			chmod -R +x mysql-8.0.20
		fi
		cd /home/mysql-8.0.20/cmake
		make clean
		cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local/${filename}  -DWITH_BOOST=../boost -DDOWNLOAD_BOOST=1
		make -j 64 && make install
	else
		echo "The version of mysql Package is exists!"
	fi
}

prepare_mysql_data()
{
	umount /dev/nvme0n1
	rm -rf /data
	mkfs.xfs /dev/nvme0n1 -f
	groupadd mysql
	useradd -g mysql mysql
	mkdir /data
	mount /dev/nvme0n1 /data
	rm -rf /data/mysql
	mkdir -p /data/mysql
	mkdir -p /data/mysql/data
	mkdir -p /data/mysql/run
	mkdir -p /data/mysql/share
	mkdir -p /data/mysql/log
	mkdir -p /data/mysql/tmp
	chown -R mysql:mysql /data
	chown -R mysql:mysql /data/mysql
	echo "" > /data/mysql/log/mysql.log
	chown -R mysql:mysql /data/mysql/log/mysql.log
}

init_mysql()
{
	/usr/local/${filename}/bin/mysqld  --defaults-file=/etc/my.cnf --user=root --initialize
	/usr/local/${filename}/support-files/mysql.server start
	sed -i 's/#skip-grant-tables/skip-grant-tables/g' /etc/my.cnf
	/usr/local/${filename}/support-files/mysql.server restart
	/usr/local/${filename}/bin/mysql -u root -p123456 <<EOF
	use mysql;
	Select * from user where user='root' \G;
	update user set password_expired='N' where user='root';
	Flush privileges;
	alter user 'root'@'localhost' identified by '123456';
	flush privileges;
	update user set host='%' where user='root';
	flush privileges;
	create database tpcc;
	quit
EOF
	sed -i 's/skip-grant-tables/#skip-grant-tables/g' /etc/my.cnf
	#/usr/local/${filename}/support-files/mysql.server restart
	ps -ef |grep mysql |grep -v grep |grep -v run_mysql.sh|awk '{print $2}' |xargs kill -9 
	sleep 3
	mkdir -p ${datapath}  # 考虑预置数据存储的位置，可默认
}

copy_mysql_data()
{
	#/usr/local/${filename}/support-files/mysql.server restart
	if [ ! -e ${datapath}/tpcc ]; then
		ssh ${clientip} -C "systemctl stop firewalld"
		ssh ${clientip} -C "cd /root/benchmarksql-5.0-hwsql/run && ./runDatabaseBuild.sh props.conf"
		sleep 15
		cp -r /data/mysql/data/* ${datapath}
		sleep 10
	else
		rm -rf /data/mysql/data/*
		cp -r ${datapath}/* /data/mysql/data/
	fi
}

manual_test()
{
    # affinity功能直接放本脚本
	#sed -i "s/cpulist=(91 92 93 94 95)/cpulist=($interruptbind)/g" 
	./affinity ${networkname} $num ${networkname}
	#./affinity_nic ${networkname} $interruptbind $num
	if [ $arch = "aarch64" ];then
		numactl -C 0-$cores -i 0-3  /usr/local/${filename}/bin/mysqld --defaults-file=/etc/my.cnf &
		sleep 60
	else
		sed -i "s/91 92 93 94 95/76 77 78 79/g" affinity
		./affinity $networkname $num $networkname
		numactl -C 0-$cores -i 0-1  /usr/local/${filename}/bin/mysqld --defaults-file=/etc/my.cnf &
		sleep 60
	fi
	ssh root@$clientip -C "cd /root/benchmarksql-5.0-hwsql/run && ./runBenchmark.sh props.conf"
}

enable_hugepage()
{
	ulimit -l unlimited #保证连续的内存驻留，以减少延迟并阻止分页和交换
	export GLIBC_TUNABLES=glibc.malloc.hugetlb=2   #启用glibc malloc堆大页
	echo `id mysql -g` > /proc/sys/vm/hugetlb_shm_group #启用mysql自身大页
	sed -i "s/server-id=1/server-id=1\nlarge_pages=1/g" /etc/my.cnf
}

enable_gazelle()
{
	yum install dpdk libconfig numactl libboundscheck libpcap gazelle
	modprobe vfio enable_unsafe_noiommu_mode=1
	modprobe vfio-pci
	sed -i "s/use_ltran=1/use_ltran=0/g" /etc/gazelle/lstack.conf
	if [ $arch = "aarch64" ];then
		ip link set ${networkname} down
		ifconfig ${networkname} down
		dpdk-devbind -b vfio-pci ${networkname}
		sed -i "s/2048,0,0,0/2048,2048,2048,2048/g" /etc/gazelle/lstack.conf
	else
		ip link set ${networkname} down
		dpdk-devbind -b vfio-pci ${networkname}
		sed -i "s/2048,0,0,0/2048,2048,0,0/g" /etc/gazelle/lstack.conf
	fi
	if grep -q num_wakeup /etc/gazelle/lstack.conf
	then
		echo "done"
	else
		sed -i "s/^.*num_cpus=.*$/num_cpus=\"18,38,58,78\"\nnum_wakeup=\"14,34,54,74\"/g" /etc/gazelle/lstack.conf
	fi
	sed -i "s/^.*devices=.*$/devices=\"${mac}\"/g" /etc/gazelle/lstack.conf
	#if [ ! -e /mnt/hugepages-2M ]; then mkdir -p /mnt/hugepages-2M; mount -t hugetlbfs nodev /mnt/hugepages-2M; else echo "done" ; fi
	mkdir -p /mnt/hugepages-2M && mount -t hugetlbfs nodev /mnt/hugepages-2M
}
tmpfs_hugepages()
{
	enable_tmpfs=1
	mkdir -p /var/mysql
	mountpoint -q /var/mysql || mount -t tmpfs -o huge=always tmpfs /var/mysql
	if [ ! -L /usr/local/$filename/bin/mysqld ];then
                cp /usr/local/$filename/bin/mysqld /usr/local/$filename/bin/mysqld.bak
                mv -f /usr/local/$filename/bin/mysqld /var/mysql
                ln -sf /var/mysql/mysqld /usr/local/$filename/bin/mysqld
        fi

}

reset_tmpfs_hugepages()
{
	if [ -L /usr/local/$filename/bin/mysqld ];then
                rm -rf /usr/local/$filename/bin/mysqld
                mv /usr/local/$filename/bin/mysqld.bak /usr/local/$filename/bin/mysqld
	fi
}



if [ -z $action ]; then
	echo "No action"
	help;
elif [ $action = "install" ]; then
	install_mysql	
	prepare_mysql_data
	init_mysql

elif [ $action = "all" ]; then
	reset_tmpfs_hugepages
	umount /mnt/hugepages-2M
	echo 0 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
	install_mysql
	prepare_mysql_data
	init_mysql
	copy_mysql_data
	echo STEAL > /sys/kernel/debug/sched_features
	enable_hugepage
	enable_gazelle
	tmpfs_hugepages
	echo 138192 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
	LD_PRELOAD=/usr/lib64/liblstack.so GAZELLE_BIND_PROCNAME=mysqld /usr/local/${filename}/bin/mysqld --defaults-file=/etc/my.cnf --bind-address=${testip} &
	sleep 35
	ssh root@${clientip} -C "cd /root/benchmarksql-5.0-hwsql/run && ./runBenchmark.sh props.conf"

elif [ $action = "base" ]; then
	reset_tmpfs_hugepages
	umount /mnt/hugepages-2M
	echo 0 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
	install_mysql
	prepare_mysql_data
	init_mysql
	copy_mysql_data
	echo STEAL > /sys/kernel/debug/sched_features
	manual_test

elif [ $action = "rerun_base" ]; then
	stop_mysql
	rm -rf /data/mysql/data/* && cp -r ${datapath}/* /data/mysql/data
	manual_test

elif [ $action = "rerun_all" ]; then
	stop_mysql
	rm -rf /data/mysql/data/* && cp -r ${datapath}/* /data/mysql/data
	sleep 3
	LD_PRELOAD=/usr/lib64/liblstack.so GAZELLE_BIND_PROCNAME=mysqld /usr/local/${filename}/bin/mysqld --defaults-file=/etc/my.cnf --bind-address=${testip} &
	sleep 35
	ssh root@${clientip} -C "cd /root/benchmarksql-5.0-hwsql/run && ./runBenchmark.sh props.conf"
fi

