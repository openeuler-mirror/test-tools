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
# 1、测试工具

参考文档https://support.huaweicloud.com/tstg-kunpengsdss/kunpengcephblock_11_0006.html

## 1.1、fio简介

fio是一个开源的IO压力测试工具，主要用来测试存储的IO性能，可以支持多种引擎，本文测试时选用rbd引擎。fio配置灵活多样，支持多客户端并发测试（server、client模式）

| 参数         | 含义                                                         |
| ------------ | ------------------------------------------------------------ |
| ioengine     | IO引擎fio支持多种引擎如：cpuio、mmap、sync、psync、vsync、pvsync、pvsync2、null、net、netsplice、ftruncate、filecreate、libaio、posixaio、falloc、e4defrag、splice、rados、rbd、mtd、sg、io_uring |
| clientname   | Ceph用户                                                     |
| pool         | Ceph的存储池                                                 |
| rbdname      | Ceph RBD镜像名                                               |
| direct       | IO类型，direct=1表明采用non-buffered io，direct=0表明采用buffered io |
| rw           | 读写类型rw=read：顺序读rw=write：顺序写rw=randread：随机读rw=randwrite：随机写rw=rw：顺序混合读写rw=randrw：随机混合读写 |
| bs           | IO块大小                                                     |
| size         | 读写的数据量                                                 |
| iodepth      | 队列深度                                                     |
| numjobs      | job副本数                                                    |
| runtime      | fio执行时间                                                  |
| time_based   | 即使file已被完全读写或写完，也要执行完runtime规定的时间      |
| log_avg_msec | 设定日志采集间隔，单位为毫秒（ms）                           |
| ramp_time    | 在记录任何性能信息之前要运行特定负载的时间, 这个用来等性能稳定后，再记录日志结果，因此可以减少生成稳定的结果需要的运行时间 |
| thread       | fio默认会使用fork()创建job，如果这个选项设置的话，fio将使用pthread_create来创建线程 |
| rwmixread    | 读写混合测试中读取占的百分比                                 |
| stonewall    | 如果一个job文件里包含多个测试任务，加上这个参数会等上一个任务结束后再启动下一个任务 |

## 1.2、fio安装

**以下操作在所有client节点执行**

**1）直接yum安装**

```shell
yum -y install fio 
```

**2) 编译安装**

```shell
cd /home
wget https://git.kernel.dk/cgit/fio/snapshot/fio-3.19.tar.gz
tar -zxvf fio-3.19.tar.gz
cd fio-3.19
# 安装rbd引擎依赖
yum -y install librbd-devel
# 编译安装fio
./configure && make && make install
```

**注意：安装librbd-devel需要配置ceph源，参考环境部署文档配置源**

# 2、测试模型

测试的Ceph集群包含3个物理节点，每个节点部署1个mon，1个mgr，11个osd。

## 2.1、容量型-块存储

| **名称**    | **规格** | **解释**                                                     |
| ----------- | -------- | ------------------------------------------------------------ |
| ceph服务端  | 3台      | ceph节点数量                                                 |
| ceph客户端  | 3台      | ceph客户端数量                                               |
| mon数量     | 1*3      | 每个ceph节点1个mon                                           |
| mgr数量     | 1*3      | 每个ceph节点1个mgr                                           |
| osd数量     | 11*3     | 每个ceph节点11个osd，osd均分到ceph的三个节点，创建osd的方式 1.2T机械盘 + nvme盘分区（wal分区15G +db分区30G） |
| 存储池数量  | 1个      | -                                                            |
| image数量   | 30个     | 100G的image共30个，数据量为3T                                |
| fio并发数量 | 30个     | 均分到三个客户端                                             |

## 2.2、Bcache型-块存储

| **名称**    | **规格** | **解释**                                                     |
| ----------- | -------- | ------------------------------------------------------------ |
| ceph服务端  | 3台      | ceph节点数量                                                 |
| ceph客户端  | 3台      | ceph客户端数量                                               |
| mon数量     | 1*3      | 每个ceph节点1个mon                                           |
| mgr数量     | 1*3      | 每个ceph节点1个mgr                                           |
| osd数量     | 11*3     | 每个ceph节点11个osd，osd均分到ceph的三个节点，创建osd的方式 bcache设备 + nvme盘分区（wal分区15G +db分区30G) |
| 存储池数量  | 1个      | -                                                            |
| image数量   | 30个     | 100G的image共30个，数据量为3T                                |
| fio并发数量 | 30个     | 均分到三个客户端                                             |

**说明：bcache设备的创建是由1.2T机械盘+nvme分区200G**

# 3、测试准备

**注意：以下操作在client1节点执行，bcache型和容量型的预埋数据方法一致**

## 3.1、环境检查（重要 ! ! !）

**1) 检查bios选项，确认关闭SMMU和cpu预取**

**2)  ceph服务检查**

​	执行ceph -s命令查看集群状态，osd状态，告警信息，确认无异常信息

**若为bcache环境请检查好bcache设备是否正常，确认指定的nvme分区是否为200G，并在所有bcache执行watch.sh脚本，查看bcache设备状态确认无异常**

watch脚本内容

```shell
n=`ls /sys/block |grep bcache |wc -l`
#echo $n
LINE="------------------------------------------------------------------------------------------------------"
echo $LINE
echo `hostname`
j=$n
CACHEMODE="cachemode"
HITRATIO="hit%"
READAHEAD="rdahd"
SEQCUTOFF="seqcf"
WBPER="wb%"
WBDELAY="wbdly"
DIRTYDATA="dtydata"
STAT="stat"
CACHEPER="cache%"
BYPASS="bypass"
echo $LINE
echo -e "bcacheNo.\0011$HITRATIO\0011$BYPASS\0011$CACHEMODE\0011$READAHEAD\0011$SEQCUTOFF\0011$WBPER\0011$WBDELAY\0011$DIRTYDATA\0011$STAT\0011$CACHEPER"
echo $LINE
for i in `ls /sys/block |grep bcache`
do
        cd /sys/block/${i}/bcache
        cache_mode=`for k in {1..4};do cat cache_mode |cut -d " " -f $k |grep "\[" |sed 's/\[//g' |sed 's/\]//g';done`
        hitratio=`cat stats_five_minute/cache_hit_ratio`
        bypass=`cat stats_five_minute/bypassed`
        readahead=`cat readahead`
        seq_cutoff=`cat sequential_cutoff`
        wbper=`cat writeback_percent`
        wbdelay=`cat writeback_delay`
        dirtydata=`cat dirty_data`
        stat=`cat state`
        cache=`cat cache/cache_available_percent`
        echo -e "${i} \0011$hitratio\0011$bypass\0011$cache_mode\0011$readahead\0011$seq_cutoff\0011$wbper\0011$wbdelay \0011$dirtydata \0011$stat\0011$cache"
done
```

## 3.2、创建存储池

创建名字为data_pool、pg、pgp数量均为1024

```shell
ceph osd pool create data_pool 1024 1024
```

## 3.3、创建image

执行如下命令，在存储池上创建30个大小为100G的image

```shell
for index in $(seq 1 30); do rbd create image${index} --size 100G --pool data_pool --image-format 2 --image-feature layering;done
```

## 3.4、预埋数据(1024K顺序写)

### **1)、生成预埋数据的脚本**

```shell
cat > pre_data.sh <<EOF
#!/bin/bash
server_list=(ceph1 ceph2 ceph3)
client_list=(client1 client2 client3)
pool_name=data_pool
image_name=image
image_num=30
rw=write
block_size=1024K
size=100%

test_cmd="fio "
count=0
client_num=${#client_list[@]}

# 启动fio server
for client in ${client_list[@]}
do
 ssh ${client} "killall -9 fio"
 sleep 2
 ssh -f ${client} "mkdir -p /home/fio_server;fio -S 2>&1 >> /home/fio_server/fio_server.log"
done
sleep 2

# 生成fio文件
for i in $(seq 1 ${image_num})
do 
  cat >> ${block_size}_image${i}_${rw}.fio  <<EOF
[global]  
ioengine=rbd  
clientname=admin  
pool=${pool_name} 
size=${size} 
direct=1  
numjobs=1  
ramp_time=30
log_avg_msec=500  
thread  
rbdname=${image_name}${i}  
[${block_size}-${rw}]  
bs=${block_size}  
rw=${rw}  
iodepth=64
write_bw_log=${block_size}-${rw} 
stonewall  
buffer_compress_percentage=40
EOF

# 组装fio命令
test_cmd="${test_cmd} --client=${client_list[${count}]} ${block_size}_image${i}_${rw}.fio"

count=$((${count} + 1))
if [[ ${count} -eq ${client_num} ]]
then
    count=0
fi
done

# 预埋数据
test_cmd="${test_cmd} --output=./${block_size}-${rw}-$(date +%m-%d-%T).log"

echo $test_cmd
${test_cmd}

# 杀掉fio server
for client in ${client_list[@]}
do
 ssh ${client} "killall -9 fio"
done
EOF
```

**脚本基本逻辑描述：**

1、启动fio server进程

2、生成30个1M顺序写的fio文件（每个fio文件对应一个image），并组装fio命令(将30个fio文件均分到每个客户端)

3、执行fio命令

4、杀掉fio server

### 2)、执行数据预埋脚本

```shell
sh pre_data.sh
```

### 3)、查看预埋的数据

```shell
rbd du -p data_pool
```

**执行完命令后查看所有的image是否写满均为100G**

# 4、测试执行

**注意：1、以下步骤均在client1节点执行**

​			**2、测试用例的执行顺序必须先1M混合读写 > 4K随机写 > 4K随机混合读写** 

  		  **3、bcache场景测试前需要额外多执行一步操作(清理bcache脏数据保证数据稳定性)**

## 4.1、生成测试脚本

```shell
cat > fio_test.sh <<EOF
#!/bin/bash
server_list=(ceph1 ceph2 ceph3)
client_list=(client1 client2 client3)
pool_name=data_pool
image_name=image
image_num=30
block_size=$1
rw=$2
size=100%
numjobs=1
iodeph=64
runtime=180
ramp_time=30

# iops单位转换
get_iops_value()
{
  unit=$(echo $1|grep -Eo '[a-zA-Z]+')
  iops_value=$(echo $1|grep -Eo '[0-9]+([.][0-9]+)?')
  if [[ "${unit}" = "K" || "${unit}" = "k" ]];then
    echo ${iops_value}|awk '{printf $1 * 1000}'
  elif [[ "${unit}" = "" ]];then
    echo ${iops_value}
  else
    echo "iops unit ${unit} not support !"
    exit 1
  fi
}

test_exec()
{
test_cmd="fio "

count=0
client_num=${#client_list[@]}

# 清理服务端缓存
for server in ${server_list[@]}
do
 ssh ${server} "echo 3 > /proc/sys/vm/drop_caches"
done
sleep 2
# 启动 fio server
for client in ${client_list[@]}
do
 ssh ${client} "killall -9 fio"
 sleep 2
 ssh -f ${client} "mkdir -p /home/fio_server;fio -S 2>&1 >> /home/fio_server/fio_server.log"
done

sleep 2

# 生成fio文件
for i in $(seq 1 ${image_num})
do
  cat >> ${block_size}_image${i}_${operate}.fio  <<EOF
[global]
ioengine=rbd
clientname=admin
pool=${pool_name}
size=${image_size}
direct=1
numjobs=${numjobs}
ramp_time=${ramp_time}
runtime=${runtime}
time_based
log_avg_msec=500
thread
rbdname=${image_name}${i}
EOF

if [[ "${operate}" == "rw" || "" == "randrw" ]]
then

cat >> ${block_size}_image${i}_${operate}.fio  <<EOF
rwmixread=${read_ratio}
EOF

fi

cat >> ${block_size}_image${i}_${operate}.fio  <<EOF

[${block_size}-${operate}]
bs=${block_size}
rw=${operate}
iodepth=${iodeph}
write_bw_log=${block_size}-${operate}
stonewall
buffer_compress_percentage=40
EOF

# 组合fio测试命令
test_cmd="${test_cmd} --client=${client_list[${count}]} ${block_size}_image${i}_${operate}.fio"

count=$((${count} + 1))
if [[ ${count} -eq ${client_num} ]]
then
    count=0
fi
done

test_cmd="${test_cmd} --output=${block_size}-${operate}.log"

echo $test_cmd

${test_cmd}

# 杀掉fio进程
for client in ${client_list[@]}
do
 ssh ${client} "killall -9 fio"
done

# 处理fio测试结果
report_file=fio.report
if [ ! -e ${report_file} ];then
  touch ${report_file}
  printf "%-15s%-10s    %-10s  %-10s    %-15s%-15s   %-15s\n" "time" "block_size" "operate" "read_ratio" "iops" "bandwidth/M" "bandwidth_total/M" >> ${report_file}
fi
read_iops=$(cat ${block_size}-${operate}.log|grep -A 14 'All clients:'|grep "read: IOPS"|tail -n 1|awk -F '[=,]+' '{print $2}')
read_bandwidth=$(cat ${block_size}-${operate}.log|grep -A 14 'All clients:'|grep "read: IOPS"|tail -n 1|awk -F "[()]" '{print $2}')
write_iops=$(cat ${block_size}-${operate}.log|grep -A 14 'All clients:'|grep "write: IOPS"|tail -n 1|awk -F '[=,]+' '{print $2}')
write_bandwidth=$(cat ${block_size}-${operate}.log|grep -A 14 'All clients:'|grep "write: IOPS"|tail -n 1|awk -F "[()]" '{print $2}')
if [[ "${operate}" = "rw" || "${operate}" = "randrw" ]];then
  read_iops=$(get_iops_value ${read_iops})
  write_iops=$(get_iops_value ${write_iops})
  report_read_ratio=${read_ratio}
  iops="${read_iops}/${write_iops}"
  bandwidth="${read_bandwidth}/${write_bandwidth}"
  iops_total="$(echo ${read_iops} ${write_iops}|awk '{print $1 + $2}')"
elif [[ "${operate}" = "read" || "${operate}" = "randread" ]];then
  report_read_ratio="100"
  iops="$(get_iops_value ${read_iops})"
  bandwidth="${read_bandwidth}"
  iops_total="${iops}"
else
  report_read_ratio="0"
  iops="$(get_iops_value ${write_iops})"
  bandwidth="${write_bandwidth}"
  iops_total="${iops}"
fi
if [[ "${is_bcache}" != "true" ]];then
   is_bcache=false
fi

printf  "%-15s%-10s    %-10s    %-10s    %-15s%-15s   %-15s\n"  $(date +%m%d%H%M%S) ${block_size} ${operate}  ${report_read_ratio} ${iops} ${bandwidth} ${iops_total} >> ${report_file}

}

test_exec

EOF

```

**脚本基本逻辑与预埋数据基本一样，多了一步处理fio结果的步骤**



## 4.2、执行1M混合读写测试

```
sh fio_test.sh 1024K rw 
```

**可以多测试几次取平均值结果，可以查看fio.report文件或者1024K-rw.log文件**

## 4.3、执行4K随机写测试

```shell
sh fio_test.sh 4K randwrite 
```

**可以多测试几次取平均值结果，可以查看fio.report文件或者4K-randwrite.log文件**

## 4.4、执行4K随机混合读写测试

```shell
sh fio_test.sh 4K randrw 
```

**可以多测试几次取平均值结果，可以查看fio.report文件或者4K-randrw.log文件**

**注意：如果为容量型测试则每执行一次4K随机混合读写，则需要重启一次osd保证数据的稳定性**

```shell
ssh ceph1 "systemctl restart ceph-osd.target"
ssh ceph2 "systemctl restart ceph-osd.target"
ssh ceph3 "systemctl restart ceph-osd.target"
```

## 4.5、bcache清理脏数据

**注意点:**

**1、bcache测试脚本和测试用例与容量型场景一致，只需要额外做一步操作，每次bcache测试前需要将脏数据落盘**

**2、请保证clean_bcache_data.sh和clean_bcache.sh在同一级目录下**

**3、只需在client1执行clean_bcache.sh脚本即可**

### **4.5.1 生成clean_bcache_data.sh脚本**

```shell
cat > clean_bcache_data.sh <<EOF
#!/bin/bash
caches=$(ls /sys/block/ | grep bcache)
bcaches=()
uids=()
devs=()
for i in $caches
do
	uid=`ls -al /sys/class/block/$i/bcache/cache  | awk -F '/' '{print $NF}'`
	dev=`ls -al /sys/fs/bcache/$uid/cache0 | awk -F '/' '{print $(NF-1)}'`
	echo $i $uid $dev
	uids=(${uids[@]} ${uid})
	devs=(${devs[@]} ${dev})
	bcaches=(${bcaches[@]} ${i})
done 

let n=${#bcaches[@]}-1

for ((i=0;i<=$n; i ++))
do
	echo "detache ${devs[$i]} from cache"
	echo "echo ${uids[$i]} > /sys/block/${bcaches[$i]}/bcache/detach"
	echo ${uids[$i]} > /sys/block/${bcaches[$i]}/bcache/detach
	sleep 1s
done

date
#controller by manual
##touch bcache.lock
while true
do
	if [ -f bcache.lock ]; then
		sleep 1s
	else
		break
	fi
done

while true
do
	str=`cat /sys/block/bcache*/bcache/state | grep -v "no cache" |grep -v "clean"`
	if [ "$str" == "" ];then
		echo "detach ok"
		break
	else
		sleep 1s
	fi
done
date

for ((i=0;i<=$n; i ++))
do
	echo "attache ${devs[$i]} to cache"
	echo "echo ${uids[$i]} > /sys/block/${bcaches[$i]}/bcache/attach"
	echo ${uids[$i]} > /sys/block/${bcaches[$i]}/bcache/attach
	sleep 1s
done
EOF
```

### **4.5.2 生成clean_bcache.sh脚本**

```shell
cat > clean_bcache.sh <<EOF
server_list=(ceph1 ceph2 ceph3)
for server in ${server_list[@]}
do
echo ${server}
bcache_list=$(ssh ${server} "ls /sys/block|grep bcache")
for bcache in ${bcache_list}
do
ssh ${server} "echo 0 > /sys/block/${bcache}/bcache/writeback_delay"
ssh ${server} "echo 0 > /sys/block/${bcache}/bcache/writeback_percent"
sleep 1
ssh ${server} "echo 1 > /sys/block/${bcache}/bcache/cache/internal/trigger_gc"

done
done

sleep 30
# clean bcache data
for server in ${server_list[@]}
do
  scp clean_bcache_data.sh ${server}:/home
  ssh -f ${server} "sh /home/clean_bcache_data.sh"
done
# check bcache disk
for server in ${server_list[@]}
do
while true
do
flag=$(ssh ${server} "cat /sys/block/bcache*/bcache/state|grep -v clean|grep -v 'no cache'")
if [[ "${flag}" == "" ]]
then
echo ${server} disk is ok

break
else
echo sleep 1
sleep 1

fi
done
done

# bcache start
for server in ${server_list[@]}
do
echo ${server}
bcache_list=$(ssh ${server} "ls /sys/block|grep bcache")
for bcache in ${bcache_list[@]}
do
ssh ${server} "echo writeback >/sys/block/${bcache}/bcache/cache_mode"
ssh ${server} "echo 0 >/sys/block/${bcache}/bcache/sequential_cutoff"
ssh ${server} "echo 40 >/sys/block/${bcache}/bcache/writeback_percent"

ssh ${server} "echo 1000 > /sys/block/${bcache}/bcache/writeback_delay"
ssh ${server} "echo 0 > /sys/block/${bcache}/bcache/cache/congested_read_threshold_us"
ssh ${server} "echo 0 > /sys/block/${bcache}/bcache/cache/congested_write_threshold_us"

done
sleep 1
done
EOF

```

### 4.5.3 清理bcache脏数据

```shell
sh clean_bcache.sh
```

**等待脚本执行完即可再次执行测试用例，每执行完一次测试均需要执行该脚本**

# 5、测试调优

## 5.1、pg均衡

**如果发现磁盘io不均衡，且发现磁盘io为瓶颈时，可以进行pg均衡来提高性能，在client1执行即可**。

primarypgbalancer-opt-arm-v3、primarypgbalancer-opt-x86-v3需要自行获取

1) 生成pgblance.sh

```shell
cat > pgblance.sh <<EOF
#!/bin/bash
ceph pg dump pgs|awk '{print $1,$17}' > pgdump
ceph osd tree up > osdtree
if [[ "$(arch)" = "aarch64" ]];then
  ./primarypgbalancer-opt-arm-v3 pgdump osdtree > newpgmap
elif [[ "$(arch)" = "x86_64" ]];then
  ./primarypgbalancer-opt-x86-v3 pgdump osdtree > newpgmap
else
  echo "pg balance not support arch $(arch)"
  exit 1
fi
ceph osd set-require-min-compat-client luminous --yes-i-really-mean-it
source ./newpgmapss
EOF
```

2) 执行pgblance.sh

```shell
sh pgblance.sh
```

## 5.2、IO直通等参数优化

**在client1节点执行脚本即可**

1）生成optimize.sh

```shell
cat > optimize.sh <<EOF
#!/bin/bash
server_list=(ceph1 ceph2 ceph3)
for server in ${server_list[@]}
do
  echo ${server} optimize
  data_disk_list=($(ssh ${server} "lsblk|grep disk |grep -v nvme|grep -v \$(lsblk|grep /boot/efi|awk '{print \$1}'|grep -Eo '[a-zA-Z]+')|awk '{print \$1}'|grep sd"))

  for disk in ${data_disk_list[*]}
  do
        ssh ${server} "echo mq-deadline > /sys/class/block/${disk}/queue/scheduler"
        ssh ${server}  "echo 128 > /sys/class/block/${disk}/device/queue_depth"
        ssh ${server} "echo 256 > /sys/block/${disk}/queue/nr_requests"

        ssh ${server} "yum install hdparm -y"
        ssh ${server} "hdparm -W /dev/${disk}"
        sleep 0.5
        ssh ${server} "hdparm -W 0 /dev/${disk}"

        ssh ${server} "echo write through> /sys/class/block/${disk}/queue/write_cache"
done
done

EOF
```

2) 执行优化脚本

```shell
sh optimize.sh
```

## 5.3、bios优化项

### 5.3.1、关闭SMMU

1）进入bios设置界面

2）依次进入Advanced > MISC Config

3）将Support Smmu选项的值设置为Disabled，并保存退出

### 5.3.2、关闭预取

1）进入bios设置界面

2）依次进入Advanced > MISC Config

3）将CPU Prefetching Configuration选项的值设置为Disabled，并保存退出

