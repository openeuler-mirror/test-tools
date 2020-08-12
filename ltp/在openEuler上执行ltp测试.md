## 在openEuler上执行ltp测试



### 1.获取ltp测试套件

```shell
git clone https://github.com/linux-test-project/ltp.git
```



### 2.安装依赖

```shell
yum -y install gcc git make pkgconf autoconf automake bison flex m4 kernel-headers glibc-headers
```

```shell
yum -y install autoconf automake make clang gcc findutils libtirpc libtirpc-devel pkg-config redhat-lsb-core
```



### 3.编译测试套

```shell
cd ltp
make autotools
./configure
make
make install
```

- ltp默认编译到目标路径/opt/ltp下



### 4.执行测试

```shell
cd /opt/ltp
./runltp
```



### 5.结果查看

- 测试结果默认存放在ltp/results下
- 测试日志默认存放在ltp/output下



详细指导请阅读[官方文档](https://github.com/linux-test-project/ltp/blob/master/README.md)