# compile_mock

### 1. 介绍
rpm自编译工具


### 2. 环境准备
##### 1. 安装标准镜像，使用everything和source的源，一般使用本地挂载。
    1）上传everything、source镜像到指定机器，并进行挂载。（注意区分everything镜像架构，source镜像不分架构）
        mount openEuler-22.03-everything-x86_64-dvd.iso everything/
        mount openEuler-22.03-source-dvd.iso source/
    2）配置everything、source的源：
    [everything]
    name=everything
    baseurl=file:///home/everything
    enabled=1
    gpgcheck=0

    [source]
    name=source
    baseurl=file:///home/source
    enabled=1
    gpgcheck=0
    
##### 2. 将自编译的工具compile-mock拷贝到物理机上。


### 3. 使用说明
**kernel、gcc、glibc必跑**

##### 1. 获取所有的源码包列表source_list.bak
    cd /opt/compile_mock/common/
    dnf --repo=source --available list | awk '{print $1}'| awk -F. 'OFS="."{$NF="";print}'| awk '{print substr($0, 1, length($0)-1)}' >source_list.bak

##### 2. 随机选取500个源码包，并给文件添加执行权限
    shuf -n500 source_list.bak >source_list
    chmod +x source_list*

##### 3. 加上kernel、gcc、glibc这3个必测包：
    sed -i "1i kernel\ngcc\nglibc" source_list

##### 4. 将everything源添加到 /opt/compile_mock/common/openEuler-x86_64.cfg 或者 /opt/compile_mock/common/openEuler-aarch64.cfg 文件末尾，编译哪个架构就修改哪个架构对应的文件。
    # repos
    [everything]
    name=everything
    baseurl=file:///home/everything
    enabled=1
    gpgcheck=0

##### 5. 进入/opt/compile_mock/total_pkg/目录，运行工具进行自编译。
    1）所有包一起自编译：bash total_pkg.sh all （all是指所有的包）
    2）单个包自编译：bash total_pkg.sh hppc  (hppc是包名,选自source_list文件)


### 4. 结果查看
- 编译失败的软件包保存在/opt/compile_mock/total_pkg/fail_pkg.log文件中


### 5. FAQ
- 如果有大量的软件包编译失败，把失败的软件包二次编译即可。
- 如果失败的包不多，也可以选择手动编译：
    1、将acl源码包下载到执行机上进行编译

        yumdownloader --source bval
    2、安装bval

        rpm -i bval-1.1.1-1.oe1.src.rpm
    3、进入安装目录

        cd /root/rpmbuild/SPECS/
    4、开始编译

        dnf install rpm-build -y
        rpmbuild -ba bval.spec
    5、如果有依赖的就安装依赖
    6、查看编译过程中是否有错误
