# openEuler大版本包管理测试文档

* 文档编写日期: 2026/10/09

## 概要
包管理分为安装卸载测试和包升降级测试。要测试的包是本轮测试repo里的所有包或和上一轮repo对比的增量包列表，根据测试安排决定测试包列表。 得到要测试的包列表后， 安装卸载测试是安装这些包， 安装完成后重启， 然后卸载， 卸载完成后重启。 升降级测试的主要步骤是先用旧repo安装旧版本的包， 然后激活本轮测试repo, upgrade这些包，upgrade完成后执行downgrade, downgrade完成后执行remove包， 安装旧包， upgrade, downgrade, remove操作后都需要重启。remove包的时候需要排除系统默认安装的基础包。



## 测试包列表获取
1. 全量包列表获取
就是列出本轮测试repo里涉及的所有包。
#### 参考命令:
```shell
yum list --available | grep -E "$(uname -p)|noarch" | awk '{print $1}' | sed -E "s/\.($(uname -p)|noarch)$//" > install_list
# 检查一下安装包数量， 一般是2万多个
wc -l install_list
```

2. 增量包列表获取
增量包列表为和上一轮repo（或指定round版本）对比包版本发生变化的包， 包含升级、降级、新增的包， 一般此列表社区会有人负责提供， 新平台也将提供获取此列表功能。 


## 系统默认安装的基础包获取
**在测试前先获取默认系统安装的基础包，这些包基本上是系统运行必要的包，在删除操作的时候需要跳过**
 一般基础包的数量是500个左右
 #### 参考命令:
```shell
yum list --installed | awk '$NF == "@anaconda" {print $1}' | grep -E "$(uname -p)|noarch"  | sed -E "s/\.($(uname -p)|noarch)$//" > anaconda_list
# 检查一下基础包数量， 一般为500多
wc -l anaconda_list
```

---

## 安装卸载测试步骤
1. 安装
参考命令， 这几个包-x haoc-kernel* -x kernel-rt* -x raspberrypi* -x cloud-init* -x sysmaster -x devmaster -x install-scripts*需要先跳过， haoc-kernel kernel-rt, raspberrypi 这几个非常规内核不需要测， install-scripts 会影响破坏系统。 其它跳过的包大部分是会引起冲突的包， 后期单独测试。
**注意:跑这个命令时， 经常会???**
```
yum install -y $(cat install_list) --skip-broken -x haoc-kernel* -x kernel-rt* -x raspberrypi* -x cloud-init* -x sysmaster -x devmaster -x install-scripts* -x grubby* -x python3-dnf-plugin-local -x mariadb* -x greatsql* -x clutter-gst2* -x dtkwidget2* -x dtkcore2-devel -x containerd* -x redis-4* -x ncbi-blast* -x build -x moby-client  -x ukui-kwin-data -x ukui-window-switch -x redis-7* -x python3-poissonsearch* -x vk-kernel* -x mingw64-winpthreads -x mingw32-headers -x runc -x erlang-dialyzer -x globaltrustauthority-rbs-rbs -x kf6* -x kglobalacceld -x llvm-toolset-17* -x maven-local-openjdk17 -x maven-local-openjdk21 -x maven-local-openjdk8 -x minizip-ng -x minizip-ng-devel -x nlohmann_json-devel -x python3-django-pipeline -x python3-dnspython -x python3-mkdocstrings-python-legacy -x python3-pyqt5-sip -x python3-twisted -x qaccessibilityclient -x redis5 -x redis5-devel -x redis5-doc 2>&1 | tee rc6.install.$(date +"%m%d%H%M").log
```

**注意:跑全量安装命令时， 经常会失败， 一般是由于冲突的包导致的。这时需要把冲突的包跳过， 再次运行安装命令。错误如下**
```
Error: Transaction test error:
  file /usr/share/man/man1/clang++-17.1.gz conflicts between attempted installs of llvm-toolset-17-clang-17.0.6-14.oe2609.aarch64 and clang-17.0.6-67.oe2609.aarch64
  file /usr/share/man/man1/clang-17.1.gz conflicts between attempted installs of llvm-toolset-17-clang-17.0.6-14.oe2609.aarch64 and clang-17.0.6-67.oe2609.aarch64
  file /usr/bin/kwallet-query conflicts between attempted installs of kf6-kwallet-6.14.0-1.oe2609.aarch64 and kf5-kwallet-5.116.0-2.oe2609.aarch64

```

2. 卸载
参考命令
**注意：卸载的时候需要排除系统默认安装的基础包， 否则会导致系统无法启动, 例如kernel, grub, utsudo, systemd, grub2, efi-filesystem, NetworkManager, network-scripts, shim等， 卸载完重启前执行下dhclient命令取下ip地址， 有时候卸载完ip会丢掉， 导致重启后无法使用ssh连接**
```
yum remove -y $(cat install_list) --skip-broken --excludepkgs $(cat anaconda_list|tr '\n' ',') -x kernel -x grub* -x utsudo -x grubby-bls -x efi-filesystem -x NetworkManager -x network-scripts* -x shim* -x iptables* 2>&1 | tee rc6.remove.$(date +"%m%d%H%M").log;
```

---

## 升降级测试步骤
1. 旧包安装
旧包安装先disable掉新repo, 然后用旧repo安装包的旧版本。比如发布的2404sp7版本， 测2403sp6到2404sp7的升级，建2403sp6的机器， 然后用2403sp6的机器升级安装2404sp7的包。
参考命令
```
yum install -y $(cat install_list) --skip-broken -x haoc-kernel* -x kernel-rt* -x raspberrypi* -x cloud-init* -x sysmaster -x devmaster -x install-scripts* -x grubby* -x python3-dnf-plugin-local -x mariadb* -x greatsql* -x clutter-gst2* -x dtkwidget2* -x dtkcore2-devel -x containerd* -x redis-4* -x ncbi-blast* -x build -x moby-client  -x ukui-kwin-data -x ukui-window-switch -x redis-7* -x python3-poissonsearch* -x vk-kernel* -x mingw64-winpthreads -x mingw32-headers -x runc -x erlang-dialyzer -x globaltrustauthority-rbs-rbs -x kf6* -x kglobalacceld -x llvm-toolset-17* -x maven-local-openjdk17 -x maven-local-openjdk21 -x maven-local-openjdk8 -x minizip-ng -x minizip-ng-devel -x nlohmann_json-devel -x python3-django-pipeline -x python3-dnspython -x python3-mkdocstrings-python-legacy -x python3-pyqt5-sip -x python3-twisted -x qaccessibilityclient -x redis5 -x redis5-devel -x redis5-doc 2>&1 | tee rc6.install.$(date +"%m%d%H%M").log
```

2. 升级
**注意:升级是执行的install命令， 不是upgrade命令， 具体原因不详， 好像是执行upgrade容易出错难以实施**
参考命令
```
# 先配置上新repo，然后再进行升级安装
yum install -y $(cat install_list) --skip-broken -x python3-dns* -x python3-typer* -x perl-Test2* -x haoc-kernel* -x kernel-rt* -x raspberrypi* -x cloud-init* -x sysmaster -x devmaster -x install-scripts* -x grubby* -x grub2* -x python3-dnf-plugin-local -x gcc_secure -x selinux* -x kae-driver -x mariadb* -x greatsql* -x clutter-gst2* -x dtkwidget2* -x dtkcore2-devel -x containerd* -x redis-4* -x ncbi-blast* -x build -x moby-client -x llvm-toolset-17-mlir* -x llvm-toolset-18-mlir* -x llvm-toolset-19-mlir* -x llvm-toolset-17-python3-mlir -x llvm-toolset-18-python3-mlir -x llvm-toolset-19-python3-mlir  -x llvm-toolset-17-lldb* -x llvm-toolset-18-lldb* -x llvm-toolset-19-lldb* -x llvm-toolset-17-python3-lldb -x llvm-toolset-18-python3-lldb -x llvm-toolset-19-python3-lldb -x llvm-toolset-17-clang -x ukui-kwin-data -x ukui-window-switch -x redis-7* -x python3-poissonsearch* -x vk-kernel* -x mingw64-winpthreads -x mingw32-headers -x runc -x python3-commonmark -x groff-help -x procps-ng-i18n  -x mandoc 2>&1 | tee -a rc2.upgrade.04281100.log
```

3. 降级
参考命令
```
# repo不用动
yum downgrade -y $(cat install_list) --skip-broken -x python3-dns* -x python3-typer* -x perl-Test2* -x haoc-kernel* -x kernel-rt* -x raspberrypi* -x cloud-init* -x sysmaster -x devmaster -x install-scripts* -x grubby* -x grub2* -x python3-dnf-plugin-local -x gcc_secure -x selinux* -x kae-driver -x mariadb* -x greatsql* -x clutter-gst2* -x dtkwidget2* -x dtkcore2-devel -x containerd* -x redis-4* -x ncbi-blast* -x build -x moby-client -x llvm-toolset-17-mlir* -x llvm-toolset-18-mlir* -x llvm-toolset-19-mlir* -x llvm-toolset-17-python3-mlir -x llvm-toolset-18-python3-mlir -x llvm-toolset-19-python3-mlir  -x llvm-toolset-17-lldb* -x llvm-toolset-18-lldb* -x llvm-toolset-19-lldb* -x llvm-toolset-17-python3-lldb -x llvm-toolset-18-python3-lldb -x llvm-toolset-19-python3-lldb -x llvm-toolset-17-clang -x ukui-kwin-data -x ukui-window-switch -x redis-7* -x python3-poissonsearch* -x vk-kernel* -x mingw64-winpthreads -x mingw32-headers -x runc -x python3-commonmark -x groff-help -x procps-ng-i18n  -x mandoc 2>&1 | tee -a rc2.downgrade.04281100.log
```

4. 卸载
**注意：卸载的时候需要排除系统默认安装的基础包， 否则会导致系统无法启动, 例如kernel, grub, utsudo, systemd, grub2, efi-filesystem, NetworkManager, network-scripts, shim等， 卸载完重启前执行下dhclient命令取下ip地址， 有时候卸载完ip会丢掉， 导致重启后无法使用ssh连接**
参考命令
```
yum remove -y $(cat install_list) --skip-broken --excludepkgs $(cat anaconda_list|tr '\n' ',') -x kernel -x grub* -x utsudo -x systemd* -x grub2* -x efi-filesystem -x NetworkManager -x network-scripts* -x shim* 2>&1 | tee skip04.install.191640.log; dhclient
```


---


## 包分析
分析为对需要分析的包， 重新执行上述测试命令， 查看是否正常。如何确定为异常，就提交到issue。issue参考过去版本测试已有issue. 
分析的包包含三部分：
1. 安装命令里排除的包
安装日志开头filtered out的包， 对于异常kernel包， install-scripts这类包不需要测试。
获取参考命令：
```
grep 'All matches were filtered out by exclude filtering for argument'  rc5.install.log | awk '{print $NF}'
```
2. 安装中skipped的包
安装日志末尾skipped的包
获取参考命令：
```
cat rc4.install.log | grep -n 'Skipped:' | awk -F ':' '{print $1}' | xargs -i tail -n +{} rc4.install.log
```
3. 每轮日志里异常的包
各执行过程中有异常信息的包
获取参考命令：
```
grep -C5 -iE "fatal|error|warning|fail|problem|Invalid|no such|致命|错误|问题|警告|失败|无效|warn|需要|无法获取" XXX_log
```



---
---

* 注意，安装前先查一下有没有其它非常规kernel包， 如vk-kernel, kernel-rt， raspberrypi-kernel等， 避免安装后系统无法启动。
* 注意，安装的时候常发生依赖冲突， 例如java8, java17， redis5, redis6等， 需要手动解决依赖冲突。
* 注意，repo的网速会影响安装包进度， 尽量用局域网内的repo测试
* 注意，测试的install, upgrade, downgrade, remove完， reboot前， 把日志备份下来，方便机器无法启动后分析原因
* 注意，upgrade执行的是install命令， 不是upgrade命令， 具体原因不详， 好像是执行upgrade容易出错难以实施
* 注意，可能upgrade, downgrade阶段也会发生依赖冲突， 需要手动解决依赖冲突。
* 注意，删除包的时候， 可能会遇到下列错误， 需要通过rpm -e命令手动删除, 不需要的grub2-efi等包
```
Error: 
 Problem: The operation would result in removing the following protected packages: grub2-efi-x64
-(try to add '--skip-broken' to skip uninstallable packages or '--nobest' to use not only best candidate packages)
```
